# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!! IMPORTANT: READ THIS BEFORE EDITING! !!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Please keep each docstring sentence on its own unwrapped line. It looks like crap in a
# text editor, but it has no effect on rendering, and it allows much more useful diffs.
# (This does not apply to code comments.) Thank you!
# ======================================================================================

r"""
Assembles the browser playground and its pinned wheels into the documentation tree.

Zensical has no post-build hook.
This script writes the playground into `docs/` before the site build, and the site
build then copies it with the other documentation content.
The site serves the wheels from its own origin, which prevents cross-origin resource
sharing (CORS) errors in the browser.
"""

import json
import logging
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).parent))

from _uv_lock_wheels import pinned_wheel_urls

_LOGGER = logging.getLogger(__name__)

PINNED_PKG_NAMES = ("dyce", "lark", "optype")
PLAYGROUND_EXCLUDES = ("node_modules", "package.json", "test")


def latest_pkg_wheel_from_dist() -> Path:
    return max(Path("dist").glob("dyceum*-none-any.whl"), key=os.path.getmtime)


def assemble(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*PLAYGROUND_EXCLUDES))
    wheels_dir = dst / "wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []

    for url in pinned_wheel_urls(PINNED_PKG_NAMES):
        _LOGGER.info("downloading %s", url)
        filename = Path(urlsplit(url).path).name
        urllib.request.urlretrieve(url, wheels_dir / filename)  # ruff: ignore[suspicious-url-open-usage]
        names.append(filename)

    pkg_whl = latest_pkg_wheel_from_dist()
    shutil.copy2(pkg_whl, wheels_dir / pkg_whl.name)
    names.append(pkg_whl.name)
    (wheels_dir / "index.json").write_text(json.dumps(names, indent=2) + "\n", "utf_8")
    _LOGGER.info("assembled playground -> %s (%d wheels)", dst, len(names))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    assemble(Path("playground"), Path(sys.argv[1]))


if __name__ == "__main__":
    main()
