#!/usr/bin/env python3

from argparse import ArgumentParser

from .DevicePool import DevicePool

def parse_args():

    parser = ArgumentParser()

    parser.add_argument('-s', '--source',
                        help = "Source yaml file with devices to create.",
                        required = False,
                        default = None,
                        type = str)
    parser.add_argument('-n', '--number',
                        help = "Number of default devices to create in addition to devices in source file (if any)",
                        required = False,
                        default = 0,
                        type = int)
    parser.add_argument('-l', '--log-severity',
                        help = "Default severity for logs of devices created without source file.",
                        required = False,
                        default = 3,
                        type = int)
    parser.add_argument('-p', '--portfile',
                        help = "Directory where to store file with devices addresses",
                        required = False,
                        default = None,
                        type = str)
    
    return parser.parse_args()

def main():

    args = parse_args()

    if args.number < 1 and args.source is None:
        print("Number of devices is 0 and no source file is provided. Doing nothing...")
        exit(0)

    devices = DevicePool(args.source, args.number, log_severity=args.log_severity, portfile_prefix=args.portfile)

if __name__ == "__main__":

    main()