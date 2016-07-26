# -*- coding: utf-8 -*-
#
# tw2.fontawesome.widgets - FontAwesome widgets
#
# Copyright © 2015 Nils Philippsen <nils@tiptoe.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals, print_function, absolute_import

import pkg_resources
pkg_resources.require("tw2.core >= 2.0")

from tw2.core.params import Param
from tw2.core import Widget
from tw2.core.core import request_local

genshi_tag = None
kajiki_literal = None

from .resources import fontawesome_resources
from .metadata import icons

__all__ = ('FontAwesomeIcon')


class FontAwesomeIcon(Widget):

    template = 'dummy'

    resources = fontawesome_resources

    icon = Param("The name of the icon")

    fixed_width = Param("Makes icons have a fixed width", default=False)

    allowed_scales = {'lg', '2x', '3x', '4x', '5x'}

    scale = Param(
            "Scale the icon (one of {scales}, or None (default))".format(
                scales=", ".join(repr(x) for x in allowed_scales)),
            default = None)

    tag = Param("Which tag to use for the icon", default='i')

    @staticmethod
    def _render_attrs(attrs):
        attrstrings = [""]
        for name, value in attrs.items():
            if not value:
                continue
            if '"' not in value:
                quote = '"'
            else:
                quote = "'"
                value = value.replace('"', "&quot;")
            attrstrings.append("{name}={quote}{value}{quote}".format(
                name=name, quote=quote, value=value))
        if len(attrstrings) > 1:
            return " ".join(attrstrings)
        else:
            return ""

    def generate_output(self, displays_on):
        global genshi_tag

        if not displays_on:
            mw = request_local().get('middleware')
            displays_on = self._get_default_displays_on(mw)

        if displays_on == 'genshi':
            if not genshi_tag:
                import genshi.builder
                genshi_tag = genshi.builder.tag
            retval = getattr(genshi_tag, self.tag)(**self.attrs).generate()
        else:
            retval = "<{tag}{attrs}></{tag}>".format(
                    tag=self.tag, attrs=self._render_attrs(self.attrs))
            if displays_on == 'kajiki':
                global kajiki_literal
                if not kajiki_literal:
                    import kajiki.util
                    kajiki_literal = kajiki.util.literal
                retval = kajiki_literal(retval)

        return retval

    def prepare(self):
        super(FontAwesomeIcon, self).prepare()

        if self.icon and self.icon not in icons:
            raise ValueError("Invalid icon name: '{}'".format(self.icon))

        self.safe_modify('attrs')

        if self.attrs.get('class'):
            classes = [self.attrs['class'], 'fa']
        else:
            classes = ['fa']

        if self.icon:
            classes.append("fa-" + self.icon)

        if self.fixed_width:
            classes.append('fa-fw')

        if self.scale:
            if self.scale not in self.allowed_scales:
                raise ValueError(
                    "'scale' must be one of {scales}, or None".format(
                        scale=", ".join(repr(x) for x in self.allowed_scales)))
            classes.append('fa-' + self.scale)

        self.attrs['class'] = " ".join(classes)
