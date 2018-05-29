#!/usr/bin/env python2.7
from pfsense_setter import PfsenseSetter
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('conf',
                        help='configuration file',
                        default='/etc/update_pfsense_alias/update_pfsense_alias.ini',
                        nargs='?')
    args = parser.parse_args()
    setter = PfsenseSetter(args.conf)
    return setter.update_alias()



if __name__ == '__main__':
    main()