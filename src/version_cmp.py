"""
Compare two versions
"""
from awesomeversion import AwesomeVersion
from nvchecker.core import RichResult
import re


def version_cmp(v1: str, v2: str) -> int:
    """
    Compare two versions
    """
    v1 = AwesomeVersion(v1)
    v2 = AwesomeVersion(v2)

    # replace all space in version strings with '-'
    v1 = v1.replace(" ", "-")
    v2 = v2.replace(" ", "-")

    # make all versions lowercase
    v1 = v1.lower()
    v2 = v2.lower()

    # remove the 'v' prefix if it exists
    if v1.startswith("v"):
        v1 = v1[1:]
    if v2.startswith("v"):
        v2 = v2[1:]

    # special case: if "sp*" is in the version, treat it as a suffix.
    # Like "2.0-sp1" becomes "2.0+sp1" to make it bigger than "2.0".
    # Note: the `-sp\d+` field may not be at the end of the version string.
    def replace_sp_suffix(version: str) -> str:
        # Split the version by '-sp\d+' into parts
        parts = re.split(r'(-sp\d+)', version)
        # Replace the '-sp\d+' part with '+sp\d+' if it exists
        for i in range(len(parts)):
            if parts[i].startswith('-sp'):
                parts[i] = '+' + parts[i][1:]
        # Join the parts back together
        return ''.join(parts)

    v1 = replace_sp_suffix(v1)
    v2 = replace_sp_suffix(v2)

    if v1 > v2:
        return 1
    if v1 < v2:
        return -1
    return 0


def is_newer(v1: str, v2: str) -> bool:
    """
    Check if v1 is newer than v2
    """
    return version_cmp(v1, v2) == 1


def is_older(v1: str, v2: str) -> bool:
    """
    Check if v1 is older than v2
    """
    return version_cmp(v1, v2) == -1


def is_same(v1: str, v2: str) -> bool:
    """
    Check if v1 is the same as v2
    """
    return version_cmp(v1, v2) == 0


def filter_newer(oldvers: dict[str, RichResult], newvers: dict[str, RichResult]) -> dict[RichResult]:
    """
    Filter out the newer versions
    """
    result: dict[str, dict["old" | "new", int | None]] = {}  # type: ignore
    for prod, ver in newvers.items():
        if prod not in oldvers:
            result[prod] = {"old": None, "new": ver}
            continue
        if is_newer(ver, oldvers[prod]):
            result[prod] = {"old": oldvers[prod], "new": ver}
    for prod, ver in oldvers.items():
        if prod not in newvers:
            result[prod] = {"old": ver, "new": None}
    return result
