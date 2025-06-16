"""
Check for updates in the matrix
"""

import sys
import argparse
import logging
from matrix.assets.src.matrix_parser import Systems
from src.run_nvchecker import run_nvchecker
from src.version_cmp import filter_newer
from src.utils import gen_old

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def gen_report(newer, skipped):
    """
    Generate a report of the new versions found
    """

    res = ""
    res += """
# Update Report

## New Versions Found

| Product Triple | Old Version | New Version |
| -------------- | ----------- | ----------- |
"""

    for prod, ver in newer.items():
        if ver['new'] is None:
            continue
        trip = prod
        old_s = ver['old'].version if ver['old'] else "N/A"
        new_s = ver['new'].version if ver['new'] else "N/A"
        res += f"| {trip} | {old_s} | {new_s} |\n"

    res += """
## Skipped Products

These products doesn't have any configs! You need to add them later.

| Path |
| ---- |
"""

    for p in skipped:
        res += f"| {p} |\n"

    return res


def main():
    """
    Main function
    """

    arg = argparse.ArgumentParser()
    arg.add_argument(
        '-m', '--matrix', help='path to the support matrix', default='./matrix')
    arg.add_argument(
        '-p', '--path', help='path to the config directory',
        default='./configs'
    )
    arg.add_argument(
        '-r', '--report', help='path to the report file',
        default='./report.md'
    )
    args = arg.parse_args()

    matrix = Systems(args.matrix)

    old = gen_old(matrix)

    new, fail, skipped = run_nvchecker(
        conf_dir=args.path, matrix_dir=args.matrix, oldvers=old)
    if fail:
        logger.exception("Failed to run nvchecker: %s", fail)
        sys.exit(-1)

    upd = filter_newer(old, new)

    has_update = False
    for prod, ver in upd.items():
        if ver['old'] is None:
            logger.info(
                "Found new version for %s: %s", prod, ver['new']['version'])
            has_update = True
        elif ver['new'] is None:
            # logger.info(
            # "No new version found for %s", prod)
            continue
        else:
            logger.info(
                "Can be updated for %s: %s -> %s",
                prod, ver['old'].version, ver['new'].version)
            has_update = True

    if has_update:
        logger.info("Update available")

    report = gen_report(upd, skipped)

    with open(args.report, 'w', encoding='utf-8') as f:
        f.write(report)
        logger.info("Report written to %s", args.report)


if __name__ == '__main__':
    main()
