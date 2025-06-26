from dataclasses import dataclass

from nvchecker.core import RichResult

from matrix.assets.src.matrix_parser import Systems, gen_oldver, SystemInfo


@dataclass
class SelfRichResult(RichResult):
    """
    A class to represent a rich result with additional attributes.
    Inherits from RichResult.
    """
    vinfo: SystemInfo


def gen_item_name(vinfo: SystemInfo,
                  overwrite_vendor: str | None = None,
                  overwrite_system: str | None = None,
                  overwrite_variant: str | None = None,
                  overwrite_board_variants: list[str] | None = None) -> list[str]:
    """
    Generate a unique item name based on the system information.
    :param vinfo: SystemInfo object
    :return: Unique item name
    """
    vendor = overwrite_vendor or vinfo.vendor
    system = overwrite_system or vinfo.system
    variant = overwrite_variant or vinfo.variant or "null"
    board_variants = overwrite_board_variants or vinfo.board_variants

    b_variants = board_variants + \
        ['generic'] if board_variants else ["generic"]

    if variant is None:
        variant= "null"
    return [f"{vendor}-{b_variant}-{system}-{variant}" for b_variant in b_variants]


def gen_old(matrix) -> dict[str, SelfRichResult]:
    """
    Generate old versions from the matrix
    :param matrix: Systems object
    :return: list of old versions
    """
    res = {}
    old = gen_oldver(matrix)

    for vinfo in old:
        if vinfo.version is None:
            continue
        for name in gen_item_name(vinfo):
            res[name] = SelfRichResult(
                version=vinfo.version,
                vinfo=vinfo,
            )
    return res
