"""
Check for updates in the matrix
"""

import sys
import logging
from matrix.assets.src.matrix_parser import Systems
from src.run_nvchecker import run_nvchecker
from src.version_cmp import filter_newer
from src.utils import gen_old, SelfRichResult
from src.config import config
import src.github_action as gh

logging.basicConfig(
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)


def gen_report(newer, skipped, manually_skipped):
    """
    Generate a report of the new versions found
    """

    res = ""
    res += """
# Update Report

## New Versions Found

| Product Triple | Product:System:Variant | Old Version | New Version |
| -------------- | ---------------------- | ----------- | ----------- |
"""

    for prod, ver in newer.items():
        if ver['new'] is None:
            continue
        trip = prod
        old_s = ver['old'].version if ver['old'] else "N/A"
        new_s = ver['new'].version if ver['new'] else "N/A"
        p_s_v = f"{ver['old'].vinfo.product}:{ver['old'].vinfo.system}:{ver['old'].vinfo.variant}"
        res += f"| {trip} | {p_s_v} | {old_s} | {new_s} |\n"

    res += """
## Skipped Products

These products doesn't have any configs! You need to add them later.

| Path | Matrix |
| ---- | ------ |
"""

    for p in skipped:
        mat_p=p.replace("configs/", "matrix/")
        res += f"| [{p}]({p}) | [{mat_p}]({mat_p})  |\n"

    res += """
## Manually Skipped Products
These products were manually skipped and will not be checked for updates.
Please check them manually.
| Path | Reason |
| ---- | ------ |
"""
    for p in manually_skipped:
        res += f"| [{p[0]}]({p[0]}) | {p[1]} |\n"

    res += "\n\n"

    return res


def main():
    """
    Main function
    """

    matrix = Systems(config["matrix"])

    old = gen_old(matrix)

    new, fail, skipped, manually_skipped = run_nvchecker(
        conf_dir=config["path"], matrix_dir=config["matrix"], oldvers=old)
    if fail:
        logger.exception("Failed to run nvchecker: %s", fail)
        sys.exit(-1)

    upd = filter_newer(old, new)

    report = gen_report(upd, skipped, manually_skipped)

    with open(config["report"], 'w', encoding='utf-8') as f:
        f.write(report)
        logger.info("Report written to %s", config["report"])

    if config["GITHUB_TOKEN"] is not None:
        github = gh.GithubManager(config["GITHUB_TOKEN"])
    else:
        github = None

    if config["issue"] and github is not None:
        logger.info("Creating issue in %s", config["ISSUE_REPO"])
        repo = gh.GithubRepoManager(github, config["ISSUE_REPO"])

        issues = repo.get_all_issues()
        for prod, ver in upd.items():
            if ver['new'] is None:
                continue
            old_res: SelfRichResult = ver['old']
            title = f"[Image Check] {old_res.vinfo.product}:{old_res.vinfo.system} has new version {ver["new"].version}"
            old_s = ver['old'].version if ver['old'] else "N/A"
            body = f"New version for {old_res.vinfo.product}:{old_res.vinfo.system}:{old_res.vinfo.variant} found: {old_s} -> {ver["new"].version}\n\n"

            for issue in issues:
                if title in issue.title:
                    logger.info("Issue already exists: %s", issue.title)
                    break
            else:
                issue = gh.Issue(title=title, body=body,
                                 labels=["image-check"])
                url = repo.create_issue(issue)
                if url:
                    logger.info("Issue created: %s", url)
                    issues.append(issue)
                else:
                    logger.error("Failed to create issue for %s", prod)


if __name__ == '__main__':
    main()
