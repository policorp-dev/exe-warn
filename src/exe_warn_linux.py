 #!/usr/bin/python3

import sys

import os

import stat

from gi.repository import Gio, GLib


class ExecGuardApplicationLinux:

    def __init__(self, parent_window=None):

        self.parent_window = parent_window


    def execute(self, filepath):

        if not os.path.exists(filepath):

            print(f"Erro: Arquivo não encontrado: {filepath}")

            return False


        try:

            st = os.stat(filepath)

            os.chmod(filepath, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            return self.spawn_process([filepath])

        except Exception as e:

            print(f"Erro ao preparar execução: {e}")

            return False


    def spawn_process(self, args):

        try:
            print(f"Iniciando processo: {args}")

            proc = Gio.Subprocess.new(args, Gio.SubprocessFlags.NONE)

            return True

        except Exception as e:

            print(f"Erro ao executar subprocesso: {e}")

            return False
