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
  FOREIGN KEY (make_name) REFERENCES make(name) ON DELETE CASCADE
);
CREATE TABLE model_image (
  path varchar(255),
  model_id varchar(255),
  FOREIGN KEY (model_id) REFERENCES model(id) ON DELETE CASCADE
);
CREATE TABLE variant (
  id varchar(255) PRIMARY KEY,
  name varchar(255),
  model_id varchar(255),
  FOREIGN KEY (model_id) REFERENCES model(id) ON DELETE CASCADE
);
CREATE TABLE tag_category (title varchar(255) PRIMARY KEY);
CREATE TABLE tag (
  title varchar(255) PRIMARY KEY,
  tag_category_title varchar(255),
  FOREIGN KEY (tag_category_title) REFERENCES tag_category(title) ON DELETE CASCADE
);
CREATE TABLE variant_tag (
  variant_id varchar(255),
  tag_title varchar(255),
  value text,
  FOREIGN KEY (tag_title) REFERENCES tag(title) ON DELETE CASCADE
);
delimiter // CREATE FUNCTION `get_tag_value_from_title` (variant_id varchar(255), tag_title varchar(255)) RETURNS varchar(255) reads sql data BEGIN
declare tag_value varchar(255);
select vt.value into tag_value
from variant_tag vt
where vt.variant_id = variant_id
  and vt.tag_title = tag_title;
RETURN tag_value;
END // delimiter;