#!/usr/bin/env python3

import cgi # todo: switch to flask or something -- cgi is deprecating
import yaml
import os
from bs4 import BeautifulSoup

form = cgi.FieldStorage()

yaml_file = str(form["yaml_file"].value)
name = str(form["name"].value)
safe_name = str(form["safe_name"].value)
new_desc = str(form["description"].value).strip()

script_dir = os.path.dirname(__file__)
content_path = os.path.join(script_dir, "..", "..", "content", yaml_file)

with open(content_path, "r") as f:
    items = yaml.safe_load(f)

for item in items:
    if item["name"] == name:
        item["description"] = new_desc
        break

with open(content_path, "w") as f:
    yaml.safe_dump(items, f, default_flow_style=False, allow_unicode=True)

build_path = os.path.join(script_dir, "..", yaml_file[:-5], f"{safe_name}.html")

with open(build_path, "r") as f:
    soup = BeautifulSoup(f, "html.parser")

# Find the h2 tag with text 'Description:' and get the next <p> tag
h2_tag = soup.find("h2", string="Description:")
p_tag = h2_tag.find_next("p") if h2_tag else None

# Add line breaks to the content if the <p> tag exists
if p_tag:
    p_tag.clear()
    p_tag.append(BeautifulSoup(new_desc, "html.parser"))
    """
    # todo: for now using <br> for new line
    p_tag.clear()  # Remove existing content
    lines = new_desc.split('\n')
    for i, line in enumerate(lines):
        if i > 0:
            p_tag.append(soup.new_tag('br'))
        p_tag.append(line)   
    """

# Find the submit button and update its value
submit_button = soup.find("input", {"type": "submit"})
if submit_button and submit_button.get("value") == "Save Description":
    submit_button["value"] = "Update Description"

# Write the modified HTML back to the file
with open(build_path, "w") as f:
    f.write(str(soup))

page = "../" + yaml_file[:-5] + "/" + safe_name + ".html"

print("Content-type: text/html")
print()
print(
    f'<html><head><meta http-equiv="refresh" content="0;url={page}"></head><body>Updating...</body></html>'
)
