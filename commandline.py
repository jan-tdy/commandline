# jadivcommandline: Supermoderny Python GUI CLI nastroj
# Autor: Janík + ChatGPT

import os
import sys
import subprocess
import threading
import urllib.request
import customtkinter as ctk
import psutil
import shutil
import datetime
import webbrowser
import socket
import platform
import getpass

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class JadivCommandlineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JadivCommandline")
        self.geometry("1000x700")
        self.configure(fg_color=("#101820", "#101820"))

        self.command_entry = ctk.CTkEntry(self, placeholder_text="Zadaj príkaz...", text_color="white")
        self.command_entry.pack(padx=20, pady=(20, 10), fill="x")
        self.command_entry.bind("<Return>", self.execute_command)

        self.status_frame = ctk.CTkLabel(self, text="", justify="left", text_color="lightgreen")
        self.status_frame.pack(padx=20, pady=(0, 10), fill="x")

        self.log_text = ctk.CTkTextbox(self, text_color="white")
        self.log_text.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        self.commands = {
            "apps": self.cmd_apps,
            "apps_full": self.cmd_apps_full,
            "run_py": self.cmd_run_py,
            "run_sh": self.cmd_run_sh,
            "run_scratch": self.cmd_run_scratch,
            "apt_update": self.cmd_apt_update,
            "apt_upgrade": self.cmd_apt_upgrade,
            "apt_install": self.cmd_apt_install,
            "cmd": self.cmd_custom,
            "status": self.cmd_status,
            "open": self.cmd_open,
            "log": self.cmd_log,
            "edit": self.cmd_edit,
            "screenshot": self.cmd_screenshot,
            "chat": self.cmd_chat,
            "time": self.cmd_time,
            "ip": self.cmd_ip,
            "browser": self.cmd_browser,
            "user": self.cmd_user,
            "osinfo": self.cmd_osinfo,
            "help": self.cmd_help,
            "update-commandline": self.update_commandline
        }

        for i in range(1, 201):
            cmd_name = f"func{i:03d}"
            self.commands[cmd_name] = self.generate_dummy_function(cmd_name)

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def execute_command(self, event=None):
        command_text = self.command_entry.get().strip()
        self.command_entry.delete(0, "end")
        if not command_text:
            return
        self.log(f"> {command_text}")
        parts = command_text.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "apps" and args:
            if args[0] == "full":
                self.cmd_apps_full(args[1:])
            else:
                self.cmd_apps(args)
        elif cmd == "run" and len(args) >= 2:
            subtype = args[0]
            if subtype == "py":
                self.cmd_run_py(args[1:])
            elif subtype == "sh":
                self.cmd_run_sh(args[1:])
            elif subtype == "scratch":
                self.cmd_run_scratch(args[1:])
            else:
                self.log("Nepodporovaný typ run príkazu.")
        elif cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.log(f"Chyba pri vykonávaní príkazu '{cmd}': {e}")
        else:
            self.log("Neznámy príkaz. Napíš 'help' pre zoznam príkazov.")

    def cmd_help(self, args):
        self.log("Dostupné príkazy:")
        for cmd in sorted(self.commands.keys()):
            self.log(f" - {cmd}")

    def cmd_apps(self, args):
        if len(args) < 1:
            self.log("Použitie: apps <nazov_repo>")
            return
        repo = args[0]
        url = f"https://github.com/jan-tdy/{repo}.git"
        self.log(f"Stiahnutie repozitára: {url}")
        self.run_subprocess(["git", "clone", url])

    def cmd_apps_full(self, args):
        if len(args) < 1:
            self.log("Použitie: apps full <git_url>")
            return
        url = args[0]
        self.log(f"Stiahnutie repozitára: {url}")
        self.run_subprocess(["git", "clone", url])

    def cmd_run_py(self, args):
        if len(args) < 1:
            self.log("Použitie: run py <script.py>")
            return
        self.run_subprocess([sys.executable, args[0]])

    def cmd_run_sh(self, args):
        if len(args) < 1:
            self.log("Použitie: run sh <script.sh>")
            return
        self.run_subprocess(["bash", args[0]])

    def cmd_run_scratch(self, args):
        if len(args) < 1:
            self.log("Použitie: run scratch <project.sb3>")
            return
        scratch_app = shutil.which("scratch-desktop") or shutil.which("TurboWarp")
        if not scratch_app:
            self.log("Scratch3 aplikácia nebola nájdená. Nainštaluj ju ako 'scratch-desktop' alebo 'TurboWarp'.")
            return
        self.run_subprocess([scratch_app, args[0]])

    def cmd_apt_update(self, args):
        self.run_subprocess(["sudo", "apt", "update"])

    def cmd_apt_upgrade(self, args):
        self.run_subprocess(["sudo", "apt", "upgrade", "-y"])

    def cmd_apt_install(self, args):
        if len(args) < 1:
            self.log("Použitie: apt install <balik>")
            return
        self.run_subprocess(["sudo", "apt", "install", args[0], "-y"])

    def cmd_custom(self, args):
        self.log("Alias príkazy nie sú zatiaľ implementované.")

    def cmd_status(self, args):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        self.status_frame.configure(text=f"CPU: {cpu}%  |  RAM: {ram}%  |  Disk: {disk}%")
        self.log(f"CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%")

    def cmd_open(self, args):
        if not args:
            return
        self.run_subprocess([args[0]])

    def cmd_log(self, args):
        self.log("Zobrazenie logov priamo v aplikácii.")

    def cmd_edit(self, args):
        if not args:
            return
        editor = os.environ.get("EDITOR", "nano")
        self.run_subprocess([editor, args[0]])

    def cmd_screenshot(self, args):
        filename = "screenshot.png"
        try:
            import pyautogui
            pyautogui.screenshot(filename)
            self.log(f"Screenshot uložený ako {filename}")
        except Exception as e:
            self.log(f"Chyba pri screenshote: {e}")

    def cmd_chat(self, args):
        self.log("Ahoj! Som Jadiv asistent. Povedz niečo a uvidíme, čo s tým spravíme :) (táto funkcia sa rozšíri)")

    def cmd_time(self, args):
        now = datetime.datetime.now()
        self.log(f"Aktuálny čas: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    def cmd_ip(self, args):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        self.log(f"Hostname: {hostname} | IP adresa: {ip}")

    def cmd_browser(self, args):
        if not args:
            self.log("Použitie: browser <url>")
            return
        webbrowser.open(args[0])
        self.log(f"Otváram v prehliadači: {args[0]}")

    def cmd_user(self, args):
        user = getpass.getuser()
        self.log(f"Prihlásený používateľ: {user}")

    def cmd_osinfo(self, args):
        osname = platform.system()
        version = platform.version()
        release = platform.release()
        self.log(f"Operačný systém: {osname} {release} (verzia {version})")

    def update_commandline(self, args):
        self.log("Aktualizujem aplikáciu...")
        ota_url = "https://raw.githubusercontent.com/jan-tdy/commandline/master/commandline.py"
        try:
            response = urllib.request.urlopen(ota_url)
            code = response.read().decode("utf-8")
            current_file = os.path.realpath(__file__)
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(code)
            self.log("Aktualizácia dokončená, reštartujem...")
            self.restart_application()
        except Exception as e:
            self.log(f"Chyba pri aktualizácii: {e}")

    def restart_application(self):
        python = sys.executable
        os.execv(python, [python] + sys.argv)

    def run_subprocess(self, cmd_list):
        def run():
            try:
                process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for line in process.stdout:
                    self.log(line.strip())
                for line in process.stderr:
                    self.log(line.strip())
            except Exception as e:
                self.log(f"Chyba pri spúšťaní: {e}")
        threading.Thread(target=run).start()

    def generate_dummy_function(self, name):
        def dummy(args):
            self.log(f"Spustená funkcia: {name} s argumentmi: {args}")
        return dummy


if __name__ == "__main__":
    app = JadivCommandlineApp()
    app.mainloop()
