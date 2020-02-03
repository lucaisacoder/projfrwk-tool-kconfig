#!/usr/bin/env python3
#-*- coding = utf-8 -*-
import argparse
import os, sys
from pathlib import * # only Python3 supports
import kconfiglib
from menuconfig import menuconfig


def args_process(basename):
    # args parser
    kconfig_parser = argparse.ArgumentParser(description='menuconfig tool', prog=os.path.basename(basename))
    kconfig_parser.add_argument('--kconfig', help='KConfig file', default='Kconfig', metavar='FILENAME', required=None)
    #kconfig_parser.add_argument('--defaults', action='append', default=[], help='Optional project defaults file. Multiple files can be specified using multiple --defaults arguments.', metavar="FILENAME")
    #kconfig_parser.add_argument('--output', nargs=2, action='append', help='Write output file (format and output filename)', metavar=('FORMAT', 'FILENAME'), default=[])
    #kconfig_parser.add_argument('--env', action='append', default=[], help='Environment to set when evaluating the config file',  metavar='VAR=VALUE')
    kconfig_parser.add_argument("--menuconfig", help="Open menuconfig GUI interface", choices=["False", "True"], default="False")

    # kconfig op
    kconfig_args = kconfig_parser.parse_args()
    kconfig = kconfiglib.Kconfig(kconfig_args.kconfig)
    kconfig.load_config()
    if kconfig_args.menuconfig == "True":
        menuconfig(kconfig)


if __name__ == '__main__':
    args_process(sys.argv[0])