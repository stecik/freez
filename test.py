from Freez import WinManager
import subprocess

win_man = WinManager()

win_man.list()

# pid = 4978
# cmd = ["readlink", "-f", f"/proc/{pid}/exe"]
# res = subprocess.run(cmd, stdout=subprocess.PIPE)
# res = res.stdout.decode("utf-8").strip()
# print(res)

# cmd = f"{res} --profile-directory=Default --app-id=cadlkienfkclaiaibeoongdcgmdikeeg"
# cmd = f"{res} --profile-directory=Default --app-id=icphmklmjgmdofbbjohdmnhaffbaafbl"
# cmd = f"{res} --new-window"
# subprocess.Popen(
#     [cmd], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
# )
