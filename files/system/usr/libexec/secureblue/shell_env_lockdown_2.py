#!/usr/bin/python3

# SPDX-FileCopyrightText: Copyright 2026 The Secureblue Authors
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import assert_never

from utils import (
    CommandUsageError,
    ToggleMode,
    command_stdout,
    command_succeeds,
    get_config_dir,
    parse_basic_toggle_args,
)

SHELL_ENV_FILES: list[tuple[str, list[Path]]] = [
    (
        "sh",
        [
            Path.home() / ".profile",
            get_config_dir() / "environment.d/",
        ],
    ),
    (
        "bash",
        [
            Path.home() / ".bash_aliases",
            Path.home() / ".bash_login",
            Path.home() / ".bash_logout",
            Path.home() / ".bash_profile",
            Path.home() / ".bashrc",
            Path.home() / ".bashrc.d/",
            get_config_dir() / "bash_completion/",
        ],
    ),
    (
        "zsh",
        [
            Path.home() / ".zlogin",
            Path.home() / ".zlogout",
            Path.home() / ".zprofile",
            Path.home() / ".zshenv",
            Path.home() / ".zshrc",
        ],
    ),
    (
        "fish",
        [
            get_config_dir() / "fish/config.fish",
            get_config_dir() / "fish/fish_variables",
            Path.home() / ".local/share/fish/vendor_conf.d/",
            get_config_dir() / "fish/completions",
            get_config_dir() / "fish/conf.d/",
            get_config_dir() / "fish/functions/",
        ],
    ),
]


def target_files() -> list[Path]:
    target_files: list[Path] = []
    for shell, files_list in SHELL_ENV_FILES:
        if command_succeeds("command", "-v", shell):
            target_files += files_list

    return target_files


def lockdown_status() -> None:

    class Colors:
        green = "\033[92m"
        red = "\033[91m"
        end = "\033[0m"

    for file in target_files():
        try:
            lockdown_check: str = command_stdout("lsattr", "-d", file)
            if "i" in lockdown_check.split(maxsplit=1)[0]:
                print(f"{file} {Colors.green}is immutable{Colors.end}")
            else:
                print(f"{file} {Colors.red}is not immutable{Colors.end}")
        except CalledProcessError:
            print(f"{file} {Colors.red}does not exist{Colors.end}")


def unlock_files() -> None:

    print("Unlocking files...")
    try:
        run(["/usr/bin/run0"], check=True)
    except CalledProcessError:
        print("Root permissions not granted. Exiting...")
        return

    for file in target_files():
        print(f"Unlocking {file}...")
        if str(file).endswith("/"):
            run(["/usr/bin/chattr", "-R", "-i", file], check=True)
        else:
            run(["/usr/bin/chattr", "-i", file], check=True)

    print("Files unlocked.")


def lock_files() -> None:

    user_input: str = "YES I UNDERSTAND"

    print("""WARNING: This will lock all the configuration files for your installed shells.
             This is needed to ensure the mitigation (see LD_PRELOAD attacks) is effective.""")

    if input(f"Type {user_input} and press Enter to continue: ") != user_input:
        print("Wrong user input received. Exiting...")

    print("Locking files...")
    try:
        run(["/usr/bin/run0"], check=True)
    except CalledProcessError:
        print("Root permissions not granted. Exiting...")
        return

    for file in target_files():
        print(f"Locking {file}...")
        if str(file).endswith("/"):
            file.mkdir(mode=600, parents=True, exist_ok=True)
            run(["/usr/bin/chattr", "-R", "+i", file], check=True)
        else:
            file.touch(mode=600, exist_ok=True)
            run(["/usr/bin/chattr", "+i", file], check=True)

    print("Files locked.")


def main() -> int:

    try:
        mode = parse_basic_toggle_args(prompt="Would you like to lockdown your shell environment?")
    except CommandUsageError as e:
        print(f"Usage error: {e}. See usage with --help.")
        return 2

    try:
        match mode:
            case ToggleMode.ON:
                lock_files()
            case ToggleMode.OFF:
                unlock_files()
            case ToggleMode.STATUS:
                lockdown_status()
            case ToggleMode.HELP:
                print("Help")
            case _ as unreachable:
                assert_never(unreachable)
    except CalledProcessError:
        print("An error occurred.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
