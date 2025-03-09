import subprocess
import os
from typing import List, Dict, Any, Iterable
import json


class Freez:

    def __init__(self):
        self.win_man = WinManager()


class WinManager:

    def __init__(self):
        self._builder = CMD_Builder()

    def get_windows(self) -> List[Dict]:
        cmd = self._builder.build("List")
        res = subprocess.run(cmd, stdout=subprocess.PIPE)
        win_list = res.stdout.decode("utf-8")
        win_list = self._text_to_iterable(win_list, "[", "]")
        return win_list

    def _text_to_iterable(
        self, text: str, symbol_beg: str, symbol_end: str
    ) -> Iterable:
        start_idx = text.find(symbol_beg)
        end_idx = text.rfind(symbol_end)
        text = text[start_idx : end_idx + 1]
        text = json.loads(text)
        return text

    def list(self, pretty: bool = True) -> None:
        if not pretty:
            print(self.get_windows())
        else:
            for win in self.get_windows():
                for key, value in win.items():
                    print(f"{key}: {value}")
                print()

    def get_details(self, win_id: int) -> Dict:
        cmd = self._builder.build("Details", [win_id])
        res = subprocess.run(cmd, stdout=subprocess.PIPE)
        details = res.stdout.decode("utf-8")
        details = self._text_to_iterable(details, "{", "}")
        return details

    def details(self, win_id: int, pretty: bool = True) -> None:
        if not pretty:
            print(self.get_details(win_id))
        else:
            details = self.get_details(win_id)
            for key, value in details.items():
                print(f"{key}: {value}")
            print()

    def minimize(self, win_id: int) -> None:
        cmd = self._builder.build("Minimize", [win_id])
        subprocess.run(cmd)

    def unminimize(self, win_id: int) -> None:
        cmd = self._builder.build("Unminimize", [win_id])
        subprocess.run(cmd)

    def maximize(self, win_id: int) -> None:
        cmd = self._builder.build("Maximize", [win_id])
        subprocess.run(cmd)

    def unmaximize(self, win_id: int) -> None:
        cmd = self._builder.build("Unmaximize", [win_id])
        subprocess.run(cmd)

    def move(self, win_id: int, x: int, y: int) -> None:
        params = self._get_params([win_id, x, y])
        cmd = self._builder.build("Move", params)
        subprocess.run(cmd)

    def _get_params(self, params: List) -> List:
        negative = False
        for p in params:
            if type(p) == int and p < 0:
                negative = True
                break
        if negative:
            return ["~~"] + params
        return params

    def resize(self, win_id: int, width: int, height: int) -> None:
        cmd = self._builder.build("Resize", [win_id, width, height])
        subprocess.run(cmd)

    def move_resize(self, win_id: int, x: int, y: int, width: int, height: int) -> None:
        params = self._get_params([win_id, x, y, width, height])
        cmd = self._builder.build("MoveResize", params)
        subprocess.run(cmd)

    def move_to_workspace(self, win_id: int, workspace_id: int) -> None:
        cmd = self._builder.build("MoveToWorkspace", [win_id, workspace_id])
        subprocess.run(cmd)

    def activate(self, win_id: int) -> None:
        cmd = self._builder.build("Activate", [win_id])
        subprocess.run(cmd)

    def close(self, win_id: int) -> None:
        cmd = self._builder.build("Close", [win_id])
        subprocess.run(cmd)


class CMD_Builder:

    def __init__(self):
        self._base = [
            "gdbus",
            "call",
            "-e",
            "-d",
            "org.gnome.Shell",
            "-o",
            "/org/gnome/Shell/Extensions/Windows",
            "--method",
        ]
        self._method_location = "org.gnome.Shell.Extensions.Windows"

    def build(self, method: str, params: List = []) -> List[str]:
        return [
            *self._base,
            f"{self._method_location}.{method}",
            *[str(p) for p in params],
        ]
