import time
import mysql.connector
import csv
import colorama as cm
import selenium
from helper import *
import dotenv
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import random as rand
cm.init(convert=True)

CONFIG = dotenv.dotenv_values()
TAG_CATEGORIES = {
    "Engine & Transmission": ["Drivetrain", "Fuel Type", "City Mileage", "Highway Mileage", "ARAI Certified Mileage", "ARAI Certified Mileage for CNG", "Gears", "Power", "Torque", "Turbocharger", "Battery", "Electric Range", "Distance to Empty", "Electric Range"],
    "Dimensions & Weight": ["Height", "Length", "Width", "Wheelbase", "Body Type", "Ground Clearance", "Minimum Turning Radius"],
    "Capacity": ["Doors", "Seating Capacity", "Fuel Tank Capacity", "Boot Space"],
    "Suspensions, Brakes, Steering & Tyres": ["Front Brakes", "Rear Brakes", "Front Suspension", "Rear Suspension", "Front Tyre & Rim", "Rear Tyre & Rim", "Wheels Size", "Power Steering"],
    "Safety": ["Airbags", "ISOFIX (Child-Seat Mount)", "Number of Airbags", "ESP (Electronic Stability Program)", "ASR / Traction Control", "Hill Assist", "ADAS"],
    "Braking & Traction": ["ABS (Anti-lock Braking System)", "EBD (Electronic Brake-force Distribution)", "EBA (Electronic Brake Assist)"],
    "Locks & Security": ["Keyless Entry"],
    "Comfort & Convenience": ["Third Row AC Vents", "Ventilation System", "Second Row AC Vents",  "Start / Stop Button", "12v Power Outlet", "Boot-lid Opener", "Fuel-lid Opener", "Sun Visor", "Gear Indicator", "Drive Modes", "Lane Watch Camera/ Side Mirror Camera", "Walk Away Auto Car Lock", "Headlight Reminder", "Gear Shift Reminder", "Adjustable Steering Column", "Parking Assistance", "Tyre Pressure Monitoring System", "Rain Sensing Wipers", "Paddle Shifters", "Cruise Control", "Heads-Up Display", "Automatic Headlamps"],
    "Seats & Upholstery": ["Power Seats", "Seat Height Adjustment", "Rear Center Armrest", "Heated Seats", "Leather Wrapped Steering", "Seats Material"],
    "Storage": ["Cooled Glove Box", "Door Pockets", "Adjustable Headrests"],
    "Doors, Windows, Mirrors & Wipers": ["Power Windows", "Auto-Dimming Rear-View Mirror"],
    "Exterior": ["Colors", "Sunroof", "Wheel Material"],
    "Lighting": ["Ambient Lightning", "Cargo/Boot Lights", "Headlights"],
    "Instrumentation": ["Odometer", "Speedometer", "Tachometer", "Tripmeter", "Instrument Console"],
    "Entertainment, Information & Communication": ["Audiosystem", "Aux-in Compatibility", "Bluetooth", "CD / MP3 / DVD Player", "Voice Recognition", "Android Auto", "Infotainment Screen", "Navigation System", "Speakers"],
    "Manufacturer Warranty": ["Basic Warranty", "Extended Warranty"],
}
HEADERS = "CNO,Make,Model,Variant,Ex-Showroom Price,Drivetrain,Fuel Tank Capacity,Fuel Type,Height,Length,Width,Body Type,Doors,City Mileage,Highway Mileage,ARAI Certified Mileage,ARAI Certified Mileage for CNG,Gears,Ground Clearance,Front Brakes,Rear Brakes,Front Suspension,Rear Suspension,Front Tyre & Rim,Rear Tyre & Rim,Power Steering,Power Windows,Power Seats,Keyless Entry,Power,Torque,Odometer,Speedometer,Tachometer,Tripmeter,Seating Capacity,Seats Material,Type,Wheelbase,Wheels Size,Start / Stop Button,12v Power Outlet,Audiosystem,Aux-in Compatibility,Basic Warranty,Bluetooth,Boot-lid Opener,Boot Space,CD / MP3 / DVD Player,Distance to Empty,Door Pockets,Extended Warranty,Fuel-lid Opener,Instrument Console,Minimum Turning Radius,Sun Visor,Third Row AC Vents,Ventilation System,Auto-Dimming Rear-View Mirror,Hill Assist,Gear Indicator,Ambient Lightning,Cargo/Boot Lights,Drive Modes,Lane Watch Camera/ Side Mirror Camera,Voice Recognition,Walk Away Auto Car Lock,ABS (Anti-lock Braking System),Headlight Reminder,Adjustable Headrests,Airbags,EBD (Electronic Brake-force Distribution),Gear Shift Reminder,Number of Airbags,Adjustable Steering Column,Misc,Other specs,Parking Assistance,Android Auto,Cigarette Lighter,Infotainment Screen,EBA (Electronic Brake Assist),Seat Height Adjustment,Navigation System,Second Row AC Vents,Tyre Pressure Monitoring System,Rear Center Armrest,ESP (Electronic Stability Program),Cooled Glove Box,Heated Seats,Turbocharger,Rain Sensing Wipers,Paddle Shifters,Leather Wrapped Steering,Automatic Headlamps,ASR / Traction Control,Cruise Control,Battery,Electric Range,ISOFIX Child Seat Anchor,ADAS,Wheel Material,Year,Speakers,Colors,Sunroof,Headlights".split(
    ',')


mysqlcnn = mysql.connector.connect(
    user=CONFIG['MYSQL_USER'], password=CONFIG['MYSQL_PASSWORD'])


def csv_write_filtered_data():
    with open(CONFIG['RAW_DATA_FILE_PATH'], mode='r', newline='') as data_file, open(CONFIG['FILTERED_DATA_FILE_PATH'], mode='w', newline='') as filtered_data_file:
        csv_writer = csv.writer(filtered_data_file)
        data = []

        def get_random_year():
            return rand.choice(['2019', '2020', '2021', '2022', '2023'])

        def get_random_speakers():
            return rand.randint(4, 8)

        def get_random_colors():
            return rand.choices(['beige', 'blue', 'yellow', 'sunset orange', 'graphite', 'red', 'forest green', 'white', 'silver', 'magma grey', 'midnight blue', 'dual-tone red on black', 'dual-tone red on white', 'dual-tone blue on black', 'dual-tone blue on white', 'dual-tone white on black', 'Lava Blue', 'Cherry Red', 'Seaweed Green'], k=rand.randint(3, 8))
        man_year = get_random_year()
        speakers = get_random_speakers()
        prev_model = None
        for row in csv.reader(data_file):
            if int(row[4]) > 2500000:
                continue
            child_seat_anchor = 'Yes' if int(row[4]) > 800000 else 'No'
            adas = 'Yes' if row[2].lower() in (
                'seltos', 'creta', 'xuv500', 'hector') and int(row[4]) > 1800000 else 'No'
            wheel_material = 'Alloy' if int(row[4]) > 1000000 else 'Steel'
            adas = 'Yes' if row[2].lower() in (
                'seltos', 'creta', 'xuv500', 'hector') else 'No'
            sunroof = 'Yes' if int(row[4]) > 1500000 else 'No'
            headlights = 'LED' if int(row[4]) > 1500000 else 'Xenon' if int(
                row[4]) > 1200000 else 'Halogen'
            if prev_model != row[2]:
                man_year = get_random_year()
                speakers = get_random_speakers()
                colors = ', '.join(get_random_colors())
                prev_model = row[2]
            row += [child_seat_anchor, adas,
                    wheel_material, man_year, str(speakers), colors, sunroof, headlights]
            data.append(row)
            csv_writer.writerow(row)
    return data


def get_model_img_paths_webed():
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome()
    time.sleep(5)
    data = []
    with open('./vehicle_model_img_paths.csv', newline='') as img_path_file, open('./vehicle_model_img_paths_out.csv', newline='', mode='w') as out_file:
        writer = csv.writer(out_file)
        for row in csv.reader(img_path_file):
            if row[1] != '':
                data.append(row)
                continue
            print(row[0], ':')
            driver.get('https://www.carwale.com')
            inp = driver.find_element(
                By.XPATH, "//*[@placeholder='Type to select car name, e.g. Jeep Meridian']")
            print(inp)
            inp.send_keys(row[0])
            time.sleep(1)
            inp.send_keys(Keys.ENTER)
            time.sleep(3)
            row[1] = input('>>>')
            writer.writerow(row)
    return data[1:]


def get_model_img_paths():
    data = []
    with open('./vehicle_model_img_paths_out.csv', newline='') as csv_file:
        for row in csv.reader(csv_file):
            data.append(row)
    return data[1:]


def csv_load_data():
    with open(CONFIG['FILTERED_DATA_FILE_PATH'], mode='r', newline='') as data_file:
        data = []
        for row in csv.reader(data_file):
            data.append(row)
    return data


def db_insert_row(table, data, should_commit=False, should_log=True):
    try:
        keys = join(list(data.keys()), ',')
        values = str(tuple(data.values()))
        values = values if ',)' not in values else values[:-2] + ')'
        mscur.execute('insert into {}({}) values {}'.format(
            table, keys, values).replace('None', 'null'))
        if should_commit:
            mysqlcnn.commit()
        if should_log:
            printc('INSERTED {} INTO {}', type='d',
                   data=[['a2', values], ['a', table]])
        return True
    except mysql.connector.Error as err:
        printc(f'ERROR: {err.msg}', type='e')
        return False


def db_show_dbs():
    mscur.execute('show databases')
    print(mscur.fetchall())


def db_exists():
    try:
        mscur.execute('show databases')
        dbs = mscur.fetchall()
        if CONFIG['DB_NAME'] in [i['Database'] for i in dbs]:
            mscur.execute(f'use {CONFIG["DB_NAME"]}')
            return True
        else:
            return False
    except mysql.connector.Error as err:
        printc(f'ERROR:db_exists: {err.msg}', type='e')
        return None


def db_init(force=False):
    is_db_exists = db_exists()
    if is_db_exists == None:
        return False
    if not is_db_exists or force:
        try:
            mscur.execute(f'drop database if exists {CONFIG['DB_NAME']}')
            mysqlcnn.commit()
        except mysql.connector.Error as err:
            printc(f'ERROR:db_init>dropdb: {err.msg}', type='e')
            return False

        with open(CONFIG['DB_INIT_FILE_PATH'], "r") as db_file:
            script = db_file.read()
            printc('Running SQL Script...')
            for i in script.split(';'):
                try:
                    if i.strip() != '':
                        mscur.execute(i)
                        printc(i)
                except mysql.connector.Error as err:
                    printc(f'ERROR:db_init>sqlexec: {err.msg}', type='e')
                    return False
            printc('Succesfully ran init script.\n', type='s')
    return True


def db_migrate_init_data():
    raw_data = csv_write_filtered_data()

    printc('Inserting Makes...')
    makes = {i[1] for i in raw_data}
    for i in makes:
        if not db_insert_row('make', {'name': i}, should_log=False):
            return False
        printc("Inserted {} into {}", data=[
            ['a2', i], ['a', 'make']])
    mysqlcnn.commit()
    printc('Succesfully inserted Makes.\n', type='s')

    printc('Inserting Models...')
    models = {(i[1], i[2]) for i in raw_data}
    model_img_paths = get_model_img_paths()
    db_models = []
    for i in models:
        db_model = {'id': generate_unique_id(
        ), 'name': i[1], 'make_name': i[0]}
        if not db_insert_row('model', db_model, should_log=False):
            return False
        img_paths = [ip for ip in model_img_paths if ip[0].lower() ==
                     db_model['name'].lower()]
        if len(img_paths) > 0:
            db_model_image = {
                'model_id': db_model['id'], 'path': img_paths[0][1]}
            if not db_insert_row('model_image', db_model_image, should_log=False):
                return False
        printc("Inserted {} {} into {}", data=[
            ['a2', i[0]], ['a2', i[1]], ['a', 'model']])
        db_models.append(db_model)
    mysqlcnn.commit()
    printc('Succesfully inserted Models.\n', type='s')

    printc('Inserting Tag Categories...')
    db_tag_categories = []
    for i in TAG_CATEGORIES:
        db_tag_category = {
            'title': i}
        if not db_insert_row('tag_category', db_tag_category, should_log=False):
            return False
        printc("Inserted {} into {}", data=[
            ['a2', i], ['a', 'tag_category']])
        db_tag_categories.append(db_tag_category)
    mysqlcnn.commit()
    printc('Succesfully inserted Tag Categories.\n', type='s')

    printc('Inserting Tags...')
    db_tags = []
    for i in HEADERS[4:]:
        tag_category_titles = [
            j for j in TAG_CATEGORIES if i in TAG_CATEGORIES[j]]
        db_tag = {
            'title': i}
        if len(tag_category_titles) > 0:
            db_tag['tag_category_title'] = tag_category_titles[0]
        if not db_insert_row('tag', db_tag, should_log=False):
            return False
        printc("Inserted {} into {}", data=[
            ['a2', i], ['a', 'tag']])
        db_tags.append(db_tag)
    mysqlcnn.commit()
    printc('Succesfully inserted Tags.\n', type='s')

    printc('Inserting Variants...')
    variants = [[i[1], i[2], i[3],
                 {HEADERS[j]: i[j] for j in range(4, len(HEADERS))}
                 ] for i in raw_data]
    for i in variants:
        db_variant = {'id': generate_unique_id(),
                      'name': i[2], 'model_id': [m for m in db_models if m['make_name'] == i[0] and m['name'] == i[1]][0]['id']}
        if not db_insert_row('variant', db_variant, should_log=False):
            return False
        printc("Inserted {} {} {} into {}", data=[
            ['a2', i[0]], ['a2', i[1]], ['a2', i[2]], ['a', 'variant']])
        for j in range(len(db_tags)):
            if not db_insert_row('variant_tag', {
                'tag_title': db_tags[j]['title'],
                'variant_id': db_variant['id'],
                'value': None if i[3][db_tags[j]['title']] == '' else i[3][db_tags[j]['title']]
            }, should_log=False):
                return False
    mysqlcnn.commit()
    printc('Succesfully inserted Variants.\n', type='s')

    printc('Adding Make Images...')
    url = "https://www.carwale.com"

    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    imgs_div = soup.find_all("ul", "o-XylGE o-chzWeu o-cpnuEd")
    imgs = imgs_div[0].find_all(
        "img", "o-bXKmQE o-cgkaRG o-cQfblS o-bNxxEB o-pGqQl o-wBtSi o-bwUciP o-btTZkL o-bfyaNx o-eAZqQI")

    mscur.execute('''
        select name from make
    ''')
    makes = [i['name'] for i in mscur.fetchall()]

    makes_w_img = []
    for i in imgs:
        title = i['alt'][:-5]
        if title not in makes:
            continue
        makes_w_img.append(title)
        mscur.execute(
            'update make set img_path = %s where name = %s', (i['src'], title))
        printc("Updated {} in {}", data=[
            ['a2', title], ['a', 'make']])
    printc('Succesfully updated Make Images.\n', type='s')

    printc('Removing Makes without Images with CASCADE...')
    for i in makes:
        if i in makes_w_img:
            continue
        mscur.execute(
            'delete from make where name = %s', (i,))
        printc("Deleting {} from {}", data=[
            ['a2', i], ['a', 'make']])
    printc('Succesfully deleted Makes.\n', type='s')
    mysqlcnn.commit()
    return True


mscur = mysqlcnn.cursor(dictionary=True)

should_migrate_db = True
try:
    if not db_init(should_migrate_db):
        exit(1)
    if should_migrate_db:
        print('here')
        db_migrate_init_data()
except Exception as ex:
    print(ex)
mscur.execute('desc variant_tag')
printt(
    mscur.fetchall())

mscur.close()
mysqlcnn.close()

cm.deinit()
