#!/usr/bin/python

# SPDX-FileCopyrightText: Copyright 2026 The Secureblue Authors
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError

from utils import command_stdout

SHELL_ENV_FILES: list[tuple[str, list[str]]] = [
    (
        "sh",
        [
            "~/.profile",
            "~/.config/environment.d/",
        ],
    ),
]

SHELL_ENV_FILES = [
    (shell, [str(Path(filepath).expanduser()) for filepath in files_list])
    for shell, files_list in SHELL_ENV_FILES
]


def file_status(files_list: list[str]) -> int:
    for file in files_list:
        try:
            imm_check: str = command_stdout("lsattr", "-d", file)
        except CalledProcessError:
            print(f"{file} does not exist")
        if "i" in imm_check:
            print(f"{file} is immutable")
        else:
            print(f"{file} is not immutable")

    return 0


# def lock_files(shell: str, file: str) -> None:
#     path: Path = Path(file)
#
#     if file.endswith("/"):
#         path.mkdir(mode=600, parents=True, exist_ok=True)
#         run(["/usr/bin/chattr", "+i", file], check=True)


def main() -> None:
    for shell, files_list in SHELL_ENV_FILES:
        if which(shell):
            file_status(files_list)


if __name__ == "__main__":
    sys.exit(main())
