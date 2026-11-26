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
gi.require_version('Adw', '1')
from gi.repository import Adw

from setzer.app.service_locator import ServiceLocator


class ThemeManager():
    ''' Follows the system light/dark preference. '''

    def init():
        settings = ServiceLocator.get_settings()
        settings.connect('settings_changed', ThemeManager.on_settings_changed)
        Adw.StyleManager.get_default().connect('notify::dark', ThemeManager.on_system_dark_changed)
        ThemeManager.update_adw_color_scheme()

    def on_settings_changed(settings, parameter):
        section, item, value = parameter

        if item == 'follow_system_theme':
            ThemeManager.update_adw_color_scheme()
            ThemeManager.notify_scheme_changed()
        elif item == 'invert_pdf_in_dark_mode':
            ThemeManager.notify_scheme_changed()

    def on_system_dark_changed(style_manager, parameter):
        if ThemeManager.follows_system():
            ThemeManager.notify_scheme_changed()

    def notify_scheme_changed():
        # re-emit so that editor, css, help and preview refresh themselves
        settings = ServiceLocator.get_settings()
        settings.add_change_code('settings_changed', ('preferences', 'color_scheme', ThemeManager.get_color_scheme_name()))

    def update_adw_color_scheme():
        if ThemeManager.follows_system():
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.DEFAULT)
        else:
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

    def follows_system():
        return ServiceLocator.get_settings().get_value('preferences', 'follow_system_theme')

    def is_dark():
        return ThemeManager.follows_system() and Adw.StyleManager.get_default().get_dark()

    def get_color_scheme_name():
        settings = ServiceLocator.get_settings()
        if ThemeManager.follows_system():
            return 'default-dark' if ThemeManager.is_dark() else 'default'
        return settings.get_value('preferences', 'color_scheme')

    def invert_pdf(recolor_pdf=False):
        ''' Invert pdf colors in dark mode, unless the pdf is already
            recolored to match the theme. '''

        if recolor_pdf: return False
        settings = ServiceLocator.get_settings()
        return ThemeManager.is_dark() and settings.get_value('preferences', 'invert_pdf_in_dark_mode')


