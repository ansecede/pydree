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
from dtypes import FSItem, FSItemType, PreGenTreeHolder
FileExtAccumulator = dict[str, int]

meta_vol1_json = "metainfo.json"
report_vol1 = "with_html/finished_report.html" 

meta_vol1: FSItem = json.load(open(meta_vol1_json, "r"))

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
import pathlib
from typing import Callable, Literal

TagCreatorFunction = Callable[[int, FSItemType, FileExtAccumulator], Tag] | Callable[[str], Tag] | Callable[[], Tag]

class ReportTagGenerator:
    soup: BeautifulSoup

    def __init__(self, fpath: str | pathlib.Path) -> None:
        with open(fpath, "r") as base_file:
            self.soup = BeautifulSoup(base_file)

    def separator(self) -> Tag:
        separator_soup = self.soup.new_tag("div", attrs={"class":"title"})
        return separator_soup

    def directory_items(self) -> Tag:
        directory_items_soup = self.soup.new_tag("div", attrs={"class":"tree-nav__item directory-items"})
        return directory_items_soup

    def create_item_qty(self, quantity: int, item_type: FSItemType, per_fextension_qty: FileExtAccumulator = {}) -> Tag:
        file_qty_soup = self.soup.new_tag("span", attrs={"class":"tree-nav__item-title file-qty"})
        if item_type == "file":
            file_summary = f"[{quantity} Archivos, "
            for ext, qty in per_fextension_qty.items():
                file_summary += f"\"{ext}\":{qty}, "
            
            file_summary = file_summary[:-2]
            file_summary += f"]"
            file_qty_soup.string = file_summary
        else:
            file_qty_soup.string = f"[{quantity} Carpetas]"
        return file_qty_soup
    
    def create_dir(self, name: str, size: str, description: str | None) -> Tag:
        directory_soup = self.soup.new_tag("details", attrs={"class":"tree-nav__item is-expandable directory"})
        summary = self.soup.new_tag("summary", attrs={"class":"tree-nav__item-title"})
        tooltip_container = self.soup.new_tag("div", attrs={"class":"tooltip"})
        icon = self.soup.new_tag("i", attrs={"class":"icon ion-folder"})
        
        title = self.soup.new_tag("span", attrs={"class":"directory-name"})
        title.string = name
        dir_size = self.soup.new_tag("span", attrs={"class":"directory-size", "style":"font-style: italic;"})
        dir_size.string = f" - {size}"

        summary.append(icon)
        if description:
            tooltip_text = self.soup.new_tag("span", attrs={"class":"tooltiptext"})
            tooltip_text.string = description
            tooltip_container.append(title)
            tooltip_container.append(dir_size)
            tooltip_container.append(tooltip_text)
            summary.append(tooltip_container)
        else:
            summary.append(title)
            summary.append(dir_size)
        directory_soup.append(summary)
        return directory_soup

    def create_file(self, fname: str) -> Tag: 
        fcontainer_soup = self.soup.new_tag("span", attrs={"class":"tree-nav__item-title file"})
        icon = self.soup.new_tag("i", attrs={"class":"icon ion-document-text"})
        
        title = self.soup.new_tag("span", attrs={"class":"file-name"})
        title.string = fname

        fcontainer_soup.append(icon)
        fcontainer_soup.append(title)
        return fcontainer_soup



root_title_wrapper = base_report_body.find(id="root-title-wrapper")
root_title_wrapper


# %%
def rename_root(soup_body: Tag, new_name: str):
    soup_body.find(class_="root-title").string = new_name

def add_description_to_root(soup_body: Tag, description: str | None):
    if description:
        soup_body.find(class_="root-tooltiptext").string = description

def clear_root(soup_body: Tag):
    soup_body.find(class_="root").clear()

def add_root_size():
    pass


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
            directory = rtg.create_dir(children_stats["name"], children_stats["size_str"],  children_stats.get("description", None))
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
rename_root(base_report_body, meta_vol1["name"])
add_description_to_root(base_report_body, meta_vol1.get("description", None))
root_dir = base_report_body.find(id="root-title-wrapper")
clear_root(base_report_body)
first_expandable_dir = base_report_body.details
first_expandable_dir.append(root_dir)

consice_populate_html(first_expandable_dir, meta_vol1)

with open(report_vol1, "w") as file:
    file.write(str(base_report_soup))


