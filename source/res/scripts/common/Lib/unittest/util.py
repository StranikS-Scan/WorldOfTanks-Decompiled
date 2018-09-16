# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/unittest/util.py
from collections import namedtuple, OrderedDict
__unittest = True
_MAX_LENGTH = 80

def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)

    return result if not short or len(result) < _MAX_LENGTH else result[:_MAX_LENGTH] + ' [truncated]...'


def strclass(cls):
    return '%s.%s' % (cls.__module__, cls.__name__)


def sorted_list_difference(expected, actual):
    i = j = 0
    missing = []
    unexpected = []
    while True:
        try:
            e = expected[i]
            a = actual[j]
            if e < a:
                missing.append(e)
                i += 1
                while expected[i] == e:
                    i += 1

            elif e > a:
                unexpected.append(a)
                j += 1
                while actual[j] == a:
                    j += 1

            else:
                i += 1
                try:
                    while expected[i] == e:
                        i += 1

                finally:
                    j += 1
                    while actual[j] == a:
                        j += 1

        except IndexError:
            missing.extend(expected[i:])
            unexpected.extend(actual[j:])
            break

    return (missing, unexpected)


def unorderable_list_difference(expected, actual, ignore_duplicate=False):
    missing = []
    unexpected = []
    while expected:
        item = expected.pop()
        try:
            actual.remove(item)
        except ValueError:
            missing.append(item)

        if ignore_duplicate:
            for lst in (expected, actual):
                try:
                    while True:
                        lst.remove(item)

                except ValueError:
                    pass

    if ignore_duplicate:
        while actual:
            item = actual.pop()
            unexpected.append(item)
            try:
                while True:
                    actual.remove(item)

            except ValueError:
                pass

        return (missing, unexpected)
    return (missing, actual)


_Mismatch = namedtuple('Mismatch', 'actual expected value')

def _count_diff_all_purpose(actual, expected):
    s, t = list(actual), list(expected)
    m, n = len(s), len(t)
    NULL = object()
    result = []
    for i, elem in enumerate(s):
        if elem is NULL:
            continue
        cnt_s = cnt_t = 0
        for j in range(i, m):
            if s[j] == elem:
                cnt_s += 1
                s[j] = NULL

        for j, other_elem in enumerate(t):
            if other_elem == elem:
                cnt_t += 1
                t[j] = NULL

        if cnt_s != cnt_t:
            diff = _Mismatch(cnt_s, cnt_t, elem)
            result.append(diff)

    for i, elem in enumerate(t):
        if elem is NULL:
            continue
        cnt_t = 0
        for j in range(i, n):
            if t[j] == elem:
                cnt_t += 1
                t[j] = NULL

        diff = _Mismatch(0, cnt_t, elem)
        result.append(diff)

    return result


def _ordered_count(iterable):
    c = OrderedDict()
    for elem in iterable:
        c[elem] = c.get(elem, 0) + 1

    return c


def _count_diff_hashable(actual, expected):
    s, t = _ordered_count(actual), _ordered_count(expected)
    result = []
    for elem, cnt_s in s.items():
        cnt_t = t.get(elem, 0)
        if cnt_s != cnt_t:
            diff = _Mismatch(cnt_s, cnt_t, elem)
            result.append(diff)

    for elem, cnt_t in t.items():
        if elem not in s:
            diff = _Mismatch(0, cnt_t, elem)
            result.append(diff)

    return result
