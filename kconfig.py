#!/usr/bin/env python3
#-*- coding = utf-8 -*-
import argparse
import os, sys
from pathlib import * # only Python3 supports
import kconfiglib
from menuconfig import menuconfig



def gen_make_cfg_file(kconfig, filename, gui):
    print("-- Genarate makefile config file: " + filename)
    if not gui:
        kconfig.write_config(filename)

def _cmake_contents(kconfig, header):
    chunks = [header]
    add = chunks.append
    config_vars = []
    for sym in kconfig.unique_defined_syms:
        # _write_to_conf is determined when the value is calculated. This
        # is a hidden function call due to property magic.
        val = sym.str_value
        if not sym._write_to_conf:
            continue
        if sym.orig_type in (kconfiglib.BOOL, kconfiglib.TRISTATE) and val == "n":
            val = ""
        add("set({}{} \"{}\")\n".format(
            kconfig.config_prefix, sym.name, val))
        config_vars.append(str(kconfig.config_prefix+sym.name))
    add("set(CONFIGS_LIST {})\n".format(";".join(config_vars)))
    return "".join(chunks)

def gen_cmake_cfg_file(kconfig, filename, gui):
    print("-- Genarate cmake config file: " + filename)
    cmake_conf_header = "### WARNING: This file is generated automatically. Do not edit it. ###\n\n"
    cmake_conf_content = _cmake_contents(kconfig, cmake_conf_header)
    # don't change file info if config no change
    if os.path.exists(filename):
        with open(filename) as f:
            if f.read() == cmake_conf_content:
                return
    f = open(filename, "w")
    f.write(cmake_conf_content)
    f.close()

def gen_header_file(kconfig, filename, gui):
    print("-- Genarate C/CPP Header file: " + filename)
    kconfig.write_autoconf(filename)

OUTPUT_FORMATS = {"makefile": gen_make_cfg_file,
                  "header": gen_header_file,
                  "cmake": gen_cmake_cfg_file
                  }

def args_process(basename):
    # args parser
    kconfig_parser = argparse.ArgumentParser(description='menuconfig tool', prog=os.path.basename(basename))
    kconfig_parser.add_argument('--kconfig', help='KConfig file', default='Kconfig', metavar='FILENAME', required=None)
    kconfig_parser.add_argument('--defaults', action='append', default=[], help='Optional project defaults file. Multiple files can be specified using multiple --defaults arguments.', metavar="FILENAME")
    kconfig_parser.add_argument('--output', nargs=2, action='append', help='Write output file (format and output filename)', metavar=('FORMAT', 'FILENAME'), default=[])
    #kconfig_parser.add_argument('--env', action='append', default=[], help='Environment to set when evaluating the config file',  metavar='VAR=VALUE')
    kconfig_parser.add_argument("--menuconfig", help="Open menuconfig GUI interface", choices=["False", "True"], default="False")

    kconfig_args = kconfig_parser.parse_args()

    out_format = {"makefile": ".config"}
    for fmt, filename in kconfig_args.output:
        if fmt not in OUTPUT_FORMATS.keys():
            print("Format %s not supported! Known formats:%s" %(fmt, OUTPUT_FORMATS.keys()))
            sys.exit(1)
        out_format[fmt] = filename

    # kconfig op
    kconfig = kconfiglib.Kconfig(kconfig_args.kconfig)
    if not os.path.exists(out_format["makefile"]):
        for path in kconfig_args.defaults:
            if not os.path.exists(path):
                raise ValueError("Path %s not found!" %(path))
            print("-- Load default:", path)
            kconfig.load_config(path, replace=False)
    else:
        kconfig.load_config()

    if kconfig_args.menuconfig == "True":
        menuconfig(kconfig)

    for fmt, filename in out_format.items():
        dir = os.path.split(filename)[0]
        if not os.path.exists(dir):
            os.makedirs(dir)

    for fmt, filename in out_format.items():
        func = OUTPUT_FORMATS[fmt]
        func(kconfig, filename, kconfig_args.menuconfig == "True")


if __name__ == '__main__':
    args_process(sys.argv[0])