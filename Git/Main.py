import os

import zlib
import hashlib

GIT_OBJECTS_PATH = '.git/objects'
with open('.gitignore') as f:
    GIT_IGNORE = f.readlines()


def git_init() -> None:
    try:
        os.mkdir('.git')
        os.mkdir('.git/objects')
        os.mkdir('.git/refs')
        with open('.git/HEAD', 'w') as head_file:
            head_file.write('ref: refs/heads/master\n')

        print('git init(Success)')

    except Exception as e:
        raise Exception('git init(Error):' + e)


def cat_file(sha_key: str) -> str:
    if len(sha_key) != 40:
        raise Exception('invalid sha')

    try:
        folder_name = sha_key[:2]
        file_name = sha_key[2:]

        with open(f'{GIT_OBJECTS_PATH}/{folder_name}/{file_name}', 'r') as f:
            compressed_data = eval(f.read())
            decompressed_data = zlib.decompress(compressed_data)

            return decompressed_data

    except Exception as e:
        print('cat-file(Error):', e)


def generate_sha_key(object_name: str, content: str) -> str:
    header = f"{object_name} {len(content)}\u0000"
    store = header + content

    sha_key = hashlib.sha1(
        header.encode('utf-8')
    ).hexdigest()

    return sha_key


def hash_object(object_name: str, file_name: str) -> str:
    if os.path.exists(file_name):
        original_data = open(file_name, 'rb').read()
        compressed_data = zlib.compress(original_data, zlib.Z_BEST_COMPRESSION)

        sha_key = generate_sha_key(object_name, str(original_data))

        if not os.path.exists(f'{GIT_OBJECTS_PATH}/{sha_key[:2]}'):
            os.mkdir(f'{GIT_OBJECTS_PATH}/{sha_key[:2]}')

        with open(f'{GIT_OBJECTS_PATH}/{sha_key[:2]}/{sha_key[2:]}', 'w') as f:
            f.write(str(compressed_data))

        return sha_key

    else:
        print('hash_object(Error): file doesn\'t exists')


def tree(sha_code: str) -> str:
    for file_name in os.listdir(path):
        level = len(path.split('/')) - 1
        printed = '  ' * level + f'- {file_name}'

        print(printed)

        if os.path.isdir(f'{path}/{file_name}'):
            printed += '/'

        if os.path.isdir(f'{path}/{file_name}'):
            tree(f'{path}/{file_name}')


def ls_tree(sha_key):
    content = cat_file(sha_key)

    return content.decode('utf-8').split('\n')


def write_tree(path: str) -> None:
    tree = ''

    for file_name in set(os.listdir(path)) - set(['.git']):
        file_path = f'{path}/{file_name}'

        if os.path.isdir(file_path):
            object_name = 'tree'
            key = write_tree(file_path)
        else:
            object_name = 'blob'
            key = hash_object('blob', file_path)

        print(f'{object_name} {key} {file_name}')
        tree += f'{object_name} {key} {file_name}\n'

    key = generate_sha_key('tree', path)

    if not os.path.exists(f'{GIT_OBJECTS_PATH}/{key[:2]}'):
        os.mkdir(f'{GIT_OBJECTS_PATH}/{key[:2]}')

    with open(f'{GIT_OBJECTS_PATH}/{key[:2]}/{key[2:]}', 'w') as f:
        f.write(str(zlib.compress(bytes(tree, 'utf-8'), zlib.Z_BEST_COMPRESSION)))

    return key
