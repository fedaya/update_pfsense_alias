# -*- coding: utf-8 -*-
# netsoins_route
# Copyright (C) 2018  Etienne Gille
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from dns import resolver
import ConfigParser
import sys


class DnsGetter:
    """
        This is a helper class designed to get the IP address(es) from the urls defined in the ini file.
    """
    def __init__(self, ini_file):
        """

        :param ini_file: a ini file in which [general]->domains is defined as a comma separated list
        """
        self.ini_file = ini_file
        try:
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(ini_file)
            self.domains = cfg.get('general', 'domains').split(',')
            try:
                self.dns_servers = cfg.get('general', 'dns_servers').split(',')
            except:
                self.dns_servers = None
            if 'default' in self.dns_servers:
                self.dns_servers = None
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.ParsingError):
            print >> sys.stderr, 'Malformed ini file'
            exit(1)

    def get_ip_addresses(self):
        """
        Get the IP Addresses from extracted domain names

        :return: a list of IP addresses (as strings)
        """
        ips = []
        solver = None
        if self.dns_servers is None:
            solver = resolver.get_default_resolver()
        else:
            solver = resolver.Resolver(configure=False)
            solver.nameservers = self.dns_servers
        for domain in self.domains:
            try:
                ans = solver.query(domain, 'A')
            except (resolver.NoAnswer, resolver.NXDOMAIN):
                print >> sys.stderr, "this domain doesn't exist: " + domain
                exit(2)
            except resolver.NoNameservers:
                print >> sys.stderr, "unable to do a dns query, please check your internet connection"
                exit(3)
            for a in ans:
                ips.append((domain, str(a)))
        return ips

    def reread_ini_file(self, ini_file = None):
        """
        reread the original ini file or a new one if supplied

        :param ini_file: if supplied, this new ini file will be parsed instead of the original one.
        :return:
        """
        if ini_file is None:
            ini_file = self.ini_file
        self.__init__(ini_file)

