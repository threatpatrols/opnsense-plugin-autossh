#!/usr/local/bin/python2.7

"""
    Copyright (c) 2018 Verb Networks Pty Ltd <contact@verbnetworks.com>
    Copyright (c) 2018 Nicholas de Jong <me@nicholasdejong.com>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import time
import json
import base64
import random
import argparse
import subprocess
from calendar import timegm


class AutosshInterfaceException(Exception):
    pass


class AutosshInterface():

    def main(self):

        parser = argparse.ArgumentParser(description='Autossh tunnel management interface')
        parser.add_argument('action',
            type=str,
            choices=['key_gen', 'connection_test', 'connection_create', 'connection_destroy', 'connection_status'],
            help='AutosshInterface action request'
        )

        # key_gen
        parser.add_argument('--key_type', type=str, help='Type of SSH key to generate')

        # connection_test, connection_create, connection_destroy, connection_status
        parser.add_argument('--connection_uuid', type=str, help='UUID of the Autossh tunnel connection to use')

        args = parser.parse_args()
        if args.action == 'key_gen' and args.key_type is not None:
            return self.key_gen(key_type=args.key_type)
        elif args.action == 'connection_test' and args.connection_uuid is not None:
            return self.connection_test(connection_uuid=args.connection_uuid)
        elif args.action == 'connection_create' and args.connection_uuid is not None:
            return self.connection_create(connection_uuid=args.connection_uuid)
        elif args.action == 'connection_destroy' and args.connection_uuid is not None:
            return self.connection_destroy(connection_uuid=args.connection_uuid)
        elif args.action == 'connection_status' and args.connection_uuid is not None:
            return self.connection_status(connection_uuid=args.connection_uuid)

        return {'status': 'fail', 'message': 'Unable to invoke AutosshInterface'}

    def key_gen(self, key_type, fingerprint_type='md5'):

        temp_keyfile = os.path.join(
            '/tmp',
            'autossh-keygen.{}'.format(''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8)))
        )

        key_comment = 'host_id:{}'.format(self.get_system_hostid())

        key_generators = {
            'dsa1024': 'ssh-keygen -t dsa -b 1024 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'ecdsa256': 'ssh-keygen -t ecdsa -b 256 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'ecdsa384': 'ssh-keygen -t ecdsa -b 384 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'ecdsa521': 'ssh-keygen -t ecdsa -b 521 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'ed25519': 'ssh-keygen -t ed25519 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'rsa1024': 'ssh-keygen -t rsa -b 1024 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'rsa2048': 'ssh-keygen -t rsa -b 2048 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
            'rsa4096': 'ssh-keygen -t rsa -b 4096 -q -N "" -f "{}" -C "{}"'.format(temp_keyfile, key_comment),
        }

        if key_type.lower() not in key_generators.keys():
            return {'status': 'fail', 'message': 'key_type not supported', 'data': key_type}

        self.shell_command(key_generators[key_type.lower()])
        if not os.path.isfile(temp_keyfile) or not os.path.isfile(temp_keyfile + '.pub'):
            return {'status': 'fail', 'message': 'unable to correctly generate ssh material'}

        fingerprint = self.shell_command('ssh-keygen -f "{}" -l -E {}'.format(temp_keyfile + '.pub', fingerprint_type)).strip()
        if len(fingerprint) < 1:
            return {'status': 'fail', 'message': 'unable to correctly generate ssh key signature'}

        with open(temp_keyfile, 'r') as f:
            private_key_data = f.read()
        os.unlink(temp_keyfile)

        with open(temp_keyfile + '.pub', 'r') as f:
            public_key_data = f.read()
        os.unlink(temp_keyfile + '.pub')

        return {
            'status': 'success',
            'message': 'SSH keypair successfully created',
            'data': {
                'key_private': base64.b64encode(private_key_data),
                'key_public': base64.b64encode(public_key_data),
                'key_fingerprint': fingerprint,
                'timestamp': time.time()
            }
        }

    def shell_command(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr is not None and len(stderr) > 0:
            raise AutosshInterfaceException(stderr.strip())
        return stdout

    def connection_test(self, connection_uuid):
        return {'status': 'fail', 'message': 'function connection_test not yet implemented', 'data': connection_uuid}

    def connection_create(self, connection_uuid):
        return {'status': 'fail', 'message': 'function connection_create not yet implemented', 'data': connection_uuid}

    def connection_destroy(self, connection_uuid):
        return {'status': 'fail', 'message': 'function connection_destroy not yet implemented', 'data': connection_uuid}

    def connection_status(self, connection_uuid):
        return {'status': 'fail', 'message': 'function connection_status not yet implemented', 'data': connection_uuid}

    def get_system_hostid(self):
        hostid = '00000000-0000-0000-0000-000000000000'
        if os.path.isfile('/etc/hostid'):
            with open('/etc/hostid', 'r') as f:
                hostid = f.read().strip()
        return hostid

    def response_output(self, message, status='success', data=None):

        if status.lower() == 'okay' or status.lower() == 'ok':
            status = 'success'

        response_data = {
            'status': status.lower(),
            'message': message,
            'timestamp': self.normalize_timestamp(time.time())
        }

        if data is not None:
            response_data['data'] = data

        print (json.dumps(response_data))
        return response_data

    def normalize_timestamp(self, input):

        # oh just kill me now :( every part of this just feels horrible

        try:
            input = str(input)

            # 2018-08-04T07:46:37.000Z
            if '-' in input and 'T' in input and ':' in input and '.' in input and input.endswith('Z'):
                t = time.strptime(input.split('.')[0], '%Y-%m-%dT%H:%M:%S')

            # 2018-08-04T07:44:45Z
            elif '-' in input and 'T' in input and ':' in input and '.' not in input and input.endswith('Z'):
                t = time.strptime(input, '%Y-%m-%dT%H:%M:%SZ')

            # 20180804T074445Z
            elif '-' not in input and 'T' in input and ':' not in input and '.' not in input and input.endswith(
                    'Z'):
                t = time.strptime(input, '%Y%m%dT%H%M%SZ')

            # 20180804Z074445
            elif '-' not in input and 'T' not in input and ':' not in input and '.' not in input and 'Z' in input:
                t = time.strptime(input, '%Y%m%dZ%H%M%S')

            # 1533373930.983988
            elif '-' not in input and 'T' not in input and ':' not in input and '.' in input and 'Z' not in input:
                t = time.gmtime(int(input.split('.')[0]))

            # 1533378888
            elif '-' not in input and 'T' not in input and ':' not in input and '.' not in input and 'Z' not in input:
                t = time.gmtime(int(input))

        except ValueError as e:
            return input

        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timegm(t)))


if __name__ == '__main__':
    Interface = AutosshInterface()
    Interface.response_output(**Interface.main())
