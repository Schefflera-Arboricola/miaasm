import os
import re
import yaml
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)


@app.context_processor
def inject_globals():
    return {"BG_COLOR": BG_COLOR, "SCALE": SCALE}

CONTENT = os.path.join(os.path.dirname(__file__), "content")
SCALE = 2.0
BG_COLOR = "#e8d9b7"


def load_sections():
    sections = []
    files = sorted(os.listdir(CONTENT), key=lambda x: x.lower())
    for file in files:
        if not (file.endswith(".yaml") or file.endswith(".yml")):
            continue
        with open(os.path.join(CONTENT, file), "r") as f:
            items = yaml.safe_load(f) or []
        section_name = file[:-5].title()
        section_slug = file[:-5]
        enriched = []
        for item in items:
            safe_name = item["name"].lower().replace(" ", "-")
            enriched.append({
                "name": item["name"],
                "safe_name": safe_name,
                "section": section_slug,
                "yaml_file": file,
            })
        sections.append((section_name, enriched))
    return sections


def find_item(section_slug, safe_name):
    for file in os.listdir(CONTENT):
        if not (file.endswith(".yaml") or file.endswith(".yml")):
            continue
        if file[:-5] != section_slug:
            continue
        with open(os.path.join(CONTENT, file), "r") as f:
            items = yaml.safe_load(f) or []
        for item in items:
            if item["name"].lower().replace(" ", "-") == safe_name:
                iframe = item.get("iframe", "").strip()
                iframe = iframe.replace(
                    'width="560" height="315"',
                    f'width="{int(560 * SCALE)}" height="{int(315 * SCALE)}"',
                )
                return {
                    "name": item["name"],
                    "safe_name": safe_name,
                    "section": section_slug,
                    "yaml_file": file,
                    "iframe": iframe,
                    "desc": item.get("description", "").strip(),
                }
    return None


@app.route("/")
def index():
    sections = load_sections()
    return render_template("index.html", sections=sections)


@app.route("/<section>/<safe_name>")
def item(section, safe_name):
    data = find_item(section, safe_name)
    if data is None:
        return "Not found", 404
    return render_template("item.html", **data)


@app.route("/edit_desc", methods=["POST"])
def edit_desc():
    yaml_file = request.form["yaml_file"]
    name = request.form["name"]
    safe_name = request.form["safe_name"]
    section = request.form["section"]
    new_desc = request.form["description"].strip()

    # Validate yaml_file is a bare filename with no path components
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.ya?ml", yaml_file):
        abort(400, "Invalid yaml_file parameter")

    content_path = os.path.join(CONTENT, yaml_file)
    if not os.path.isfile(content_path):
        abort(404, "Content file not found")

    with open(content_path, "r") as f:
        items = yaml.safe_load(f) or []

    matched = False
    for item in items:
        if item["name"] == name:
            item["description"] = new_desc
            matched = True
            break

    if not matched:
        abort(404, "Item not found")

    with open(content_path, "w") as f:
        yaml.safe_dump(items, f, default_flow_style=False, allow_unicode=True)

    return redirect(url_for("item", section=section, safe_name=safe_name))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
