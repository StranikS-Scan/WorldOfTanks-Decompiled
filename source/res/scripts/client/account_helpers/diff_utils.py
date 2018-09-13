# Embedded file name: scripts/client/account_helpers/diff_utils.py


def synchronizeDicts(diff, cache):
    updates, replaces, deletes = (0, 0, 0)
    keys_r, keys_d, keys_u = [], [], []
    for k in diff.iterkeys():
        if isinstance(k, tuple):
            if k[1] == '_r':
                keys_r.append(k)
                replaces += 1
                continue
            elif k[1] == '_d':
                keys_d.append(k)
                deletes += 1
                continue
        keys_u.append(k)
        updates += 1

    for key_r in keys_r:
        cache[key_r[0]] = diff[key_r]

    for key_d in keys_d:
        value = cache.get(key_d[0], None)
        if value:
            value.difference_update(diff[key_d])

    for key_u in keys_u:
        value = diff[key_u]
        if value is None:
            cache.pop(key_u, None)
        elif isinstance(value, dict):
            updates, replaces, deletes = [ i + j for i, j in zip((updates, replaces, deletes), synchronizeDicts(value, cache.setdefault(key_u, {}))) ]
        elif isinstance(value, set):
            cache.setdefault(key_u, set()).update(value)
        else:
            cache[key_u] = value

    return (updates, replaces, deletes)
