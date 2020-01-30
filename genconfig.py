#
# @file from https://github.com/Neutree/c_cpp_project_framework
# @author neucrack
#

import argparse
import os, sys

kconfig_lib_path = sys.path[0]+"/Kconfiglib"
sys.path.append(kconfig_lib_path)

import kconfiglib
from menuconfig import menuconfig


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


def write_config(kconfig, filename, gui):
    print("-- Write makefile config at: " + filename)
    if not gui:
        kconfig.write_config(filename)

def write_cmake(kconfig, filename, gui):
    print("-- Write  cmake  config  at: " + filename)
    cmake_conf_header = "# Generated by c_cpp_project_framework(https://github.com/Neutree/c_cpp_project_framework)\n"
    cmake_conf_header += "### DO NOT edit this file!! ###\n\n"
    cmake_conf_content = _cmake_contents(kconfig, cmake_conf_header)
    # don't change file info if config no change
    if os.path.exists(filename):
        with open(filename) as f:
            if f.read() == cmake_conf_content:
                return
    f = open(filename, "w")
    f.write(cmake_conf_content)
    f.close()


def write_header(kconfig, filename, gui):
    print("-- write  c header file  at: " + filename)
    kconfig.write_autoconf(filename)

OUTPUT_FORMATS = {"makefile": write_config,
                  "header": write_header,
                  "cmake": write_cmake
                  }

parser = argparse.ArgumentParser(description='menuconfig tool', prog=os.path.basename(sys.argv[0]))

parser.add_argument('--kconfig',
                    help='KConfig file',
                    default='Kconfig',
                    metavar='FILENAME',
                    required=None)

parser.add_argument('--defaults',
                    action='append',
                    default=[],
                    help='Optional project defaults file. '
                            'Multiple files can be specified using multiple --defaults arguments.',
                    metavar="FILENAME"
                    )

parser.add_argument('--output', nargs=2, action='append',
                        help='Write output file (format and output filename)',
                        metavar=('FORMAT', 'FILENAME'),
                        default=[])

parser.add_argument('--env',
                    action='append',
                    default=[],
                    help='Environment to set when evaluating the config file', 
                    metavar='VAR=VALUE'
                    )

parser.add_argument("--menuconfig",
                    help="Open menuconfig GUI interface",
                    choices=["False", "True"],
                    default="False",
                    )

args = parser.parse_args()
print("9999999999: " + args.kconfig)
for env in args.env:
    env = env.split("=")
    var = env[0]
    value = env[1]
    os.environ[var] = value

out_format = {"makefile": ".config"}
for fmt, filename in args.output:
    if fmt not in OUTPUT_FORMATS.keys():
        print("Format %s not supported! Known formats:%s" %(fmt, OUTPUT_FORMATS.keys()))
        sys.exit(1)
    out_format[fmt] = filename
    
if out_format["makefile"] != ".config":
    os.environ["KCONFIG_CONFIG"] = out_format["makefile"]

kconfig = kconfiglib.Kconfig(args.kconfig)

# load config, so if config file exist, the default file may 
#              not take effect, if want to use default, 
#              remove the config file in build directory
if not os.path.exists(out_format["makefile"]):
    for path in args.defaults:
        if not os.path.exists(path):
            raise ValueError("Path %s not found!" %(path))
        print("-- Load default:", path)
        kconfig.load_config(path, replace=False)
else:
    kconfig.load_config()

if args.menuconfig == "True":
    menuconfig(kconfig)

# write back
for fmt, filename in out_format.items():
    dir = os.path.split(filename)[0]
    if not os.path.exists(dir):
        os.makedirs(dir)

for fmt, filename in out_format.items():
    func = OUTPUT_FORMATS[fmt]
    func(kconfig, filename, args.menuconfig == "True")


