CREATE DATABASE budget_wheels;
USE budget_wheels;
CREATE TABLE make (
  name varchar(255) PRIMARY KEY,
  img_path varchar(255)
);
CREATE TABLE model (
  id varchar(255) PRIMARY KEY,
  name varchar(255),
  make_name varchar(255),
  FOREIGN KEY (make_name) REFERENCES make(name)
);
CREATE TABLE model_image (
  path varchar(255),
  model_id varchar(255),
  FOREIGN KEY (model_id) REFERENCES model(id)
);
CREATE TABLE variant (
  id varchar(255) PRIMARY KEY,
  name varchar(255),
  model_id varchar(255),
  FOREIGN KEY (model_id) REFERENCES model(id)
);
CREATE TABLE tag_category (title varchar(255) PRIMARY KEY);
CREATE TABLE tag (
  title varchar(255) PRIMARY KEY,
  tag_category_title varchar(255),
  FOREIGN KEY (tag_category_title) REFERENCES tag_category(title)
);
CREATE TABLE vehicle_tag (
  variant_id varchar(255),
  tag_title varchar(255),
  value text,
  FOREIGN KEY (tag_title) REFERENCES tag(title)
);