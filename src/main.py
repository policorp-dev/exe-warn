# main.py
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

import sys
import gi
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import ExeWarnWindow


class ExeWarnApplication(Adw.Application):

    def __init__(self):
        super().__init__(application_id='org.gnome.ExeWarn',
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         resource_base_path='/org/gnome/ExeWarn')
        self.file_arg = None
        self.file_path = None
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_open(self, files, n_files, hint):
        if n_files > 0:
            gfile = files[0]
            self.file_path = gfile.get_path()
            self.file_arg = gfile.get_basename()

        self.do_activate()

    def do_command_line(self, command_line):
        args = command_line.get_arguments()

        if len(args) > 1:
            raw_filename = args[1]
            self.file_arg = raw_filename

            cwd = command_line.get_cwd()

            if cwd and not os.path.isabs(raw_filename):
                full_path = os.path.join(cwd, raw_filename)
                self.file_path = os.path.abspath(full_path)
            else:
                self.file_path = os.path.abspath(raw_filename)

            print(f"Arg: {self.file_arg}")
            print(f"Path Absoluto: {self.file_path}")

        self.activate()
        return 0

    def do_activate(self):
        win = ExeWarnWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(application_name='exe-warn',
                                  application_icon='org.gnome.ExeWarn',
                                  developer_name='Policorp',
                                  version='0.1.0',
                                  developers=['Policorp'],
                                  copyright='© 2025 Policorp')
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    app = ExeWarnApplication()
    return app.run(sys.argv)
