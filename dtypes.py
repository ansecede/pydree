from typing import TypedDict, Literal, Callable, NotRequired
from enum import Enum
import pathlib
from bs4 import BeautifulSoup, Tag


FSItemType = Literal["file", "directory"]


class EnumFSItemType(Enum):
    dir = "directory"
    file = "file"


FileExtAccumulator = dict[str, int]


class FSItem(TypedDict):
    name: str
    path: str
    relative_path: str
    type: FSItemType
    description: NotRequired[str]
    size: int
    size_str: str
    file_qty: int
    per_fextension_qty: FileExtAccumulator
    dir_qty: int
    # hash: str
    children: list["FSItem"]
    # children: list[Self]

    # def __iter__(self) -> Generator[tuple[str, str], Any, Any]:


DirTree = list[FSItem]


PreGenTreeMeta = dict[str, FSItem]

PreGenTreeHolderKeys = Literal["dirs", "pregenerated_trees"]


class PreGenTreeHolder(TypedDict):
    dirs: list[str]
    pregenerated_trees: PreGenTreeMeta


TagCreatorFunction = Callable[[int, FSItemType, FileExtAccumulator], Tag] | Callable[[
    str], Tag] | Callable[[], Tag]


class ReportTagGenerator:
    soup: BeautifulSoup

    def __init__(self, fpath: str | pathlib.Path) -> None:
        with open(fpath, "r") as base_file:
            self.soup = BeautifulSoup(base_file, "html.parser")

    def separator(self) -> Tag:
        separator_soup = self.soup.new_tag("div", attrs={"class": "title"})
        return separator_soup

    def directory_items(self) -> Tag:
        directory_items_soup = self.soup.new_tag(
            "div", attrs={"class": "tree-nav__item directory-items"})
        return directory_items_soup

    def create_item_qty(self, quantity: int, item_type: FSItemType, per_fextension_qty: FileExtAccumulator = {}) -> Tag:
        file_qty_soup = self.soup.new_tag(
            "span", attrs={"class": "tree-nav__item-title file-qty"})
        if item_type == "file":
            file_summary = f"[{quantity:,} Archivos - "
            for ext, qty in per_fextension_qty.items():
                file_summary += f"\"{ext}\":{qty:,}, "

            file_summary = file_summary[:-2]
            file_summary += f"]"
            file_qty_soup.string = file_summary
        else:
            file_qty_soup.string = f"[{quantity} Carpetas]"
        return file_qty_soup

    def create_dir(self, name: str, extra_text: str, tooltip_desc: str | None) -> Tag:
        directory_soup = self.soup.new_tag(
            "details", attrs={"class": "tree-nav__item is-expandable directory"})
        summary = self.soup.new_tag(
            "summary", attrs={"class": "tree-nav__item-title"})
        tooltip_container = self.soup.new_tag(
            "div", attrs={"class": "tooltip"})
        icon = self.soup.new_tag("i", attrs={"class": "icon ion-folder"})

        title = self.soup.new_tag(
            "span", attrs={"class": "directory-name bold"})
        title.string = name
        dir_size = self.soup.new_tag(
            "span", attrs={"class": "directory-size", "style": "font-style: italic;"})
        if extra_text:
            dir_size.string = f" - {extra_text}"

        summary.append(icon)
        if tooltip_desc:
            tooltip_text = self.soup.new_tag(
                "span", attrs={"class": "tooltiptext"})
            tooltip_text.string = tooltip_desc
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
        fcontainer_soup = self.soup.new_tag(
            "span", attrs={"class": "tree-nav__item-title file"})
        icon = self.soup.new_tag(
            "i", attrs={"class": "icon ion-document-text"})

        title = self.soup.new_tag("span", attrs={"class": "file-name"})
        title.string = fname

        fcontainer_soup.append(icon)
        fcontainer_soup.append(title)
        return fcontainer_soup
