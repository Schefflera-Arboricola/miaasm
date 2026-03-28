import os
import yaml
import shutil

CONTENT = "content"
BUILD = "_build"
SCALE = 2.0
BG_COLOR = "#e8d9b7"

if os.path.exists(BUILD):
    os.system(f"rm -rf {BUILD}")  # a bit unsafe

os.makedirs(BUILD, exist_ok=True)

index_sections = []

files = os.listdir(CONTENT)
files = sorted(files, key=lambda x: x.lower())

for file in files:
    if not (file.endswith(".yaml") or file.endswith(".yml")):
        continue

    with open(os.path.join(CONTENT, file), "r") as f:
        items = yaml.safe_load(f)

    section = f"<h2>{file[:-5].title()}</h2><ul>"
    folder = os.path.join(BUILD, file[:-5])
    os.makedirs(folder, exist_ok=True)

    if items:
        for item in items:
            name = item["name"]
            iframe = item.get("iframe", "").strip()
            desc = item.get("description", "").strip()

            safe_name = name.lower().replace(" ", "-")
            path = os.path.join(folder, f"{safe_name}.html")
            with open(path, "w") as f:
                submit_button_text = (
                    "Save Description" if not desc else "Update Description"
                )
                s = f"""<!DOCTYPE html>
<html>
<head><title>{name}</title>
</head>
<body style='background-color:{BG_COLOR};'>
<a href="../index.html">Back to Home</a>
<h1>{name}</h1> 
<hr> 
<div align='center'>
{iframe.replace('width="560" height="315"', f'width="{560 * SCALE}" height="{315 * SCALE}"')}
<hr>
    <div id="desc_display">
        <h2>Description:</h2>
        <p>{desc or "No description yet."}</p>
    </div>
    <br>
    <form method="post" action="../cgi-bin/edit_desc.py">
    <input type="hidden" name="yaml_file" value="{file}">
    <input type="hidden" name="name" value="{name}">
    <input type="hidden" name="safe_name" value="{safe_name}">
    <textarea name="description" rows="5" cols="100"></textarea>
    <br><br>
    <input type="submit" value="{submit_button_text}" style="box-sizing: border-box; padding: 10px; line-height: 1.2;" />  
    </form>
</div>
<hr>
</body></html>"""

                f.write(s)
            section += f'<li><a href="{file[:-5]}/{safe_name}.html">{name}</a></li>'

    index_sections.append(section + "</ul><hr>")

with open(os.path.join(BUILD, "index.html"), "w") as f:
    f.write(
        f"""<!DOCTYPE html>
<html><head><title>Index</title>
</head><body style='background-color:{BG_COLOR};'>
<h1>All Content</h1><hr>
{"".join(index_sections)}
</body></html>"""
    )

# Copy cgi-bin to _build
if os.path.exists("cgi-bin"):
    shutil.copytree("cgi-bin", "_build/cgi-bin", dirs_exist_ok=True)

print("Done: website at _build/index.html")
