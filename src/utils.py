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


def gen_old(matrix) -> dict[str, RichResult]:
    """
    Generate old versions from the matrix
    :param matrix: Systems object
    :return: list of old versions
    """
    res = {}
    old = gen_oldver(matrix)

    for vinfo in old:
        b_variants = vinfo.board_variants + ['generic'] if vinfo.board_variants else [
            "generic"]
        if vinfo.version is None:
            continue
        if vinfo.variant is None:
            vinfo.variant = "null"
        for b_variant in b_variants:
            res[f"{vinfo.vendor}-{b_variant}-{vinfo.system}-{vinfo.variant}"] = SelfRichResult(
                version=vinfo.version,
                vinfo=vinfo,
            )
    return res
