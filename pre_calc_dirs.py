from dtypes import PreGenTreeHolder
from dree import StatsGenerator
from utils import parse_size
import json
import os
import pathlib
import pprint
import tqdm
import timeit
import dree
from dotenv import load_dotenv

load_dotenv()
desc_file = os.environ.get("DESCRIPTIONS_FILE", "descriptions.json")


def main() -> None:
    # dree.scan_dir(vol1_dir, vol1_outfile, desc_file)
    dree.scan_dir("/home/malcon/NAS_Vol2-ImageDB_Related/Image_Database/RINK/Q4-2023",
                  "Q4-2023.json", desc_file)
    # dree.scan_dir(f"{vol2_dir}/Image_Database/RINK/Q3-2023",
    #   "idk.json", desc_file)
    pass


if __name__ == "__main__":
    main()
    # other()


# pregenerate_file = "pregenerated_tree.json"
# problematic: PreGenTreeHolder = json.load(open(pregenerate_file, "r"))


# root = pathlib.Path("/home/malcon/NAS_Vol2-ImageDB_Related/Image_Database")
# root_str = root.as_posix()
# stat_gen = StatsGenerator(root_str)
# for dir in problematic["dirs"]:
#     start_time = timeit.default_timer()

#     # code you want to evaluate
#     path = root.joinpath(dir)
#     items = os.listdir(path)
#     item_qty = len(items)

#     elapsed = timeit.default_timer() - start_time
#     print("Elapsed time of .listdir():", elapsed)

#     total_size = path.stat().st_size
#     for item in tqdm.tqdm(items):
#         f_path = path.joinpath(item)
#         total_size += f_path.stat().st_size

#     first_f_path = path.joinpath(items[0])
#     last_f_path = path.joinpath(items[-1])

#     problematic["pregenerated_trees"] = {dir: {"name": dir,
#                                                "path": path.as_posix(),
#                                                "relative_path": path.relative_to(root).as_posix(),
#                                                "type": "directory",
#                                                "size": total_size,
#                                                "size_str": parse_size(total_size),
#                                                "file_qty": item_qty,
#                                                "per_fextension_qty": {"jpg": item_qty},
#                                                "dir_qty": 0,
#                                                # hash: str
#                                                "children": [stat_gen.generate_stats(first_f_path), stat_gen.generate_stats(last_f_path)]}
#                                          }

#     pprint.pprint(problematic)


# with open(pregenerate_file, "w") as out_f:
#     json.dump(problematic, out_f, indent=4)
