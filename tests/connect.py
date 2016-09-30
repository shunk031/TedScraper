# -*- coding: utf-8 -*-
# import the module
from __future__ import print_function

import aerospike
import json
import os

# Configure the client
config = {
    'hosts': [('10.29.36.182', 3000)]
}

# Create a client and connect it to the cluster
try:
    client = aerospike.client(config).connect()
except:
    import sys
    print("failed to connect to the cluster with", config['hosts'])
    sys.exit(1)

# Records are addressable via a tuple of (namespace, set, key)
key = ('test', 'foo', 'bar')

dir_name = "~/Programing/Python/ted-scraper-dev/02/ted-scraper/dump_files"
dir_list = os.listdir(dir_name)

for dl in dir_list:
    with open(os.path.join(dir_name, dl), "r") as f:
        data = json.load(f)
        print("add %s" % dl)
        try:
            # Write a record
            client.put(key, data)

        except Exception as e:
            import sys
            print("error: {0}".format(e), file=sys.stderr)
# Read a record
(key, metadata, record) = client.get(key)
print(key, metadata, record)

# Close the connection to the Aerospike cluster
client.close()
