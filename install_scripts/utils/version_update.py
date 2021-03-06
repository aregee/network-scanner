#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

# This program updates the Umit version number in all the places it needs to be
# updated. It takes a single command-line argument, which is the new version
# number. For example:
# python install_scripts/utils/version_update.py X.YY

import os
import sys

from glob import glob
import re

UMIT_VERSION = os.path.join("share", "umit", "config", "umit_version")
VERSION_PY = os.path.join("umit", "core", "Version.py")
UMIT_COMPILED_NSI = os.path.join("install_scripts", "windows", "umit_compiled.nsi")

def get_winpcap():
    windeps = os.path.join("install_scripts", "windows",
                           "win_dependencies", "WinPcap*")
    return os.path.split(glob(windeps)[0])[1]

WINPCAP = get_winpcap()

def update_umit_compiled(base_dir, version):
    umit_compiled = os.path.join(base_dir, UMIT_COMPILED_NSI)
    print ">>> Updating:", umit_compiled
    ucf = open(umit_compiled)
    ucompiled_content = ucf.read()
    ucf.close()

    ucompiled_content = re.sub("!define APPLICATION_VERSION \".+\"",
                               "!define APPLICATION_VERSION \"%s\"" % version,
                               ucompiled_content)
    ucompiled_content = re.sub("!define WINPCAP \".+\"",
                               "!define WINPCAP \"%s\"" % WINPCAP,
                               ucompiled_content)

    ucf = open(umit_compiled, "w")
    ucf.write(ucompiled_content)
    ucf.close()

def update_umit_version(base_dir, version):
    print ">>> Updating %s" % os.path.join(base_dir, UMIT_VERSION)
    vf = open(os.path.join(base_dir, UMIT_VERSION), "wb")
    print >> vf, version
    vf.close()
    print ">>> Updating %s" % os.path.join(base_dir, VERSION_PY)
    vf = open(os.path.join(base_dir, VERSION_PY), "w")
    print >> vf, "VERSION = \"%s\"" % version
    vf.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "Usage: %s <version>" % sys.argv[0]
        sys.exit(1)

    version = sys.argv[1]
    print ">>> Updating version number to \"%s\"" % version
    update_umit_version(".", version)
    update_umit_compiled(".", version)
