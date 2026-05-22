"""Simple helper to rename or delete embedding keys in embeddings.pkl."""

import os
import pickle
import sys


def load_embeddings(file_path):
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'rb') as handle:
        return pickle.load(handle)


def save_embeddings(file_path, payload):
    with open(file_path, 'wb') as handle:
        pickle.dump(payload, handle)


def rename_key(file_path, old_key, new_key):
    data = load_embeddings(file_path)
    if old_key not in data:
        return 0

    data[new_key] = data.pop(old_key)
    save_embeddings(file_path, data)
    return len(data.get(new_key, []))


def delete_key(file_path, key):
    data = load_embeddings(file_path)
    if key in data:
        del data[key]
        save_embeddings(file_path, data)
        return 1

    return 0


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python embedding_store.py <rename|delete> <embeddings_path> <key> [new_key]')
        sys.exit(1)

    action = sys.argv[1]
    embeddings_path = sys.argv[2]
    key = sys.argv[3]

    try:
        if action == 'rename':
            if len(sys.argv) < 5:
                raise ValueError('new_key is required for rename action')
            new_key = sys.argv[4]
            count = rename_key(embeddings_path, key, new_key)
            print(count)
        elif action == 'delete':
            count = delete_key(embeddings_path, key)
            print(count)
        else:
            raise ValueError(f'Unknown action: {action}')
    except Exception as error:
        print(str(error))
        sys.exit(1)