# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: tdd
#     language: python
#     name: python3
# ---

# %%
import os
import json
from dtypes import FSItem, FSItemType, PreGenTreeHolder, ReportTagGenerator, TagCreatorFunction
FileExtAccumulator = dict[str, int]


meta_vol2_json = "NAS_Vol2_meta.json"
report_vol2 = "with_html/NAS_report_Vol2.html" 

meta_vol1_json = "NAS_Vol1_meta.json"
report_vol1 = "with_html/NAS_report_Vol1.html" 

meta_vol1: FSItem = json.load(open(meta_vol1_json, "r"))
meta_vol2: FSItem = json.load(open(meta_vol2_json, "r"))

# %%
from bs4 import BeautifulSoup, Tag, NavigableString

SUMMARY_BASE_REPORT = "with_html/min_base.html"

with open(SUMMARY_BASE_REPORT) as base_file:
    base_report_soup = BeautifulSoup(base_file)

base_report_body = base_report_soup.body
base_report_logo = base_report_body.find("div", class_="title")


# %% [markdown]
# - Tomar los elementos importantes

# %%
def clear_root(soup_body: Tag):
    soup_body.find(class_="tree-nav").clear()

root_title_wrapper = base_report_body.find(id="root-title-wrapper")
root_title_wrapper

# %%
rtg = ReportTagGenerator(SUMMARY_BASE_REPORT)

    
def add_to_directory_items(parent_soup: Tag, creator: TagCreatorFunction, *args):
    current_dir_items = parent_soup.find(class_="directory-items")
    item_soup = creator(*args)
#         print(current_dir_items, fsoup)
    if not current_dir_items:
        new_directory_items = rtg.directory_items()
        new_directory_items.append(item_soup)
        parent_soup.append(new_directory_items)
        return new_directory_items
    else:
        current_dir_items.append(item_soup)
        return current_dir_items
    

def consice_populate_html(parent_soup: Tag, parent_stats: FSItem):
    f_children: list[Tag | NavigableString] = []
    print("Parent:", parent_soup.span.string)
    print(parent_stats["name"], parent_stats["type"], [t["name"] for t in parent_stats["children"]])

    for children_stats in parent_stats["children"]:
        if children_stats["type"] == "directory":
            directory = rtg.create_dir(children_stats["name"], children_stats["size_str"], children_stats.get("description", None))
            children = consice_populate_html(directory, children_stats)
            for child in children:
                directory.append(child)
            f_children.append(directory)
        else:
            continue
    # Checking some edge cases

    # Add file qty
    if parent_stats["file_qty"] > 0:
        f_children.append(add_to_directory_items(parent_soup, rtg.create_item_qty, parent_stats["file_qty"], "file", parent_stats["per_fextension_qty"]))

    for child in f_children:
        parent_soup.append(child)
    # print(first_expandable_dir.prettify())

    return f_children


# %%
# do root things
# NAS Vol1
clear_root(base_report_body)
vol1_root_dir = rtg.create_dir(meta_vol1["name"], meta_vol1["size_str"], meta_vol1.get("description", None))
main_container = base_report_body.nav
print(main_container.prettify())
main_container.append(vol1_root_dir)
first_expandable_dir = main_container.details

consice_populate_html(first_expandable_dir, meta_vol1)

with open(report_vol1, "w") as file:
    file.write(str(base_report_soup))


# NAS Vol2
clear_root(base_report_body)
vol2_root_dir = rtg.create_dir(meta_vol2["name"], meta_vol2["size_str"], meta_vol2.get("description", None))
main_container = base_report_body.nav
main_container.append(vol2_root_dir)
first_expandable_dir = main_container.details

consice_populate_html(first_expandable_dir, meta_vol2)

with open(report_vol2, "w") as file:
    file.write(str(base_report_soup))


# %%
def clear_body(soup_body: Tag):
    soup_body.clear()

clear_body(base_report_body)
base_report_soup.body.append(base_report_logo)
for html_report in [report_vol1, report_vol2]:
    with open(html_report) as file:
        html_report_soup = BeautifulSoup(file)

    html_report_part = html_report_soup.body.nav
    base_report_soup.body.append(html_report_part)

base_report_soup.body.append(rtg.separator())

with open("reports/Reporte_NAS.html", "w") as file:
    file.write(str(base_report_soup))
