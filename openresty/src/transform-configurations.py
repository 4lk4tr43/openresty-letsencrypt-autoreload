import os
import re

configuration_directory = '/configurations'
transform_directory = '/transformed'


def get_block_name(s, i):
    start = i
    while start >= 0:
        start -= 1
        c = s[start]
        if c == ';' or c == '{' or c == '}':
            break
    return s[start + 1:i].replace('\n', '').strip()


def get_blocks_start_index_and_level_and_name(s):
    tuples = []
    mustache_count = 0
    for i, c in enumerate(s):
        if c == '{':
            mustache_count += 1
            tuples.append((i, mustache_count, get_block_name(s, i)))
        elif c == '}':
            tuples.append((i, mustache_count, 'end'))
            mustache_count -= 1
    return tuples


def get_server_blocks_start_and_end_index(blocks):
    server_blocks = []
    start = None
    for block in blocks:
        if block[2] == 'server':
            start = block
        if start is not None and block[2] == 'end' and block[1] == start[1]:
            server_blocks.append((start[0], block[0]))
            start = None
    return server_blocks


listen_ssl_regexp = re.compile(r'(^listen.*ssl).*')
listen_80_regexp = re.compile(r'(^listen.*80).*')
location_letsencrypt_regexp = \
    re.compile(r'.*(location\s+/\.well-known/acme-challenge/?\s*'
               r'{\s*content_by_lua_block\s*{\s+auto_ssl\:challenge_server\(\s*\)\s*}\s*}).*')
ssl_certificate_regexp = re.compile(r'.*(ssl_certificate\s.*;).*')
ssl_certificate_key_regexp = re.compile(r'.*(ssl_certificate_key\s.*;).*')
lua_certificate_regexp = re.compile(r'.*(ssl_certificate_by_lua_block\s*'
                                    r'\{\s*auto_ssl:ssl_certificate\s*\(\s*\)\s*\}).*')


def remove_expression(block, expression):
    i = block.find(expression + ' ')
    if i > -1:
        i = i
        while i < len(block):
            if block[i] == ';':
                break
            i += 1
        return block[0:i] + block[i + 1:]
    return block


def modify_server_block(block):
    stripped_block = ' '.join(block.replace('\n', '').split())
    split = stripped_block.replace('{', ';').replace('}', ';').split(';')

    for fragment in split:
        part = fragment.strip()
        if listen_80_regexp.match(part) is not None:
            if location_letsencrypt_regexp.match(stripped_block):
                return None
            return '{ location /.well-known/acme-challenge/ { content_by_lua_block { auto_ssl:challenge_server() } }' \
                   + stripped_block[1:len(stripped_block) - 1] + ' }'
        elif listen_ssl_regexp.match(part) is not None:
            modified_block = stripped_block[:len(stripped_block) - 1]
            has_certificate = ssl_certificate_regexp.match(stripped_block)
            has_certificate_key = ssl_certificate_key_regexp.match(stripped_block)

            if has_certificate is not None and has_certificate_key is not None:
                return None

            if has_certificate_key is None:
                modified_block = remove_expression(modified_block, 'ssl_certificate')
            else:
                modified_block = remove_expression(modified_block, 'ssl_certificate_key')

            modified_block += ' ssl_certificate /etc/ssl/resty-auto-ssl-fallback.crt;' \
                              ' ssl_certificate_key /etc/ssl/resty-auto-ssl-fallback.key;'

            if lua_certificate_regexp.match(modified_block) is None:
                modified_block = '{ ssl_certificate_by_lua_block { auto_ssl: ssl_certificate() } ' + modified_block[1:]

            return modified_block + ' }'


def get_server_blocks(s, indices):
    block_contents = []
    for i, e in indices:
        block_contents.append(s[i:e + 1])
    return block_contents


def transform_server_blocks(blocks):
    modified_blocks = []
    for block in blocks:
        modified_blocks.append(modify_server_block(block))
    return modified_blocks


def modify_content(s, block_indices, transformed_server_blocks):
    parts = []
    current_index = 0
    for indices in block_indices:
        parts.append(s[current_index:indices[0]])
        parts.append(s[indices[0]:indices[1] + 1])
        current_index = indices[1] + 1

    i = 0
    while i * 2 + 1 < len(parts):
        if transformed_server_blocks[i] is not None:
            parts[i * 2 + 1] = transformed_server_blocks[i]
        i += 1

    return re.sub('\n+', '\n', ''.join(parts))


def remove_comment(line):
    no_comments_line = ''
    double_string = False
    single_string = False
    for c in line:
        if c == '#':
            if not double_string and not single_string:
                break
        elif c == '"':
            double_string = not double_string
        elif c == "'":
            single_string = not single_string
        no_comments_line += c
    return no_comments_line


def remove_comments(s):
    no_comments = []
    split = s.split('\n')
    for line in split:
        no_comments.append(remove_comment(line))
    return '\n'.join(no_comments)


for root, dirs, files in os.walk(transform_directory):
    for name in files:
        os.remove(os.path.join(root, name))

for root, dirs, files in os.walk(configuration_directory):
    for name in files:
        if name.endswith('.conf'):
            with open(os.path.join(root, name), 'r') as file:
                content = remove_comments(file.read())
                server_block_indices = get_server_blocks_start_and_end_index(get_blocks_start_index_and_level_and_name(content))
                modified_server_blocks = transform_server_blocks(get_server_blocks(content, server_block_indices))
                with open(os.path.join(transform_directory, name), 'x') as transformed_file:
                    transformed_file.write(modify_content(content, server_block_indices, modified_server_blocks))

print('Transform Executed')