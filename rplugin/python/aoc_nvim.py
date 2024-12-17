from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import urllib.request
import urllib.error
import time
from dataclasses import dataclass
import re
from functools import wraps

import pynvim


@dataclass
class AocPlugin:
    nvim: pynvim.Nvim

    def __post_init__(self) -> None:
        self.cookie: str | None = self.nvim.vars.get("aoc_session_cookie")
        self.base_dir: Path = Path(self.nvim.eval("getcwd()"))

    def _get_headers(self) -> dict[str, str]:
        if not self.cookie:
            self.nvim.err_write("No session cookie set. Use :AocSetCookie\n")
            raise ValueError("No cookie set")
        return {
            "Cookie": f"session={self.cookie}",
            "User-Agent": "github.com/username/aoc-nvim by email@example.com",
        }

    def get_current_day(self) -> tuple[int, int]:
        """Get year and day from current working directory."""
        cwd = self.base_dir
        day_dir = cwd.name
        year_dir = cwd.parent.name

        if not day_dir.startswith("day") or not year_dir.startswith("aoc"):
            self.nvim.err_write("Not in an advent of code directory\n")
            raise ValueError("Invalid directory structure")

        return int(year_dir[3:]), int(day_dir[3:])

    def timing(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                end = time.time()
                elapsed = (end - start) * 1000
                unit = "ms"
                if elapsed < 100:
                    elapsed *= 1000
                    unit = "μs"
                self.nvim.out_write(f"> {int(elapsed)} {unit} ({func.__name__})\n")

        return wrapper

    @timing
    def download_input(self) -> None:
        """Download input for current day."""
        year, day = self.get_current_day()
        url = f"https://adventofcode.com/{year}/day/{day}/input"

        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req) as response:
                input_data = response.read().decode()

            input_file = self.base_dir / "input.txt"
            input_file.write_text(input_data)
            input_file.chmod(0o400)  # Read-only

            self.nvim.out_write(f"Downloaded input for day {day}\n")

        except urllib.error.URLError as e:
            self.nvim.err_write(f"Failed to download input: {e}\n")

    @timing
    def submit_solution(self, part: int, answer: str) -> None:
        """Submit solution for current day."""
        year, day = self.get_current_day()
        url = f"https://adventofcode.com/{year}/day/{day}/answer"

        data = urllib.parse.urlencode(
            {"level": part, "answer": answer.strip()}
        ).encode()

        try:
            req = urllib.request.Request(
                url, data=data, headers=self._get_headers(), method="POST"
            )

            with urllib.request.urlopen(req) as response:
                result = response.read().decode()

            if "That's the right answer!" in result:
                self.nvim.out_write("\x1b[32mCorrect answer!\x1b[0m\n")
            elif "That's not the right answer" in result:
                self.nvim.err_write("\x1b[31mIncorrect answer\x1b[0m\n")
            elif "You gave an answer too recently" in result:
                wait = re.search(r"You have (\d+m\s*\d+s) left to wait", result)
                if wait:
                    self.nvim.err_write(
                        f"\x1b[33mToo many attempts. Wait {wait.group(1)}\x1b[0m\n"
                    )
            else:
                self.nvim.err_write(f"Unexpected response: {result}\n")

        except urllib.error.URLError as e:
            self.nvim.err_write(f"Failed to submit solution: {e}\n")


@pynvim.plugin
class AocNeovimPlugin:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim
        self.aoc = AocPlugin(nvim)

    @pynvim.command("AocDownload", nargs=0, sync=True)
    def download_input(self) -> None:
        self.aoc.download_input()

    @pynvim.command("AocSubmit", nargs=1, sync=True)
    def submit_solution(self, args: list[str]) -> None:
        if not args or args[0] not in ("1", "2"):
            self.nvim.err_write("Usage: AocSubmit <part> (1 or 2)\n")
            return

        # Get the current line or visual selection
        mode = self.nvim.api.get_mode()["mode"]
        if mode == "v" or mode == "V":
            self.nvim.command("normal! y")
            answer = self.nvim.eval('@"')
        else:
            answer = self.nvim.current.line

        self.aoc.submit_solution(int(args[0]), answer)

    @pynvim.command("AocSetCookie", nargs=1, sync=True)
    def set_cookie(self, args: list[str]) -> None:
        if not args:
            self.nvim.err_write("Usage: AocSetCookie <session_cookie>\n")
            return
        self.nvim.vars["aoc_session_cookie"] = args[0]
        self.nvim.out_write("Session cookie set\n")
