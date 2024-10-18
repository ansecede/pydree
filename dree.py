import pathlib
from functools import reduce
import json
import os
import pathlib
import timeit

import pandas as pd
import tqdm

from dotenv import load_dotenv

from dtypes import FSItem, EnumFSItemType, FileExtAccumulator, PreGenTreeHolder
from utils import obtener_descripcion, parse_size


def _filter_fs_items(items: list[str]) -> list[str]:
    filtered = [item for item in items if not item[0] == '.']
    filtered = [item for item in filtered if not item[0] == '@']
    filtered = [item for item in filtered if not item == "__pycache__"]

    return filtered


def _count_file_extensions(files: list[str]) -> FileExtAccumulator:
    extensions: FileExtAccumulator = dict()
    for file in files:
        ext = pathlib.Path(file).suffix
        if ext in extensions:
            extensions[ext] += 1
        else:
            extensions[ext] = 1

    return extensions


def _order_fs_items(items: list[str], parent: pathlib.Path) -> tuple[list[str], int, int, FileExtAccumulator]:
    if len(items) < 1_000_000:
        dirs = sorted(
            [item for item in items if parent.joinpath(item).is_dir()])
        files = sorted(
            [item for item in items if parent.joinpath(item).is_file()])
        per_extensions_qty = _count_file_extensions(files)
    else:
        dirs = []
        files = items
        per_extensions_qty = {"jpg": len(files)}

    return dirs + files, len(dirs), len(files), per_extensions_qty


def _sanitize_fs_items(items: list[str], parent: pathlib.Path, stats:  FSItem) -> list[str]:
    if len(items) < 1_000_000:
        filtered = _filter_fs_items(items)
    else:
        filtered = items

    filtered_n_orderd, dir_qty, file_qty, per_extensions_qty = _order_fs_items(
        filtered, parent)

    stats["dir_qty"] = dir_qty
    stats["file_qty"] = file_qty
    stats["per_fextension_qty"] = per_extensions_qty

    return filtered_n_orderd


class StatsGenerator:
    root: str
    descriptions: dict[str, str]

    def __init__(self, root: str, descriptions: dict[str, str]):
        if root is None:
            raise ValueError(
                "Root is a required value")
        self.root = root
        self.descriptions = descriptions

    def generate_stats(self, path: pathlib.Path) -> FSItem:
        return {"name": path.name,
                "path": path.absolute().as_posix(),
                "relative_path": path.relative_to(self.root).as_posix(),
                "type": EnumFSItemType.dir.value if path.is_dir() else EnumFSItemType.file.value,
                "description": obtener_descripcion(path.name, self.descriptions),
                "size": path.stat().st_size,
                "size_str": "",
                "file_qty": 0,
                "per_fextension_qty": {},
                "dir_qty": 0,
                "children": []}


def _recursive_item_listing(items: list[str], parent: pathlib.Path, parent_stats: FSItem,
                            pre_calc_dirs: PreGenTreeHolder, stats_generator: StatsGenerator) -> list[FSItem]:
    children: list[FSItem] = []

    for item in tqdm.tqdm(items):
        item_path = parent.joinpath(item)
        item_stats = stats_generator.generate_stats(item_path)

        if item in pre_calc_dirs["dirs"]:
            # Here I just add the precalculated metadata
            print()
            print(f"{item}: Has precalc tree")
            item_stats = pre_calc_dirs["pregenerated_trees"][item]
            children.append(item_stats)
            continue
        elif item_path.is_dir():
            start_time = timeit.default_timer()
            print()
            print(f"{item}: listing dir")
            try:
                sibling_items = os.listdir(item_path)
            except Exception as e:
                print(e)
            elapsed = timeit.default_timer() - start_time
            print(f"{item}:", "Elapsed time of .listdir():", elapsed)

            sanitized_items = _sanitize_fs_items(
                sibling_items, item_path, item_stats)
            new_children = _recursive_item_listing(
                sanitized_items, item_path, item_stats, pre_calc_dirs, stats_generator)
            item_stats["size"] = reduce(
                lambda acc, item: acc+item["size"], new_children, 0)
            item_stats["size_str"] = parse_size(item_stats["size"])
            children.append(item_stats)

        elif item_path.is_file():
            children.append(item_stats)

        # break

    # only_dirs_in_tree = (parent_stats["file_qty"] == 0) and (
    #     parent_stats["dir_qty"] > 7)
    only_files_in_tree = (parent_stats["file_qty"] > 7) and (
        parent_stats["dir_qty"] == 0)
    if only_files_in_tree:
        parent_stats["children"] = []

    else:
        parent_stats["children"] = children

    return children


def scan_dir(root_dir: str, outfile: str, descriptions_fname: str) -> FSItem:
    root = pathlib.Path(root_dir)
    desc: dict[str, str] = json.load(open(descriptions_fname, "r"))

    stats_generator = StatsGenerator(root_dir, desc)
    root_stats = stats_generator.generate_stats(root)
    problematic: PreGenTreeHolder = json.load(
        open("pregenerated_tree.json", "r"))

    print("Root dir:", root, "- size", parse_size(root.stat().st_size))

    start_time = timeit.default_timer()
    print()
    print(f"{root}: listing root")
    sibling_items = os.listdir(root_dir)
    elapsed = timeit.default_timer() - start_time
    print(f"{root}:", "Elapsed time of .listdir(root):", elapsed)
    sanitized_items = _sanitize_fs_items(sibling_items, root, root_stats)
    print("sanitized_items:", sanitized_items)
    print(root_stats)

    root_stats["children"] = _recursive_item_listing(
        sanitized_items, root, root_stats, problematic, stats_generator)
    root_stats["size"] = reduce(
        lambda acc, item: acc+item["size"], root_stats["children"], 0)
    root_stats["size_str"] = parse_size(root_stats["size"])

    print("Writing output to:", outfile)
    with open(outfile, "w") as outf:
        json.dump(root_stats, outf, indent=4)
        pass

    return root_stats
