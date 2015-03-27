#!/usr/bin/python
# -*- coding: utf-8 -*-

# main.py file is part of USBdev.

# Copyright 2015 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# USBdev is a tool recognition of USB devices.

# https://github.com/dslackw/USBdev

# USBdev is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import time
import usb.core

__all__ = "usbdev"
__author__ = "dslackw"
__copyright__ = 2015
__version_info__ = (2015, 3, 24)
__version__ = "{0}.{1}.{2}".format(*__version_info__)
__license__ = "GNU General Public License v3 (GPLv3)"
__email__ = "d.zlatanidis@gmail.com"
__website__ = "https://github.com/dslackw/USBdev"
__lib_path__ = "/var/lib/{0}/".format(__all__)


def usb_ids():
    """ find plugin usb devices """
    dict_ids = {}
    dev = usb.core.find(find_all=True)
    for cfg in dev:
        dict_ids[hex(cfg.idVendor)] = hex(cfg.idProduct)
    return dict_ids


def repository():
    """ read usb ids repository """
    with open(__lib_path__ + 'usb.ids', 'r') as f:
        return f.read()


def fix_ids(id):
    """ convert id from hex to string """
    len_id = len(id)
    if len_id < 4:
        return('0' * (4 - len_id) + id)
    return id


def find_usb(diff):
    """ return usb vendor name and device name """
    usb_find = {}
    vendor_id, vendor_name = '', ''
    for search in repository().splitlines():
        for ven, pro in diff.items():
            if ven:
                vendor_id = fix_ids(ven[2:])
            if search.startswith(vendor_id):
                vendor_name = search[len(vendor_id):].strip()
            if vendor_name and vendor_name not in usb_find.keys():
                usb_find[vendor_name] = ''
            if (vendor_name and not usb_find[vendor_name] and
                    search.startswith('\t{0}'.format(pro[2:]))):
                usb_find[vendor_name] = search[6:].strip()
    return usb_find


def daemon(stb):
    """ main loop recognize if usb plugin """
    sys.stdout.write('Plugin USB device now ...')
    sys.stdout.flush()
    count = 0
    try:
        while True:
            before = usb_ids()
            time.sleep(stb)
            count += 1
            sys.stdout.write('.')
            sys.stdout.flush()
            after = usb_ids()
            diff = dict(set(after.items()) - set(before.items()))
            if diff or count == 60:
                sys.stdout.write('Done')
                break
        return diff
    except KeyboardInterrupt:
        return {}


def options():
    """ print arguments options """
    args = [
        "USBdev is a tool recognition of USB devices\n",
        "Optional  arguments:",
        "  -h, --help               display this help and exit",
        "  -v, --version            print program version and exit",
        "  -t, --time [sec]         waiting time before plugin",
    ]
    for opt in args:
        print opt
    sys.exit()


def usage():
    """ print arguments usage """
    usg = [
        "usage: {0} [-h] [-v]".format(__all__),
        "              [-t sec]"
    ]
    for opt in usg:
        print opt
    sys.exit()


def version():
    """ print version and exit """
    print('Version: {0}'.format(__version__))
    sys.exit()


def arguments():
    """ CLI control """
    args = sys.argv
    args.pop(0)
    if len(args) == 1 and args[0] in ['-h', '--help']:
        options()
    elif len(args) == 1 and args[0] in ['-v', '--version']:
        version()
    elif len(args) == 2 and args[0] in ['-t', '--time']:
        try:
            return int(args[1])
        except ValueError:
            print('{0}: Error: integer required'.format(__all__))
            sys.exit()
    elif len(args) == 0:
        return 1
    else:
        usage()


def main():

    stb = arguments()
    found = daemon(stb)
    print('')
    if found:
        print('Found:')
        for key, value in find_usb(found).iteritems():
            print("'{0} {1}'".format(key, value))
    else:
        print('No device found')

if __name__ == '__main__':
    main()
