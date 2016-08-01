# -*- coding: utf-8 -*-
#
# tw2.fontawesome.resources - FontAwesome CSS resources
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

import os

from tw2.core.params import Param, Deferred
from tw2.core import Link, CSSLink, DirLink
from tw2.core.core import request_local
from tw2.core.middleware import register_resource

from . import config


__all__ = ('FontAwesomeCSSLink')


class AltLinkError(Exception):
    pass


class AltLinkMixin(Link):
    name = Param("(string) The name of the resource to link to")
    dirname = Param("(string) Specify the directory path for the given file, "
                    "relative to the \"static\" folder.  Some substitutions "
                    "are allowed (name and version).")
    basename = Param("(string) Specify the basename for the given file.")
    version = Param("(string) Specify the version of the resource to use.")
    external = Param("(boolean) True if you would like to grab the file from "
                     "a CDN instead of locally.  Default: False",
                     default=Deferred(lambda: config.external))
    url_base = Param("(string) The base url for fetching the resource "
                     "externally")
    extension = Param("(string) File extension")
    additional_files = Param("(list(string)) An optional list of files that "
                             "should be registered with the static resource "
                             "handler.  Default: []", default=[])

    variant = Param("File variant, e.g., (min for minified), "
                    "default is %s" % config.variant,
                    default=Deferred(lambda: config.variant))

    def __init__(self, *args, **kw):
        self._link = None
        super(AltLinkMixin, self).__init__(*args, **kw)

    def prepare(self):
        if not self.is_external:
            self.modname or self.__module__
            rl = request_local()
            resources = rl['middleware'].resources
            resources.register(
                self.modname,
                os.path.dirname(self.filename),
                whole_dir=True)
        super(AltLinkMixin, self).prepare()

    @property
    def core_filename(self):
        ret = self.basename
        variant = self.variant
        if isinstance(variant, Deferred):
            variant = variant.fn()
        if variant:
            ret = '.'.join((ret, variant))
        ret += '.' + self.extension
        return ret

    @property
    def external_link(self):
        link = '/'.join((self.url_base, self.dirname, self.core_filename))
        return link

    def _get_link(self):
        rl = request_local()
        mw = rl['middleware']

        external = self.external
        if isinstance(external, Deferred):
            external = external.fn()

        if not self._link:
            if external:
                link = self.external_link
            else:
                link = ('/' + '/'.join((
                    mw.config.script_name.strip('/'),
                    mw.config.res_prefix.strip('/'),
                    self.modname,
                    'static',
                    self.dirname,
                    self.core_filename
                ))).replace('//', '/')
            self._link = link
        return self._link % self.substitutions

    def _set_link(self, link):
        self._link = link

    link = property(_get_link, _set_link)

    def abspath(self, filename):
        return os.sep.join((
            pkg_resources.resource_filename(self.modname, ''),
            filename
        ))

    def try_filename(self, filename):
        abspath = self.abspath(filename)
        if os.path.exists(abspath):
            return filename
        raise AltLinkError('File does not exist: %s' % abspath)

    @property
    def substitutions(self):
        return dict(name=self.name, version=self.version)

    @property
    def filename(self):
        #make basename windows/qnix compat
        basename = self.core_filename
        basename = basename.replace('/', os.sep)
        basename = basename.replace('\\', os.sep)

        filename = os.sep.join(('static', self.dirname, basename)) % \
                self.substitutions

        #try the default
        return self.try_filename(filename)

    @property
    def is_external(self):
        return self.external


class FontAwesomeLinkMixin(AltLinkMixin):

    name = "font-awesome"
    modname = 'tw2.fontawesome'
    version = config.version
    url_base = "//maxcdn.bootstrapcdn.com/font-awesome/%(version)s"


class FontAwesomeCSSLink(CSSLink, FontAwesomeLinkMixin):

    dirname = "css"
    basename = "font-awesome"
    extension = "css"


class FontAwesomeFontsDirLink(DirLink, FontAwesomeLinkMixin):

    filename = "static/fonts"


fontawesome_css = FontAwesomeCSSLink()
fontawesome_fonts = FontAwesomeFontsDirLink()
fontawesome_resources = [fontawesome_css, fontawesome_fonts]

def register_resources():
    for res in fontawesome_resources:
        register_resource(
                res.req().modname, res.req().filename,
                isinstance(res, DirLink))

def inject_resources():
    for res in fontawesome_resources:
        res.inject()
