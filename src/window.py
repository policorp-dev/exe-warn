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
import gettext
from gi.repository import Adw, Gtk
APPNAME = "exe-warn"
gettext.bindtextdomain(APPNAME, "/usr/share/locale")
gettext.textdomain(APPNAME)
_ = gettext.gettext

@Gtk.Template(resource_path="/org/gnome/ExeWarn/window.ui")
class ExeWarnWindow(Adw.ApplicationWindow):
    __gtype_name__ = "ExeWarnWindow"

    subtitle_label = Gtk.Template.Child()
    message_label = Gtk.Template.Child()
    wine_button = Gtk.Template.Child()
    native_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = self.get_application()
        if getattr(app, "file_arg", None):
            # --- ESTADO COM FICHEIRO SELECIONADO ---
            filepath = app.file_arg
            filename = filepath.split("/")[-1]

            # Tenta extrair um nome de aplicativo mais limpo
            app_name_match = re.match(r"(\w+?)(installer|setup)?\.exe", filename, re.IGNORECASE)
            app_name = app_name_match.group(1).capitalize() if app_name_match else _("This app")

            # Define o título da janela (nomes de ficheiros não são traduzidos)
            self.set_title(filename)

            # --- NOVO PADRÃO: PEGAR, FORMATAR, DEFINIR ---

            # Atualiza o subtítulo
            original_subtitle = self.subtitle_label.get_label()
            self.subtitle_label.set_label(original_subtitle.format(app_name=app_name))

            # Atualiza a mensagem principal
            original_message = self.message_label.get_label()
            self.message_label.set_label(original_message.format(filename=filename))

            # Atualiza o texto do botão de instalação nativo
            original_button_text = self.native_button.get_label()
            self.native_button.set_label(original_button_text.format(app_name=app_name))
        else:
            # --- ESTADO SEM FICHEIRO SELECIONADO ---
            # Para este estado, continuamos a definir os textos diretamente, pois são simples.
            self.set_title(_("No file selected"))
            self.subtitle_label.set_label(_("Open a .exe file to continue"))
            self.message_label.set_text("")
            self.native_button.set_visible(False)
            self.wine_button.set_visible(False)

    @Gtk.Template.Callback()
    def on_close_clicked(self, button):
        self.close()

    @Gtk.Template.Callback()
    def on_wine_clicked(self, button):
        print("WINDOWS")
        # subprocess.Popen(["flatpak", "install", "-y", "flathub", "org.winehq.Wine"])

    @Gtk.Template.Callback()
    def on_native_clicked(self, button):
        print("INSTALL")
        # subprocess.Popen(["gnome-software", ""])

