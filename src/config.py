"""
Store the config for the ruyi index updator
"""

import os
import argparse
from typing import TypedDict, ReadOnly, NotRequired


class CFG():
    """
    Wrapper for the args to act as a singleton dict
    """

    class CFGOne(TypedDict):
        """
        The type of the cli config
        """
        name: ReadOnly[str]
        short_name: NotRequired[ReadOnly[str]]
        explain: NotRequired[ReadOnly[str]]
        default: NotRequired[ReadOnly[str]]
        action: NotRequired[ReadOnly[str]]
        nargs: NotRequired[ReadOnly[str]]

    def __set_arg(self, arg: argparse.ArgumentParser, c: CFGOne):
        if "short_name" in c:
            arg.add_argument(
                f'-{c["short_name"]}',
                f'--{c["name"]}',
                help=c["explain"] if "explain" in c else None,
                default=c["default"] if "default" in c else None,
                action=c["action"] if "action" in c else None,
            )
        else:
            arg.add_argument(
                f'--{c["name"]}',
                help=c["explain"] if "explain" in c else None,
                default=c["default"] if "default" in c else None,
                action=c["action"] if "action" in c else None,
            )

    def __init__(self, config_list: list[CFGOne]):
        arg = argparse.ArgumentParser()
        for c in config_list:
            self.__set_arg(arg, c)
        args = arg.parse_args()
        self.configs = args

    def __getitem__(self, key: str):
        return self.configs.__getattribute__(key)


_cli_configs = CFG([
    {'name': 'matrix', 'short_name': 'm',
        'explain': 'path to the support matrix', 'default': './matrix'},
    {'name': 'path', 'short_name': 'p',
        'explain': 'path to the config directory', 'default': './configs'},
    {'name': 'report', 'short_name': 'r',
        'explain': 'path to the report file', 'default': './report.md'},
    {'name': 'issue', 'explain': 'create issues if newer', 'default': False,
        'action': 'store_true'},
])

_internal_configs = {
    "CI_RUN_ID": os.getenv("CI_RUN_ID", None),
    "CI_RUN_URL": os.getenv("CI_RUN_URL", None),
    "ISSUE_REPO": os.getenv("ISSUE_REPO", None),
    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", None),
}


class CFGdict():
    """
    Dict like wrapper for the config, merge the cli config and internal config
    """

    __d = {}
    _cfg = {}

    def __init__(self):
        pass

    def __getitem__(self, key: str):
        if key in self.__d:
            return self.__d[key]
        elif key in _cli_configs.configs:
            return _cli_configs[key]
        elif key in _internal_configs:
            return _internal_configs[key]
        elif key in self._cfg:
            return self._cfg[key]
        else:
            return None

    def __setitem__(self, key: str, value):
        self.__d[key] = value


config = CFGdict()
