import subprocess
import os
from typing import List, Dict, Iterable, Callable
import json
from argparse import Namespace
from abc import ABC, abstractmethod
import curses
import time

from config import DATA_DIR, DATA_FILE, OVERWRITE, TIMEOUT, CLOSE_TERMINAL


class FreezABC(ABC):

    _devnull = {
        "stdout": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    def __init__(self):
        super().__init__()
        self.win_man: WinManager = WinManager()
        self._data_dir = DATA_DIR
        self._data_file = os.path.join(self._data_dir, DATA_FILE)

    def _check_dir(self):
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

    def _load_data(self) -> Dict:
        try:
            if not os.path.exists(self._data_file):
                return {}
            with open(self._data_file, "r") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            return {}
        except Exception as e:
            print(e)
            return {}

    def _list(self, data: Dict, _list: bool) -> bool:
        if _list:
            if data:
                for name in data:
                    print(name)
            else:
                print("No saved workspaces")
            return True
        return False

    def _delete(self, data: Dict, names: List[str]) -> bool:
        if names:
            for name in names:
                if name in data.keys():
                    del data[name]
            self._save_data(data)
            return True
        return False

    @abstractmethod
    def run(self, args: Namespace) -> None:
        pass


class Freez(FreezABC):

    def __init__(self):
        super().__init__()
        self._crs_man: CursesManager = CursesManager()
        self._exec_parser: ExecParser = ExecParser()

    def _save_data(self, data: Dict) -> None:
        try:
            with open(self._data_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(e)

    def run(self, args: Namespace) -> None:
        data = self._load_data()

        if self._list(data, args.list):
            return
        if self._delete(data, args.delete):
            return

        windows = self.win_man.get_windows()

        if args.name:

            if args.manage:
                windows = self._manage(windows)

            workspace = {args.name: dict()}
            cwd = os.getcwd()
            for idx, win in enumerate(windows):
                name = f"win{idx}"
                win_config = dict()

                cls = win["wm_class"]
                details = self.win_man.get_details(win["id"])
                pid = details["pid"]
                executable = self._exec_parser.get_exec(
                    pid, cls, win["wm_class_instance"]
                )
                size = (details["width"], details["height"])
                position = (details["x"], details["y"])

                win_config["size"] = size
                win_config["position"] = position
                win_config["executable"] = executable
                win_config["cwd"] = cwd
                win_config["extra_cmd"] = ""
                workspace[args.name][name] = win_config

            if not OVERWRITE:
                selected = [False]
                msg = f"'{args.name}' exists. Do you want to overwrite it?"
                self._crs_man.run(self._crs_man.confirm_menu, msg, selected)
                if selected[0]:
                    data.update(workspace)
                    self._save_data(data)
            else:
                data.update(workspace)
                self._save_data(data)

        if self._close(windows, args.close):
            return

        if self._reboot(args.reboot):
            return

        if self._shutdown(args.shutdown):
            return

    def _close(self, windows: List[Dict], _close: bool) -> None:
        if _close:
            for win in windows:
                self.win_man.close(win["id"])
            return True
        return False

    def _reboot(self, _reboot: bool) -> None:
        if _reboot:
            subprocess.run(["reboot"])
            return True
        return False

    def _shutdown(self, _shutdown: bool) -> None:
        if _shutdown:
            subprocess.run(["shutdown", "now", "-h"])
            return True
        return False

    def _manage(self, windows: List[Dict]) -> List:
        selected = [True] * len(windows)
        items = [win["title"] for win in windows]
        self._crs_man.run(self._crs_man.menu_select, items, selected)
        return [win for win, sel in zip(windows, selected) if sel]


class ExecParser:

    def get_exec(self, pid: int, wm_cls: str, wm_inst: str) -> str:
        cmd = ["readlink", "-f", f"/proc/{pid}/exe"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE)
        res = res.stdout.decode("utf-8").strip()
        if "snap" in res:
            return self._snap(res)
        elif wm_cls == "Google-chrome":
            return self._chrome(res, wm_inst)
        elif wm_cls == "org.gnome.Terminal":
            return "gnome-terminal"
        return res

    def _snap(self, res: str) -> str:
        # handles snap apps
        res = res.split(os.path.sep)
        return res[-1]

    def _chrome(self, res: str, wm_inst: str) -> str:
        if wm_inst == "google-chrome":
            # handles regular chrome windows
            return f"{wm_inst} --new-window"
        elif "_" in wm_inst:
            # handles chrome installed apps
            app_id = wm_inst.split("_")[-1]
            return f"google-chrome --profile-directory=Default --app-id={app_id}"
        return res

    def _flatpak(self, res: str) -> str:
        pass


class Ufreez(FreezABC):

    def run(self, args: Namespace) -> None:
        data = self._load_data()

        if self._list(data, args.list):
            return

        if self._delete(data, args.delete):
            return

        terminal_id = self._get_init_terminal_id()
        workspace = data.get(args.name)
        if workspace:
            for win, config in workspace.items():
                size = config["size"]
                position = config["position"]
                executable = config["executable"]
                extra_cmd = config["extra_cmd"]
                cwd = config["cwd"]
                self._run_window(executable, cwd, position, size, extra_cmd)
        if CLOSE_TERMINAL and terminal_id:
            self.win_man.close(terminal_id)

    def _run_window(
        self, executable: str, cwd: str, position: tuple, size: tuple, extra_cmd: str
    ) -> None:
        windows = self.win_man.get_windows()
        subprocess.Popen(
            executable.split() + extra_cmd.split(),
            cwd=cwd,
            **self._devnull,
            preexec_fn=os.setsid,
        )
        win_id = self._get_id(windows)
        if win_id:
            self.win_man.move_resize(win_id, *position, *size)

    def _get_id(self, windows: List[Dict]) -> int:
        start = time.time()
        win_id = None
        while not win_id and time.time() - start < TIMEOUT:
            new_windows = self.win_man.get_windows()
            if len(new_windows) != len(windows):
                win_id = self._get_new_id(windows, new_windows)
            else:
                time.sleep(0.1)
        return win_id

    def _get_new_id(self, old: List[Dict], new: List[Dict]) -> int:
        old_ids = [win["id"] for win in old]
        new_ids = [win["id"] for win in new]
        diff = list(set(new_ids) - set(old_ids))
        if diff:
            return diff[0]
        return None

    def _get_init_terminal_id(self) -> int:
        windows = self.win_man.get_windows()
        for win in windows:
            if win["wm_class"] == "org.gnome.Terminal":
                return win["id"]
        return None


class WinManager:

    _devnull = {
        "stdout": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    def __init__(self):
        self._builder: CMD_Builder = CMD_Builder()

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
        subprocess.run(cmd, **self._devnull)

    def unminimize(self, win_id: int) -> None:
        cmd = self._builder.build("Unminimize", [win_id])
        subprocess.run(cmd, **self._devnull)

    def maximize(self, win_id: int) -> None:
        cmd = self._builder.build("Maximize", [win_id])
        subprocess.run(cmd, **self._devnull)

    def unmaximize(self, win_id: int) -> None:
        cmd = self._builder.build("Unmaximize", [win_id])
        subprocess.run(cmd, **self._devnull)

    def move(self, win_id: int, x: int, y: int) -> None:
        params = self._get_params([win_id, x, y])
        cmd = self._builder.build("Move", params)
        subprocess.run(cmd, **self._devnull)

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
        subprocess.run(cmd, **self._devnull)

    def move_resize(self, win_id: int, x: int, y: int, width: int, height: int) -> None:
        params = self._get_params([win_id, x, y, width, height])
        cmd = self._builder.build("MoveResize", params)
        subprocess.run(cmd, **self._devnull)

    def move_to_workspace(self, win_id: int, workspace_id: int) -> None:
        cmd = self._builder.build("MoveToWorkspace", [win_id, workspace_id])
        subprocess.run(cmd, **self._devnull)

    def activate(self, win_id: int) -> None:
        cmd = self._builder.build("Activate", [win_id])
        subprocess.run(cmd, **self._devnull)

    def close(self, win_id: int) -> None:
        cmd = self._builder.build("Close", [win_id])
        subprocess.run(cmd, **self._devnull)


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


class CursesManager:

    def confirm_menu(self, stdscr, message, selected):
        lines, cols = curses.LINES, curses.COLS
        curses.use_default_colors()
        curses.curs_set(0)
        options = ["Yes", "No"]
        option = True
        max_len = len(message)
        h = 6
        w = max_len
        y = lines // 2 - h // 2
        x = cols // 2 - w // 2
        win = curses.newwin(h, w, y, x)
        win.keypad(1)

        while True:
            win.clear()
            win.addstr(0, 0, message)
            win.addstr(
                4, max_len // 2 - 4, options[0], curses.A_REVERSE if option else 0
            )
            win.addstr(
                4, max_len // 2 + 4, options[1], curses.A_REVERSE if not option else 0
            )

            key = win.getch()

            if key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                option = not option
            elif key == 10:  # ENTER key
                selected[0] = option
                break

    def menu_select(self, stdsrc, items, selected):
        lines, cols = curses.LINES, curses.COLS
        curses.use_default_colors()
        curses.curs_set(0)

        pointer = 0
        key_hint = "Select with SPACE, confirm with ENTER"
        max_len = max([len(item) for item in items] + [len(key_hint)]) + 10
        h = len(items) + 5
        w = max_len
        y = lines // 2 - h // 2
        x = cols // 2 - w // 2
        win = curses.newwin(h, w, y, x)
        win.keypad(1)

        while True:
            win.clear()
            win.addstr(0, 0, key_hint)

            for idx, item in enumerate(items):
                if idx == pointer:
                    win.addstr(
                        idx + 2,
                        2,
                        f"{'[x]' if selected[idx] else '[ ]'} {item}",
                        curses.A_REVERSE,
                    )
                else:
                    win.addstr(
                        idx + 2,
                        2,
                        f"{'[x]' if selected[idx] else '[ ]'} {item}",
                    )

            key = win.getch()

            if key == curses.KEY_UP:
                if pointer > 0:
                    pointer -= 1
                else:
                    pointer = len(items) - 1
            elif key == curses.KEY_DOWN:
                if pointer < len(items) - 1:
                    pointer += 1
                else:
                    pointer = 0
            elif key == ord(" "):
                selected[pointer] = not selected[pointer]
            elif key == 10:  # ENTER key
                break

    def run(self, func: Callable, *args, **kwargs):
        curses.wrapper(func, *args, **kwargs)
