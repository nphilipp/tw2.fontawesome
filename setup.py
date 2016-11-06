from __future__ import print_function

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

from distutils import log

import os
import re
if not hasattr(re, "ASCII"):
    # Python 2.x, ASCII doesn't exist, but is default
    re.ASCII = 0

class generate_files_mixin(object):

    iconname_selector_re = re.compile(r"\.fa-(?P<name>[^ :]+):before")

    icon_extractor_re = re.compile(
            r"(?P<selectors>"
                r"(?:\.fa-[\w-]+::?before\s*,\s*)*"
                r"\.fa-[\w-]+::?before)"
            r"""\s*{\s*content\s*:\s*"(?P<content>[^"]+)"\s*;\s*}""",
            re.MULTILINE | re.DOTALL | re.ASCII)

    icon_name_re = re.compile(r"\.fa-(?P<name>[\w-]+)::?before", re.ASCII)

    here = os.path.dirname(__file__)

    def paths(self, srcdir, destdir):
        return {
            'css': os.path.join(
                srcdir, "Font-Awesome", "css", "font-awesome.css"),
            'metadata': os.path.join(
                destdir, "tw2", "fontawesome", "metadata.py"),
            }

    def generate_files(self, srcdir, destdir):
        paths = self.paths(srcdir, destdir)
        csspath = paths['css']
        metadatapath = paths['metadata']

        icons = {}

        with open(csspath, "r") as cssfile:
            log.info("extracting icon information from CSS {}".format(csspath))
            for m in self.icon_extractor_re.finditer(cssfile.read()):
                if m:
                    selectors, content = m.group('selectors', 'content')
                for m in self.icon_name_re.finditer(selectors):
                    if m:
                        icons[m.group('name')] = content.replace("\\", "\\u")

        with open(metadatapath, "w") as metadatafile:
            # file header
            log.info("writing metadata file {}:".format(metadatapath))
            print(
                "# -*- coding: utf-8 -*-\n"
                "# This file is generated, do not edit\n"
                "\n"
                "from __future__ import unicode_literals\n", file=metadatafile)

            # icon mapping
            log.info(" - icon mapping")
            print("icons = {", file=metadatafile)
            for name, content in ((x, icons[x]) for x in sorted(icons)):
                print(
                    """    "{}": "{}",""".format(name, content),
                    file=metadatafile)
            print("}", file=metadatafile)


class my_build_py(build_py, generate_files_mixin):

    def run(self):
        build_py.run(self)

        if self.dry_run:
            return

        self.generate_files(self.here, self.build_lib)


class my_develop(develop, generate_files_mixin):

    def install_for_development(self):
        develop.install_for_development(self)

        self.generate_files(self.here, self.here)

    def uninstall_link(self):
        develop.uninstall_link(self)

        paths = self.paths(self.here, self.here)

        log.info("removing generated file {}".format(paths['metadata']))
        os.unlink(paths['metadata'])


setup(
    name="tw2.fontawesome",
    version="4.7.0",
    description="ToscaWidgets 2 wrapper for FontAwesome",
    author="Nils Philippsen",
    author_email="nils@tiptoe.de",
    #url=
    #download_url=
    install_requires=['tw2.core>=2.0', 'Genshi'],
    tests_require=['nose'],
    packages=find_packages(),
    namespace_packages = ['tw2'],
    zip_safe=False,
    include_package_data=True,
    package_data={"tw2.fontawesome": ["static/css/*", "static/fonts/*"]},
    test_suite="nose.collector",
    entry_points="""
        [tw2.widgets]
        widgets = tw2.fontawesome
    """,
    keywords = ["tw2.widgets"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Environment :: Web Environment :: ToscaWidgets",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Widget Sets",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    cmdclass={
        'build_py': my_build_py,
        'develop': my_develop
        }
)
