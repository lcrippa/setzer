#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

try:
    gi.require_version('Spelling', '1')
    from gi.repository import Spelling
except (ValueError, ImportError):
    Spelling = None

from setzer.app.service_locator import ServiceLocator


def is_available():
    return Spelling != None

def get_languages():
    ''' Return a list of (code, name) tuples for all available dictionaries. '''

    if Spelling == None: return []
    provider = Spelling.Provider.get_default()
    if provider == None: return []

    languages = provider.list_languages()
    result = [(languages.get_item(i).get_code(), languages.get_item(i).get_name()) for i in range(languages.get_n_items())]
    return sorted(result, key=lambda language: language[1])


class Spellchecking(object):
    ''' Spellchecking for LaTeX documents (libspelling), optional dependency. '''

    def __init__(self, document):
        self.document = document
        self.settings = ServiceLocator.get_settings()
        self.adapter = None

        if Spelling == None or not document.is_latex_document(): return

        self.set_language(self.settings.get_value('preferences', 'spelling_language'))
        self.adapter = Spelling.TextBufferAdapter.new(document.source_buffer, Spelling.Checker.get_default())
        self.adapter.set_enabled(self.settings.get_value('preferences', 'enable_spellchecking'))

        self.settings.connect('settings_changed', self.on_settings_changed)

    def close(self):
        if self.adapter != None:
            self.adapter.set_enabled(False)
            self.adapter = None

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if self.adapter == None: return
        if (section, item) == ('preferences', 'enable_spellchecking'):
            self.adapter.set_enabled(value)
        if (section, item) == ('preferences', 'spelling_language'):
            self.set_language(value)

    def set_language(self, code):
        if code == '':
            provider = Spelling.Provider.get_default()
            if provider == None: return
            code = provider.get_default_code()
        Spelling.Checker.get_default().set_language(code)

    def is_active(self):
        return self.adapter != None and self.adapter.get_enabled()

    def update_at_position(self, x, y):
        ''' Move cursor to (x, y) in the source view, return True if the word there is misspelled. '''

        buffer = self.document.source_buffer
        if buffer.get_has_selection(): return False

        view = self.document.source_view
        buffer_x, buffer_y = view.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, int(x), int(y))
        found, location = view.get_iter_at_location(buffer_x, buffer_y)
        if not found: return False

        buffer.place_cursor(location)
        self.adapter.update_corrections()
        return self.adapter.get_action_enabled('add')

    def get_corrections(self):
        section = self.adapter.get_menu_model().get_item_link(0, 'section')
        return [section.get_item_attribute_value(i, 'label', None).get_string() for i in range(section.get_n_items())]

    def correct(self, word):
        self.adapter.activate_action('correct', GLib.Variant('s', word))

    def add_word(self):
        self.adapter.activate_action('add', None)

    def ignore_word(self):
        self.adapter.activate_action('ignore', None)


