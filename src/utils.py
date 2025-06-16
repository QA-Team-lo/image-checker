from matrix.assets.src.matrix_parser import Systems, gen_oldver
from nvchecker.core import RichResult


def gen_old(matrix) -> dict[str, RichResult]:
    """
    Generate old versions from the matrix
    :param matrix: Systems object
    :return: list of old versions
    """
    res = {}
    old = gen_oldver(matrix)

    for vinfo in old:
        b_variants = vinfo.board_variants if vinfo.board_variants else [
            "generic"]
        if vinfo.version is None:
            continue
        for b_variant in b_variants:
            res[f"{vinfo.vendor}-{b_variant}-{vinfo.system}-{vinfo.variant}"] = RichResult(
                version=vinfo.version
            )
    return res
