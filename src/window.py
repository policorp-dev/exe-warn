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
from gi.repository import Adw, Gtk, Gio
from .config import APPNAME, PKGDATADIR, VERSION
import gettext
gettext.bindtextdomain(APPNAME, "/usr/share/locale")
gettext.textdomain(APPNAME)
_ = gettext.gettext
caminho_do_policorp_store = "/usr/share/policorp-linux-store/policorp-linux-store"

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

    matched_rule = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = self.get_application()
        if getattr(app, "file_arg", None):
            filepath = app.file_arg
            filename = filepath.split("/")[-1]
            self.set_title(filename)

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
            if self.matched_rule:
                app_name = self.matched_rule.get('alternative', {}).get('name', self.matched_rule.get('name', _("App")))

                if 'flatpak' in self.matched_rule:
                    original_subtitle_flatpak = self.subtitle_label_flatpak.get_label()
                    self.subtitle_label_flatpak.set_label(original_subtitle_flatpak.format( filename=filename, app_name=app_name))
                    self.subtitle_label_flatpak.set_visible(True)
                elif 'webLink' in self.matched_rule:
                    original_subtitle_webLink = self.subtitle_label_webLink.get_label()
                    self.subtitle_label_webLink.set_label(original_subtitle_webLink.format( filename=filename, app_name=app_name))
                    self.subtitle_label_webLink.set_visible(True)

                #main_message = self.matched_rule.get('mainMessage')
                original_message = self.message_label.get_label()
                self.message_label.set_label(original_message.format(filename=filename))

                original_button_text = self.native_button.get_label()
                self.native_button.set_label(original_button_text.format(app_name=app_name))

                self.native_button.set_visible(True)
                self.wine_button.set_visible(True)
                is_clickable = any(key in self.matched_rule for key in ['flatpak', 'webLink'])
                self.native_button.set_sensitive(is_clickable)
                if not is_clickable:
                    self.wine_button.remove_css_class('flat')
                    self.wine_button.add_css_class('suggested-action')

            else:
                original_subtitle_unknown = self.subtitle_label_unknown.get_label()
                self.subtitle_label_unknown.set_label(original_subtitle_unknown.format( filename=filename))
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
        # subprocess.Popen(["flatpak", "install", "-y", "flathub", "org.winehq.Wine"])

    @Gtk.Template.Callback()
    def on_native_clicked(self, button):
        if not self.matched_rule:
            return

        if 'flatpak' in self.matched_rule:
            flatpak_id = self.matched_rule['flatpak']['id']
            print(f"Installing Flatpak: {flatpak_id}")
            if flatpak_id == "org.libreoffice.LibreOffice":
                self.on_exec_policorp_store("OnlyOffice", flatpak_id)
                self.close()

            uri = f"appstream://{flatpak_id}"
            launcher = Gtk.UriLauncher.new(uri)
            launcher.launch(None, None, None)
            print(f"Pedido para abrir '{uri}' enviado via Gtk.UriLauncher.")
            #subprocess.Popen(["gnome-software", f"--details={flatpak_id}"])
            self.close()
        elif 'webLink' in self.matched_rule:
            url = self.matched_rule['webLink']['href']
            print(f"Opening web link: {url}")
            subprocess.Popen(["xdg-open", f"{url}"])
            self.close()
       # elif 'apt' in self.matched_rule:
       #     apt_pkg = self.matched_rule['apt']
       #     print(f"Opening Apt URL for: {apt_pkg}")
       #     uri = f"apt:{apt_pkg}"
       #     Gtk.show_uri(self.get_display(), uri, Gtk.get_current_event_time())

    def on_exec_policorp_store(self, application, flatpak_id):
        if os.path.exists(caminho_do_policorp_store):
            comando = [caminho_do_policorp_store, "--application", application]
            subprocess.Popen(comando)
        else:
            uri = f"appstream://{flatpak_id}"
            launcher = Gtk.UriLauncher.new(uri)
            launcher.launch(None, None, None)
            print(f"Pedido para abrir '{uri}' enviado via Gtk.UriLauncher.")

