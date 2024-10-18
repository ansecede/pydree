rtg = ReportTagGenerator(SUMMARY_BASE_REPORT)

# do root things
# ...
# rename_root(report_body, meta["name"])
# root_dir = report_body.find(id="root-title-wrapper")
# clear_root(report_body)
# first_expandable_dir = report_body.details
# first_expandable_dir.append(root_dir)


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


def populate_html(parent_soup: Tag, parent_stats: FSItem):
    f_children: list[Tag | NavigableString] = []
    print("Parent:", parent_soup.span.string)
    print(parent_stats["name"], parent_stats["type"], [
          t["name"] for t in parent_stats["children"]])

    for children_stats in parent_stats["children"]:
        if children_stats["type"] == "directory":
            directory = rtg.create_dir(
                children_stats["name"], children_stats["size_str"])
            children = populate_html(directory, children_stats)
            for child in children:
                directory.append(child)
            f_children.append(directory)
        elif children_stats["type"] == "file":
            f_children.append(add_to_directory_items(
                parent_soup, rtg.create_file, children_stats["name"]))
        # break
    # Checking some edge cases
    only_files_in_tree = (parent_stats["file_qty"] > 7) and (
        parent_stats["dir_qty"] == 0)
    only_dirs_in_tree = (parent_stats["file_qty"] == 0) and (
        parent_stats["dir_qty"] > 7)
    if only_files_in_tree or only_dirs_in_tree:
        f_children.append(add_to_directory_items(
            parent_soup, rtg.three_pointer))

    # Add file qty
    if parent_stats["file_qty"] > 7:
        f_children.append(add_to_directory_items(parent_soup, rtg.create_item_qty,
                          parent_stats["file_qty"], "file", parent_stats["per_fextension_qty"]))

    # Add dir qty
    if parent_stats["dir_qty"] > 7:
        f_children.append(add_to_directory_items(
            parent_soup, rtg.create_item_qty, parent_stats["dir_qty"], parent_stats["type"]))

    for child in f_children:
        parent_soup.append(child)
    print(parent_soup.prettify())
    # print(first_expandable_dir.prettify())

    return f_children

# populate_html(first_expandable_dir, meta)

# with open(report, "w") as file:
#     file.write(str(base_report_soup))
