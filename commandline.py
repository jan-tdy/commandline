# jadivcommandline: Supermoderny Python CLI nástroj v shell štýle (bez GUI)
# Autor: Janík + ChatGPT (terminálová verzia)

import os
import sys
import subprocess
import urllib.request
import psutil
import shutil
import datetime
import webbrowser
import socket
import platform
import getpass
import random
import string

class JadivCommandline:
    def __init__(self):
        self.history = []
        self.commands = {
            "apps": self.cmd_apps,
            "apps_full": self.cmd_apps_full,
            "run_py": self.cmd_run_py,
            "run_sh": self.cmd_run_sh,
            "apt_update": self.cmd_apt_update,
            "apt_upgrade": self.cmd_apt_upgrade,
            "apt_install": self.cmd_apt_install,
            "cmd": self.cmd_custom,
            "status": self.cmd_status,
            "log": self.cmd_log,
            "edit": self.cmd_edit,
            "help": self.cmd_help,
            "calc": self.cmd_calc,
            "set": self.cmd_set,
            "greet": lambda args: print("Ahoj! Vitaj v jadivcommandline."),
            "random_number": lambda args: print(f"Náhodné číslo: {random.randint(1, 100)}"),
            "today": lambda args: print(f"Dnes je: {datetime.datetime.now().strftime('%A, %d. %B %Y')}"),
            "clear": lambda args: os.system('clear'),
            "say": lambda args: print("Použitie: say <text>") if not args else print(" ".join(args)),
            "double": lambda args: print("Použitie: double <číslo>") if not args or not args[0].isdigit() else print(f"{args[0]} × 2 = {int(args[0]) * 2}"),
            "whoami": lambda args: print(f"Používateľ: {getpass.getuser()}"),
            "hostname": lambda args: print(f"Hostname: {socket.gethostname()}"),
            "diskfree": lambda args: print(f"Voľné miesto: {shutil.disk_usage('/').free // (1024**2)} MB"),
            "cipher": self.cmd_cipher,
            "screenshot": self.cmd_screenshot,
            "osinfo": self.cmd_osinfo,
            "uptime": self.cmd_uptime,
            "reboot": self.cmd_reboot,
            "shutdown": self.cmd_shutdown
        }

    def cmd_apps(self, args):
        if not args:
            print("Použitie: apps <nazov_repo>")
            return
        repo = args[0]
        url = f"https://github.com/jan-tdy/{repo}/archive/refs/heads/main.zip"
        print(f"Sťahujem: {url}")
        subprocess.run(["wget", url, "-O", f"{repo}.zip"])

    def cmd_apps_full(self, args):
        if not args:
            print("Použitie: apps_full <celá_adresa_repo>")
            return
        url = args[0]
        print(f"Sťahujem: {url}")
        subprocess.run(["wget", url, "-O", "repo.zip"])

    def cmd_run_py(self, args):
        if not args:
            print("Použitie: run_py <subor.py>")
            return
        subprocess.run(["python3", args[0]])

    def cmd_run_sh(self, args):
        if not args:
            print("Použitie: run_sh <skript.sh>")
            return
        subprocess.run(["bash", args[0]])

    def cmd_apt_update(self, args):
        subprocess.run(["sudo", "apt", "update"])

    def cmd_apt_upgrade(self, args):
        subprocess.run(["sudo", "apt", "upgrade", "-y"])

    def cmd_apt_install(self, args):
        if not args:
            print("Použitie: apt_install <balík>")
            return
        subprocess.run(["sudo", "apt", "install", args[0], "-y"])

    def cmd_custom(self, args):
        if not args:
            print("Použitie: cmd <príkaz>")
            return
        subprocess.run(args)

    def cmd_status(self, args):
        print("Stav systému:")
        print(f"Uptime: {datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())}")
        print(f"CPU Temp: {self.get_cpu_temp()}°C")
        print(f"Disk voľný: {shutil.disk_usage('/').free // (1024 ** 2)} MB")

    def cmd_log(self, args):
        print("História príkazov:")
        for i, cmd in enumerate(self.history[-10:], start=1):
            print(f"{i}: {cmd}")

    def cmd_edit(self, args):
        print("Editor zatiaľ nie je implementovaný.")

    def cmd_help(self, args):
        print("Dostupné príkazy:")
        for cmd in sorted(self.commands):
            print(f"- {cmd}")

    def cmd_calc(self, args):
        try:
            result = eval(" ".join(args))
            print(f"Výsledok: {result}")
        except:
            print("Chybný výraz")

    def cmd_set(self, args):
        print("Táto verzia zatiaľ nepodporuje nastavenia.")

    def cmd_cipher(self, args):
        if not args or args[0] not in ["encrypt", "decrypt"]:
            print("Použitie: cipher encrypt <text> | cipher decrypt <zakodovany_text> <kod>")
            return

        if args[0] == "encrypt":
            if len(args) < 2:
                print("Chyba: Zadaj text na šifrovanie")
                return
            text = " ".join(args[1:])
            pin = ''.join(random.choices(string.digits, k=4))
            encrypt_char = "*"
            spaced_text = encrypt_char.join(text)
            binary_text = ''.join(format(ord(c), '08b') for c in spaced_text)
            reversed_binary = binary_text[::-1]
            encoded_text = reversed_binary + ''.join(format(ord(d), '08b') for d in pin)
            decrypt_code = f'{encrypt_char}{pin}'
            print("Zašifrované:", encoded_text)
            print("Kód na dešifrovanie:", decrypt_code)

        elif args[0] == "decrypt":
            if len(args) < 3:
                print("Chyba: Zadaj zašifrovaný text a kód")
                return
            encrypted_text = args[1]
            decrypt_code = args[2]
            encrypt_char = decrypt_code[0]
            pin = decrypt_code[1:]
            binary_text = encrypted_text[:-32]
            original_binary = binary_text[::-1]
            text_chars = [chr(int(original_binary[i:i+8], 2)) for i in range(0, len(original_binary), 8)]
            original_text = ''.join(text_chars).replace(encrypt_char, '')
            print("Dešifrované:", original_text)

    def cmd_screenshot(self, args):
        print("Snímka obrazovky sa vytvára...")
        subprocess.run(["scrot", "screenshot.png"])
        print("Uložené ako screenshot.png")

    def cmd_osinfo(self, args):
        print("OS Info:")
        print(platform.platform())

    def cmd_uptime(self, args):
        print("Uptime:")
        print(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()))

    def cmd_reboot(self, args):
        print("Reštartujem systém...")
        subprocess.run(["sudo", "reboot"])

    def cmd_shutdown(self, args):
        print("Vypínam systém...")
        subprocess.run(["sudo", "shutdown", "now"])

    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return round(int(f.read()) / 1000, 1)
        except:
            return "N/A"

    def repl(self):
        while True:
            try:
                command_line = input("jadiv> ").strip()
                if not command_line:
                    continue
                self.history.append(command_line)
                parts = command_line.split()
                cmd = parts[0]
                args = parts[1:]

                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"Neznámy príkaz: {cmd}")
            except (KeyboardInterrupt, EOFError):
                print("\nUkončujem jadivcommandline.")
                break

if __name__ == "__main__":
    JadivCommandline().repl()
