"""
This file let nvrunner runs in a script and return the results.

It is directily copy and modify from the nvchecker's main, which uses MIT License
"""

import os
import argparse
import asyncio
import logging
from typing import Coroutine, Tuple, cast
import queue
import yaml
import json
import toml

from nvchecker import core
from nvchecker.util import KeyManager, Entries
from nvchecker.core import Options
from nvchecker.util import ResultData, RawResult, EntryWaiter

logger = logging.getLogger(__name__)


async def run(
    result_coro: Coroutine[None, None, Tuple[ResultData, bool]],
    runner_coro: Coroutine[None, None, None],
) -> Tuple[ResultData, bool]:
    """
    From original nvchecker, create a runner
    """
    result_fu = asyncio.create_task(result_coro)
    runner_fu = asyncio.create_task(runner_coro)
    await runner_fu
    result_fu.cancel()
    return await result_fu


def load_config_from_dict(config: dict, working_dir: str = None):

    ver_files = None
    keymanager = KeyManager(None)
    source_configs = {}

    if '__config__' in config:
        c = config.pop('__config__')
        d = working_dir

        if 'oldver' in c and 'newver' in c:
            oldver_s = os.path.expandvars(
                os.path.expanduser(c.get('oldver')))
            oldver = d / oldver_s
            newver_s = os.path.expandvars(
                os.path.expanduser(c.get('newver')))
            newver = d / newver_s
            ver_files = oldver, newver

        if 'source' in c:
            source_configs = c['source']

        max_concurrency = c.get('max_concurrency', 20)
        proxy = c.get('proxy')
        httplib = c.get('httplib', None)
        http_timeout = c.get('http_timeout', 20)
    else:
        max_concurrency = 20
        proxy = None
        httplib = None
        http_timeout = 20

    return cast(Entries, config), Options(
        ver_files, max_concurrency, proxy, keymanager,
        source_configs, httplib, http_timeout,
    )


def merge_configs(
        a: dict, b: dict) -> dict:

    # if b[skip] exists and is true, skip merging
    if b.get('skip', False):
        return a

    for k, v in b.items():
        if isinstance(v, dict) and k in a and isinstance(a[k], dict):
            a[k] = merge_configs(a[k], v)
        else:
            a[k] = v
    return a


def load_all_configs(
    conf_dir: str = '.',
    matrix_dir: str = '.',
) -> tuple[dict, set, set]:
    skip_dirs = ['.', '..', 'report-template',
                 'assets', '.git', '.github', '.venv']

    res = {}
    q = queue.Queue()
    q.put((conf_dir, matrix_dir))

    skipped = set()
    manually_skipped = set()

    # matrix as base directory
    # iterate all sub directories, layer by layer
    while not q.empty():
        cur_conf, cur_matrix = q.get()
        sub_dirs = os.listdir(cur_matrix)
        has_sub_dirs = False
        for f in sub_dirs:
            if f in skip_dirs:
                continue
            cur_conf2 = os.path.join(cur_conf, f)
            cur_matrix2 = os.path.join(cur_matrix, f)
            if os.path.isdir(cur_matrix2):
                has_sub_dirs = True
                if not os.path.exists(cur_conf2):
                    # logger.warning(
                    # "Config directory %s does not exist, skipping", cur_conf2)
                    skipped.add(cur_conf2)
                    continue
                q.put((cur_conf2, cur_matrix2))

        sub_confs = os.listdir(cur_conf)
        has_sub_confs = False
        for f in sub_confs:
            cur_conf2 = os.path.join(cur_conf, f)
            if not os.path.isfile(cur_conf2):
                continue
            if f not in ('config.yaml', 'config.yml', 'config.toml', 'config.json'):
                skipped.add(cur_conf2)
                continue
            conf = None
            has_sub_confs = True
            if f in ('config.yaml', 'config.yml'):
                with open(cur_conf2, 'r', encoding='utf-8') as f:
                    try:
                        conf = yaml.load(f, Loader=yaml.FullLoader)
                    except yaml.YAMLError as e:
                        logger.error(
                            "Failed to parse YAML file %s: %s", cur_conf2, e)
                        continue
            if f == 'config.toml':
                with open(cur_conf2, 'r', encoding='utf-8') as f:
                    try:
                        conf = toml.load(f)
                    except toml.TomlDecodeError as e:
                        logger.error(
                            "Failed to parse TOML file %s: %s", cur_conf2, e)
                        continue
            if f == 'config.json':
                with open(cur_conf2, 'r', encoding='utf-8') as f:
                    try:
                        conf = json.load(f)
                    except json.JSONDecodeError as e:
                        logger.error(
                            "Failed to parse JSON file %s: %s", cur_conf2, e)
                        continue
            if not conf or len(conf) == 0:
                logger.warning("Config file %s is empty, skipping", cur_conf2)
                skipped.add(cur_conf2)
                continue
            if conf.get('eol', False):
                continue
            if conf.get('skip', False):
                logger.info("Skipping config %s", cur_conf2)
                reason = conf.get('reason', 'No reason provided')
                manually_skipped.add(
                    (cur_conf2, reason))
                continue
            res = merge_configs(res, conf)
        
        if not has_sub_confs and not has_sub_dirs:
            logger.warning(
                "No config files found in %s, skipping", cur_conf)
            skipped.add(cur_conf)
    return res, skipped, manually_skipped


def run_nvchecker(conf_dir: str = '.', matrix_dir: str = '.', oldvers: dict = None,
                  logging='warning', logger='pretty', version=False) -> Tuple[dict, bool, set, set]:
    """
    Modified way to run nvchecker in program
    return: new_ver, has_failure
    """
    if oldvers is None:
        oldvers = {}
    args = argparse.Namespace(
        logging=logging,
        logger=logger,
        version=version,
    )
    if core.process_common_arguments(args):
        return

    confs, skipped, manually_skipped = load_all_configs(
        conf_dir=conf_dir,
        matrix_dir=matrix_dir
    )

    entries, options = load_config_from_dict(
        confs,
        working_dir=conf_dir
    )

    task_sem = asyncio.Semaphore(options.max_concurrency)
    result_q: asyncio.Queue[RawResult] = asyncio.Queue()
    dispatcher = core.setup_httpclient(
        options.max_concurrency,
        options.httplib,
        options.http_timeout,
    )
    entry_waiter = EntryWaiter()
    futures = dispatcher.dispatch(
        entries, task_sem, result_q,
        options.keymanager, entry_waiter,
        3,
        options.source_configs,
    )

    result_coro = core.process_result(
        oldvers, result_q, entry_waiter, verbose=False)
    runner_coro = core.run_tasks(futures)

    results, has_failures = asyncio.run(run(result_coro, runner_coro))

    new_vers = dict(sorted(results.items()))

    return (new_vers, has_failures, skipped, manually_skipped)


if __name__ == '__main__':
    _, __ = run_nvchecker()
    print(_)
