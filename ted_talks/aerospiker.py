# -*- coding: utf-8 -*-

from __future__ import print_function

import aerospike
import json
import os


class Aerospiker:

    def __init__(self, address, key):
        self.config = {
            'hosts': [(address, 3000)]
        }
        self.key = key

        # connect aerospike
        self.connect()

    def connect(self):
        try:
            self.client = aerospike.client(self.config).connect()
        except:
            import sys
            print("failed to connect to the cluster with",
                  self.config['hosts'])
            sys.exit(1)

    def put_all_talk_info(self, save_dir=None):

        if save_dir is None:
            save_dir = "./dump_files"
        else:
            save_dir = os.path.expanduser(save_dir)

        file_list = os.listdir(save_dir)
        for fl in file_list:
            with open(os.path.join(save_dir, fl), "r") as f:
                bins = json.load(f)
                print("put %s" % fl)
                try:
                    self.client.put(self.key, bins)
                except Exception as e:
                    import sys
                    print("error: {0}".format(e), file=sys.stderr)

    def get_talk_info(self):
        return self.client.get(self.key)

    def put_talk_info(self):
        self.client.put(self.key)

    def disconnect(self):
        self.client.close()
