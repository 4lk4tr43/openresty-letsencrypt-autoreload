#!/usr/bin/python

import os
import re

configuration_directory = "A:\Projects\openresty-letsencrypt-autoreload\mnt\configurations"

def get_blocks(s):
    current_index = 0
    root_block = []

    def get_block(sub_str):
        i = 0
        end_of_block = False
        content = ''

        while i < len(sub_str):
            c = sub_str[i]

            if c == '{':
                index, block_name, block_content = get_block(sub_str[i:])
            elif c == '}':
                end_of_block = True

            if end_of_block:
                return i, block_content[1:-1]
            else:
                block_content += c

            i += 1

    return get_block('{' + s + '}')


configuration_regexp = re.compile('.+(\.conf$)')
for root, dirs, files in os.walk(configuration_directory):
    for name in files:
        if configuration_regexp.match(name) is not None:
            path = open(os.path.join(root, name), 'r')

            print get_blocks(file.read(path))

            break
