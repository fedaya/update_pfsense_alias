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

import requests
import ConfigParser
import datetime
import hashlib
import base64
import json
import os
import sys
from copy import deepcopy
import dns_getter


class PfsenseSetter:
    """
    This is a helper class designed to set specific routes for pfsense using FauxAPI

    It works by changing a designated alias in the config

    Please checkout FauxAPI for more information on how to install and use it on github:
    https://github.com/ndejong/pfsense_fauxapi
    """

    class PfSenseParams(object):
        pass

    def __init__(self, ini_file):
        """

        :param ini_file: the ini file used to configure the program
        """
        self.ini_file = ini_file
        self.current_alias_table = []
        self.current_config = {}
        try:
            cfg = ConfigParser.SafeConfigParser()
            cfg.read(ini_file)
            self.pfsense = self.PfSenseParams()
            self.pfsense.alias = cfg.get('pfsense', 'alias_name')
            self.pfsense.address = cfg.get('pfsense', 'address')
            self.pfsense.method = cfg.get('pfsense', 'method')
            self.pfsense.port = cfg.get('pfsense','port')
            self.pfsense.auth_key = cfg.get('pfsense', 'auth_key')
            self.pfsense.auth_secret = cfg.get('pfsense', 'auth_secret')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.ParsingError):
            print >> sys.stderr, 'Malformed ini file'
            exit(1)

    @staticmethod
    def _get_timestamp():
        """
        Return the timestamp for usage with FauxAPI auth
        :return: timestamp in the format used by FauxAPI
        """
        return datetime.datetime.utcnow().strftime("%Y%m%dZ%H%M%S")

    def _get_fauxapi_auth(self):
        """
        Returns the fauxapi-auth header

        basically a copy of _generate_auth from FauxAPI python client library
        :return: the content of the fauxapi-auth header
        """
        timestamp = self._get_timestamp()
        nonce = base64.b64encode(os.urandom(40)).decode('utf-8').replace('=', '').replace('/', '').replace('+', '')[0:8]
        hash = hashlib.sha256('{}{}{}'.format(self.pfsense.auth_secret, timestamp, nonce).encode('utf-8')).hexdigest()
        return '{}:{}:{}:{}'.format(self.pfsense.auth_key, timestamp, nonce, hash)

    def _request_uri(self, action):
        return r'{}://{}:{}/fauxapi/v1/?action={}'.format(
            self.pfsense.method,
            self.pfsense.address,
            self.pfsense.port,
            action,
        )

    def _get_current_config(self):
        rq = requests.get(
            url=self._request_uri('config_get'),
            headers={'fauxapi-auth': self._get_fauxapi_auth()},
        )
        ret = rq.json()
        self.current_config = ret['data']['config']
        aliases = ret['data']['config']['aliases']['alias']
        alias = {}
        idx = 0
        for al in aliases:
            if al['name'] == self.pfsense.alias:
                self.current_alias = al
                self.current_alias_idx = idx
                break
            else:
                idx += 1
        alias_addresses = self.current_alias['address'].split(' ')
        alias_names = self.current_alias['detail'].split('||')
        self.current_alias_table = zip(alias_names, alias_addresses)
        return self.current_config

    @staticmethod
    def _find_in_tuple_list(tuple_list, elt):
        idx = -1
        it = 0
        for tup in tuple_list:
            if elt in tup:
                idx = it
                break
            else:
                it += 1
        return idx

    def _prep_update_alias(self):
        ips = dns_getter.DnsGetter(self.ini_file).get_ip_addresses()
        if ips == self.current_alias_table:
            print >> sys.stderr, "IPs haven't changed, no update necessary"
            return False
        alias_names, alias_addresses = zip(*ips)
        new_alias = deepcopy(self.current_alias)
        new_alias['address'] = ' '.join(alias_addresses).encode('utf-8')
        new_alias['detail'] = '||'.join(alias_names).encode('utf-8')
        self.new_config = deepcopy(self.current_config)
        self.new_config['aliases']['alias'][self.current_alias_idx] = new_alias
        return True

    def update_alias(self):
        self._get_current_config()
        rq_address = self._request_uri('config_set')

        rq_headers = {
            'fauxapi-auth': self._get_fauxapi_auth()
        }
        if self._prep_update_alias():
            with open('old_config.json','wb') as old_config:
                old_config.write(json.dumps(self.current_config))
            with open('new_config.json','wb') as new_config:
                new_config.write(json.dumps(self.new_config))

            rq = requests.post(
                url=rq_address,
                json=self.new_config,
                headers=rq_headers,
            )
            return rq.status_code == 200
        else:
            return False
