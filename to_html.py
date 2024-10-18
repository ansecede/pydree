import json
from dtypes import FSItem, FSItemType, PreGenTreeHolder, ReportTagGenerator, TagCreatorFunction
from bs4 import BeautifulSoup, Tag, NavigableString


SUMMARY_BASE_REPORT = "with_html/min_base.html"

rtg = ReportTagGenerator(SUMMARY_BASE_REPORT)


def _clear_root(soup_body: Tag) -> None:
    soup_body.find(class_="tree-nav").clear()


def _clear_body(soup_body: Tag):
    soup_body.clear()


def _add_to_directory_items(parent_soup: Tag, creator: TagCreatorFunction, *args):
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


def _consice_populate_html(parent_soup: Tag, parent_stats: FSItem):
    f_children: list[Tag | NavigableString] = []
    print("Parent:", parent_soup.span.string)
    print(parent_stats["name"], parent_stats["type"], [
          t["name"] for t in parent_stats["children"]])

    for children_stats in parent_stats["children"]:
        if children_stats["type"] == "directory" and children_stats.get("description", None):
            directory = rtg.create_dir(
                children_stats["name"], children_stats.get("description", ""), None)
            children = _consice_populate_html(directory, children_stats)
            for child in children:
                directory.append(child)
            f_children.append(directory)
        else:
            continue
    # Checking some edge cases

    # Add file qty
    # if parent_stats["file_qty"] > 0:
    #     f_children.append(add_to_directory_items(parent_soup, rtg.create_item_qty, parent_stats["file_qty"], "file", parent_stats["per_fextension_qty"]))

    for child in f_children:
        parent_soup.append(child)
    # print(first_expandable_dir.prettify())

    return f_children


def run(meta_vol1_json, meta_vol2_json) -> None:
    meta_vol1: FSItem = json.load(open(meta_vol1_json, "r"))
    meta_vol2: FSItem = json.load(open(meta_vol2_json, "r"))
    report_vol2 = "with_html/NAS_report_Vol2.html"
    report_vol1 = "with_html/NAS_report_Vol1.html"

    with open(SUMMARY_BASE_REPORT) as base_file:
        base_report_soup = BeautifulSoup(base_file, features="html.parser")

    base_report_body = base_report_soup.body
    if not base_report_body:
        raise ValueError(f"base_report_body:{base_report_body}")
    base_report_logo = base_report_body.find("div", class_="title")

    _clear_root(base_report_body)
    vol1_root_dir = rtg.create_dir(
        meta_vol1["name"], meta_vol1.get("description", ""), None)
    main_container = base_report_body.nav
    if not main_container:
        raise ValueError(f"main_container:{main_container}")
    main_container.append(vol1_root_dir)
    first_expandable_dir = main_container.details

    _consice_populate_html(first_expandable_dir, meta_vol1)

    with open(report_vol1, "w") as file:
        file.write(str(base_report_soup))

    # NAS Vol2
    _clear_root(base_report_body)
    vol2_root_dir = rtg.create_dir(
        meta_vol2["name"], meta_vol2.get("description", ""), None)
    main_container = base_report_body.nav
    main_container.append(vol2_root_dir)
    first_expandable_dir = main_container.details

    _consice_populate_html(first_expandable_dir, meta_vol2)

    with open(report_vol2, "w") as file:
        file.write(str(base_report_soup))

    _clear_body(base_report_body)
    base_report_soup.body.append(base_report_logo)
    for html_report in [report_vol1, report_vol2]:
        with open(html_report) as file:
            html_report_soup = BeautifulSoup(file, features="html.parser")

        html_report_part = html_report_soup.body.nav
        base_report_soup.body.append(html_report_part)

    base_report_soup.body.append(rtg.separator())

    with open("reports/Reporte_NAS.html", "w") as file:
        file.write(str(base_report_soup))
