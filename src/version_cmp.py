"""
Compare two versions
"""
from awesomeversion import AwesomeVersion
from nvchecker.core import RichResult


def version_cmp(v1: str, v2: str) -> int:
    """
    Compare two versions
    """
    v1 = AwesomeVersion(v1)
    v2 = AwesomeVersion(v2)

    # replace all space in version strings with '-'
    v1 = v1.replace(" ", "-")
    v2 = v2.replace(" ", "-")

    # remove the 'v' prefix if it exists
    if v1.startswith("v"):
        v1 = v1[1:]
    if v2.startswith("v"):
        v2 = v2[1:]

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


def filter_newer(oldvers: dict[RichResult], newvers: dict[RichResult]) -> dict[RichResult]:
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
