import os

from dotenv import load_dotenv

import dree
import to_html

load_dotenv()
vol1_dir = os.environ.get("VOL1_DIR", "")
vol2_dir = os.environ.get("VOL2_DIR", "")
vol1_outfile = os.environ.get("OUTFILE_VOL1", "meta.json")
vol2_outfile = os.environ.get("OUTFILE_VOL2", "meta.json")
desc_file = os.environ.get("DESCRIPTIONS_FILE", "descriptions.json")


def final() -> None:
    pass


def main() -> None:
    dree.scan_dir(vol1_dir, vol1_outfile, desc_file)
    dree.scan_dir(vol2_dir, vol2_outfile, desc_file)
    # to_html.run(vol1_outfile, vol2_outfile)


if __name__ == "__main__":
    main()
    # other()
