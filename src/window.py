# window.py
#
# Copyright 2025 lucas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# window.py
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import re
import json
import os
from gi.repository import Adw, Gtk, Gio, GLib

# --- Configuração para traduções e caminhos ---
from .config import APPNAME, PKGDATADIR, VERSION
import gettext
import webbrowser
from .exe_warn_linux import ExecGuardApplicationLinux

gettext.bindtextdomain(APPNAME, "/usr/share/locale")
gettext.textdomain(APPNAME)
_ = gettext.gettext
caminho_do_policorp_store = "/usr/share/policorp-linux-store/policorp-linux-store"
caminho_metadata = "/usr/share/policorp-linux-store/data/config/metadata.json"
# ----------------------------------------------------
globalfilepath = ''
globalfullfilepath = ''

@Gtk.Template(resource_path="/org/gnome/ExeWarn/window.ui")
class ExeWarnWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ExeWarnWindow"
    subtitle_label_flatpak: Gtk.Label = Gtk.Template.Child()
    subtitle_label_webLink: Gtk.Label = Gtk.Template.Child()
    subtitle_label_unknown: Gtk.Label = Gtk.Template.Child()
    subtitle_label: Gtk.Label = Gtk.Template.Child()
    message_label: Gtk.Label = Gtk.Template.Child()
    wine_button: Gtk.Button = Gtk.Template.Child()
    native_button: Gtk.Button = Gtk.Template.Child()
    #-----------------------------------------------
    subtitle_label_linux: Gtk.Label = Gtk.Template.Child()
    message_label_linux: Gtk.Label = Gtk.Template.Child()

    matched_rule = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = self.get_application()
        if getattr(app, "file_arg", None):
            filepath = app.file_arg
            file_path = app.file_path
            filename = filepath.split("/")[-1]
            self.set_title(filename)
            global globalfilepath, globalfullfilepath
            globalfilepath = filepath
            globalfullfilepath = file_path

            apps_db = []
            try:
                db_path = os.path.join(PKGDATADIR, 'apps.json')
                with open(db_path, 'r') as f:
                    apps_db = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Erro ao carregar apps.json: {e}")

            self.matched_rule = None
            for rule in apps_db:
                if 'regex' in rule and 'windows' in rule['regex']:
                    pattern = rule['regex']['windows']
                    if re.search(pattern, filename, re.IGNORECASE):
                        self.matched_rule = rule
                        break

            self.subtitle_label_flatpak.set_visible(False)
            self.subtitle_label_webLink.set_visible(False)
            self.subtitle_label_unknown.set_visible(False)
            self.subtitle_label.set_visible(False)

            self.subtitle_label_linux.set_visible(False)
            self.message_label_linux.set_visible(False)

            if self.matched_rule:
                app_name = self.matched_rule.get('alternative', {}).get('name', self.matched_rule.get('name', _("App")))
                original_app_name = self.matched_rule.get('name', filename)

                if 'flatpak' in self.matched_rule:
                    original_subtitle_flatpak = self.subtitle_label_flatpak.get_label()
                    self.subtitle_label_flatpak.set_label(original_subtitle_flatpak.format( filename=filename, app_name=app_name))
                    self.subtitle_label_flatpak.set_visible(True)
                elif 'webLink' in self.matched_rule:
                    original_subtitle_webLink = self.subtitle_label_webLink.get_label()
                    self.subtitle_label_webLink.set_label(original_subtitle_webLink.format( filename=filename, app_name=app_name))
                    self.subtitle_label_webLink.set_visible(True)

                original_message = self.message_label.get_label()
                self.message_label.set_label(original_message.format(filename=filename))

                original_button_text = self.native_button.get_label()
                self.native_button.set_label(original_button_text.format(app_name=app_name))
                self.native_button.set_visible(True)
                self.wine_button.set_visible(True)

                is_actionable = any(key in self.matched_rule for key in ['flatpak', 'webLink'])
                self.native_button.set_sensitive(is_actionable)

                if not is_actionable:
                    self.wine_button.add_css_class('destructive-action')
                else:
                    self.wine_button.remove_css_class('destructive-action')

            elif filepath.lower().endswith((".appimage", ".run", ".sh", ".bin")):
                self.execguardapplicationlinux = ExecGuardApplicationLinux()

                original_subtitle_linux = self.subtitle_label_linux.get_label()
                self.subtitle_label_linux.set_label(original_subtitle_linux.format(filename=filename))

                original_message_linux = self.message_label_linux.get_label()
                self.message_label_linux.set_label(original_message_linux.format(filename=filename))

                self.native_button.set_label('Continue')

                self.native_button.set_visible(True)
                self.wine_button.set_visible(True)
                self.subtitle_label_linux.set_visible(True)
                self.message_label_linux.set_visible(True)
            else:
                original_subtitle_unknown = self.subtitle_label_unknown.get_label()
                self.subtitle_label_unknown.set_label(original_subtitle_unknown.format(filename=filename))
                original_message_unknown = self.message_label.get_label()
                self.message_label.set_label(original_message_unknown.format(filename=filename))
                self.native_button.set_visible(False)
                self.wine_button.set_visible(True)
                self.subtitle_label_unknown.set_visible(True)

        else:
            self.set_title(_("No file selected"))
            self.subtitle_label.set_label(_("Open a .exe file to continue"))
            self.subtitle_label.set_visible(True)
            self.message_label.set_text("")
            self.native_button.set_visible(False)
            self.wine_button.set_visible(False)

    @Gtk.Template.Callback()
    def on_wine_clicked(self, button):
        self.close()

    @Gtk.Template.Callback()
    def on_native_clicked(self, button):
        global globalfilepath, globalfullfilepath
        filepath = globalfilepath
        full_file_path = globalfullfilepath
        if filepath.lower().endswith((".appimage", ".run", ".sh", ".bin")):
            print(f"Tentando executar Linux App: {full_file_path}")

            exec_guard = ExecGuardApplicationLinux(parent_window=self)
            sucesso = exec_guard.execute(full_file_path)

            if sucesso:
                print("Execução concluída com sucesso.")
                self.close()
            else:
                print("Falha ao executar o arquivo.")
                self._mostrar_erro("Não foi possível executar o arquivo.")

            return

        if not self.matched_rule:
            return

        if 'flatpak' in self.matched_rule:
            flatpak_id = self.matched_rule['flatpak']['id']

            if self.executar_app_do_metadata(flatpak_id):
                self.close()
                return

            if self._check_flathub_exists():
                uri = f"appstream://{flatpak_id}"
                launcher = Gtk.UriLauncher.new(uri)
                launcher.launch(None, None, None)
                self.close()
            else:
                app_name = self.matched_rule.get('alternative', {}).get('name', _("this app"))
                dialog = Adw.MessageDialog.new(self,
                    _("Add Application Repository?"),
                    (_("To install {app_name}, the main Flathub application repository needs to be added to your system.").format(app_name=app_name))
                )
                dialog.add_response("cancel", _("Cancel"))
                dialog.add_response("add_repo", _("Add Repository"))
                dialog.set_response_appearance("add_repo", Adw.ResponseAppearance.SUGGESTED)
                dialog.connect("response", self._on_add_repo_response)
                dialog.present()

        elif 'webLink' in self.matched_rule:
            url = self.matched_rule['webLink']['href']
            print(f"Opening web link: {url}")
            webbrowser.open(url)
            self.close()


    def _on_add_repo_response(self, dialog, response_id):
        dialog.close()
        if response_id == "add_repo":
            self._add_flathub_repo()
            info_dialog = Adw.MessageDialog.new(self, _("Repository Added"), _("The Flathub repository has been added. Please try the installation again."))
            info_dialog.add_response("ok", _("OK"))
            info_dialog.connect("response", lambda d, r: d.close())
            info_dialog.present()

    def executar_app_do_metadata(self, flatpak_id: str) -> bool:
        if not (os.path.exists(caminho_do_policorp_store) and os.path.exists(caminho_metadata)):
            return False
        try:
            with open(caminho_metadata, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            for package in metadata.get('packages', []):
                if package.get('exec') == flatpak_id:
                    application_name = package.get('name')
                    if application_name:
                        print(f"App '{application_name}' encontrado. Executando via Policorp Store...")
                        subprocess.Popen([caminho_do_policorp_store, "--application", application_name])
                        return True
        except (OSError, json.JSONDecodeError) as e:
            print(f"Erro ao processar o arquivo '{caminho_metadata}': {e}")
        return False

    def _check_flathub_exists(self):
        try:
            if not self.is_flatpak:
                result = subprocess.run(['flatpak', 'remotes'], check=True, capture_output=True, text=True)
                return 'flathub' in result.stdout
            else:
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _add_flathub_repo(self):
        try:
            subprocess.run(
                ['flatpak', 'remote-add', '--user', '--if-not-exists', 'flathub', 'https://flathub.org/repo/flathub.flatpakrepo'],
                check=True, capture_output=True, text=True
            )
            print("Repositório Flathub adicionado com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao adicionar o repositório Flathub: {e.stderr}")
        except FileNotFoundError:
            print("Erro: O comando 'flatpak' não foi encontrado.")

    @property
    def is_flatpak(self):
        """Verifica se o aplicativo está a ser executado como um Flatpak."""
        return os.path.exists('/.flatpak-info')

    def _mostrar_erro(self, mensagem):
        dialog = Adw.MessageDialog.new(
            self,
            "Erro ao executar",
            mensagem,
        )
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()
