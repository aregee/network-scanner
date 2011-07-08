#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Adriano Monteiro Marques
#
# Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
# Original author: Guilherme Polo <ggpolo@gmail.com>
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

"""
Core QuickScan Launcher
"""

# If you want to start QuickScan at system startup, please, especify here
# umit config dir. XXX outdated comment
# CONFIG_DIR = /home/myuser/.umit
CONFIG_DIR = ''

import os
import sys
import signal
import locale

if not hasattr(sys, 'frozen'):
    _source_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir))
    _bin_path = os.path.join(_source_path, 'bin')
    if os.path.exists(os.path.join(_source_path, 'MANIFEST.in')):
        # Assuming quickscan_launcher is being executed from a svn checkout.
        sys.path.insert(0, _source_path)
        # We want quickscan_launcher to be an importable module.
        sys.path.append(_bin_path)


execfile(os.path.join("deps", "umit-common", "utils", "importer.py"))

sys.path.insert(0, os.path.join("deps", "libkeybinder"))


from umit.core.BGProcess import WindowsService
from umit.core.BasePaths import HOME
from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.qs import QuickScan

HOME_CONF = None
RUNNING_FILE = None
if hasattr(sys, 'frozen'):
    FROZEN_CFG = os.path.join(os.path.dirname(sys.path[0]), ".qsuserhome")
    FROZEN_CFG = FROZEN_CFG.decode(locale.getdefaultlocale()[1])
else:
    FROZEN_CFG = None

class QSLauncherWinService(WindowsService):
    _svc_name_ = 'quickscan_launcher'
    _svc_display_name_ = "%s service" % _svc_name_
    _svc_description_ = _svc_display_name_
    _exe_args_ = None # This is defined at bottom (when not using py2exe)

    def __init__(self, args):
        WindowsService.__init__(self, args)

    def run(self):
        # _exe_args_ will be our sys.argv when this runs as a Windows service
        # as long as we don't run under py2exe.
        if FROZEN_CFG is not None:
            cfg = open(FROZEN_CFG, 'r')
            home_path = cfg.read()
            cfg.close()
            args = (sys.path[0], home_path)
        else:
            args = sys.argv[1:]
        QuickScan.main('start', winhndl=self.hndl_waitstop, *args)


def setup_homedir(usethis, force=False):
    """
    Setting umit home directory.
    """
    if force:
        Path.force_set_umit_conf(usethis)
    else:
        Path.set_umit_conf(usethis)

    global HOME_CONF, RUNNING_FILE

    HOME_CONF = os.path.split(Path.get_umit_conf())[0]
    RUNNING_FILE = os.path.join(HOME_CONF, 'qsrunning')


def usage():
    """
    Show help
    """
    print (_("Usage:") +
            (" %s start|stop|cleanup|running <config_dir>" % __file__))


def main(args, verbose=True):
    qscontrol = QuickScan.QuickScanControl(RUNNING_FILE, HOME_CONF,
            verbose, QSLauncherWinService, __file__)
    # Quoting paths since they may contain spaces
    QSLauncherWinService._exe_args_ = '"%s" "%s"' % (
            sys.path[0], qscontrol.home_conf)

    cmds = {"start": qscontrol.start,
            "stop": qscontrol.stop,
            "cleanup": qscontrol.cleanup,
            "running": qscontrol.running
            }

    cmd_args = ()
    try:
        if args[0] == 'cleanup':
            cmd_args += (True, )
        return cmds[args[0]](*cmd_args)
    except KeyError, e:
        if verbose:
            print "Invalid command especified: %s" % e
            usage()
        return 1


def pre_main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
        return 0

    if CONFIG_DIR: # forcing especified dir
        setup_homedir(CONFIG_DIR, force=True)
    else:
        try:
            setup_homedir(sys.argv[2], force=True)
        except IndexError: # no path especified
            setup_homedir(HOME)

    return main(sys.argv[1:])


if FROZEN_CFG is not None:
    def write_frozen_cfg():
        setup_homedir(HOME)
        conf = open(FROZEN_CFG, 'w')
        conf.write(HOME_CONF.encode(locale.getdefaultlocale()[1]))
        conf.close()

    import win32serviceutil
    # HandleCommandLine is used by py2exe when defining a service with
    # cmdline_style as 'custom'
    def HandleCommandLine():
        # XXX I will need the user home before starting the QuickScan,
        # I wish changing QSLauncherWinService._exe_args_ would work
        # here too, but it doesn't. The workaround here is far from
        # ideal.
        if sys.argv[1] == 'install':
            write_frozen_cfg()
        elif sys.argv[1] in ('start', 'debug'):
            if not os.path.isfile(FROZEN_CFG):
                write_frozen_cfg()

        win32serviceutil.HandleCommandLine(QSLauncherWinService)

if __name__ == "__main__":
    sys.exit(pre_main())
