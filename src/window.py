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

@Gtk.Template(resource_path="/org/gnome/ExeWarn/window.ui")
class ExeWarnWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ExeWarnWindow"

    subtitle_label: Gtk.Label = Gtk.Template.Child()
    message_label: Gtk.Label = Gtk.Template.Child()
    wine_button: Gtk.Button = Gtk.Template.Child()
    native_button: Gtk.Button = Gtk.Template.Child()

    matched_rule = None # Variável para guardar a regra encontrada

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

            # Procura por uma correspondência na base de dados
            self.matched_rule = None
            for rule in apps_db:
                if 'regex' in rule and 'windows' in rule['regex']:
                    pattern = rule['regex']['windows']
                    if re.search(pattern, filename, re.IGNORECASE):
                        self.matched_rule = rule
                        break

            if self.matched_rule:
                app_name = self.matched_rule.get('alternative', {}).get('name', self.matched_rule.get('name', _("App")))

                original_subtitle = self.subtitle_label.get_label()
                self.subtitle_label.set_label(original_subtitle.format( filename=filename, app_name=app_name))

                main_message = self.matched_rule.get('mainMessage')
                #if main_message:
                 #   self.message_label.set_label(_(main_message))
                #else:
                original_message = self.message_label.get_label()
                self.message_label.set_label(original_message.format(filename=filename))

                original_button_text = self.native_button.get_label()
                self.native_button.set_label(original_button_text.format(app_name=app_name))

                self.native_button.set_visible(True)
                self.wine_button.set_visible(True)
                #is_actionable = any(key in self.matched_rule for key in ['flatpak', 'apt', 'webLink'])
                is_clickable = 'flatpak' in self.matched_rule
                self.native_button.set_sensitive(is_clickable)

            else:
                self.subtitle_label.set_label(_("Unknown Windows application"))
                self.message_label.set_label(_("Running this application is not recommended as its origin is unknown and it may pose a security risk."))
                self.native_button.set_visible(False)
                self.wine_button.set_visible(True)
        else:
            self.set_title(_("No file selected"))
            self.subtitle_label.set_label(_("Open a .exe file to continue"))
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
            subprocess.Popen(["gnome-software", f"--details={flatpak_id}"])
       # elif 'apt' in self.matched_rule:
       #     apt_pkg = self.matched_rule['apt']
       #     print(f"Opening Apt URL for: {apt_pkg}")
       #     uri = f"apt:{apt_pkg}"
       #     Gtk.show_uri(self.get_display(), uri, Gtk.get_current_event_time())
       # elif 'webLink' in self.matched_rule:
       #     url = self.matched_rule['webLink']['href']
       #     print(f"Opening web link: {url}")
       #     Gtk.show_uri(self.get_display(), url, Gtk.get_current_event_time())

