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
Prints the pinned "none-any" wheel URL for each named package in uv.lock.

The documentation build gives these URLs to JupyterLite and to the playground.
Both then run the versions that uv.lock pins.
"""

import re
import sys
import tomllib
from collections.abc import Iterable, Iterator
from pathlib import Path

UV_LOCK_PATH = Path("uv.lock")


def pinned_wheel_urls(pkg_names: Iterable[str]) -> Iterator[str]:
    r"""
    Yields one wheel URL for each name in *pkg_names*, in order.
    Raises `RuntimeError` if a package has no pure-Python wheel.
    """
    with UV_LOCK_PATH.open("rb") as f:
        uv_lock = tomllib.load(f)

    for pkg_name in pkg_names:
        pkg = next(p for p in uv_lock["package"] if p["name"] == pkg_name)

        try:
            yield next(
                w["url"]
                for w in pkg.get("wheels", [])
                if re.search(r"\bnone-any\b", w["url"])
            )
        except StopIteration:
            raise RuntimeError(
                f"no none-any wheel for {pkg_name!r} found in {UV_LOCK_PATH}"
            ) from None


def main() -> None:
    for url in pinned_wheel_urls(sys.argv[1:]):
        sys.stdout.write(url + "\n")


if __name__ == "__main__":
    main()
