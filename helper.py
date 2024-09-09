
from uuid import uuid4
from tabulate import tabulate
import colorama as cm

FORE_COLORS = {
    'i': cm.Fore.WHITE,
    'a': cm.Fore.LIGHTCYAN_EX,
    'a2': cm.Fore.MAGENTA,
    'w': cm.Fore.YELLOW,
    'e': cm.Fore.RED,
    's': cm.Fore.GREEN,
    'd': cm.Fore.WHITE,
    'r': cm.Fore.RESET,
}


def printt(data):
    print(tabulate(data, tablefmt='fancy_grid', headers='keys'))


def join(l, sep=''):
    str = ''
    for i in l:
        str += f'{i}{sep}'
    return str if sep == '' else str[:-1]


def colored_str(values: str, type='d', data=None):
    prt = ''
    if not data:
        prt = FORE_COLORS[type] + values + FORE_COLORS['r']
    else:
        out = values.split('{}')
        for i in out:
            prt += FORE_COLORS[type] + i + FORE_COLORS['r']
            if len(data) > 0:
                val = data.pop(0)
                prt += FORE_COLORS[val[0]] + val[1] + FORE_COLORS['r']
    return prt


def printc(values: str, type='d', data=None, end='\n'):
    print(colored_str(values, type=type, data=data), end=end)


def generate_unique_id():
    return str(uuid4())
