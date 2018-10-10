# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/live_crc.py
from types import *
import zlib
import cPickle

def _iterDict__skip(x, skip=set()):
    a = list(x.items())
    a.sort()
    for i in a:
        if i[0] not in skip and i[1] is not None:
            yield i[0]
            yield i[1]

    return


def _iterDict2__skip(x, skip=set()):
    a = x.items()
    a.sort()
    for i in a:
        if i[0] not in skip and i[1] is not None:
            yield i

    return


def _iterSet__skip(x, skip=set()):
    a = list(x)
    a.sort()
    for i in a:
        if i not in skip:
            yield i


def _iterList__skip(x, skip=set()):
    for i in x:
        if i not in skip:
            yield i


t2sort__skip = {dict: _iterDict__skip,
 set: _iterSet__skip,
 frozenset: _iterSet__skip,
 list: _iterList__skip,
 tuple: _iterList__skip}

def _iterDict(x):
    a = x.items()
    a.sort()
    for i in a:
        if i[1] is not None:
            yield i[0]
            yield i[1]

    return


def _iterDict2(x):
    a = x.items()
    a.sort()
    for i in a:
        if i[1] is not None:
            yield i

    return


def _iterSet(x):
    a = list(x)
    a.sort()
    for i in a:
        yield i


def _iterList(x):
    for i in x:
        yield i


t2sort = {dict: _iterDict,
 set: _iterSet,
 frozenset: _iterSet,
 list: _iterList,
 tuple: _iterList}

class EnterTagType:
    __hash = hash('\x01Enter\xff')

    def __hash__(self):
        return EnterTagType.__hash

    def __repr__(self):
        pass


class LeaveTagType:
    __hash = hash('\x01Leave\xff')

    def __hash__(self):
        return LeaveTagType.__hash

    def __repr__(self):
        pass


ENTER = EnterTagType()
LEAVE = LeaveTagType()

def iterAny(x):
    iterator = t2sort.get(type(x), True)
    if iterator is True:
        yield x
    else:
        yield ENTER
        for i in iterator(x):
            for j in iterAny(i):
                yield j

        yield LEAVE


def iterAny__skip(x, skip=set()):
    iterator = t2sort__skip.get(type(x), True)
    if iterator is True:
        yield x
    else:
        yield ENTER
        for i in iterator(x, skip):
            for j in iterAny(i):
                yield j

        yield LEAVE


def convert(x):
    iterator = t2sort.get(type(x), True)
    if iterator is True:
        return x
    ret = tuple([ convert(i) for i in iterator(x) ])
    return ret


def convert__skip(x, skip=set()):
    iterator = t2sort__skip.get(type(x), True)
    if iterator is True:
        return x
    ret = tuple([ convert(i) for i in iterator(x, skip) ])
    return ret


def livehashA(x):
    return hash(tuple([ i for i in iterAny(x) ]))


def livehashA__skip(x, skip=set()):
    return hash(tuple([ i for i in iterAny__skip(x, skip) ]))


def livehashC(x):
    return hash(convert(x))


def livehashC__skip(x, skip=set()):
    return hash(convert__skip(x, skip))


def livehash1(x):
    iterator = t2sort.get(type(x), True)
    if iterator is True:
        return hash(x)
    return hash(tuple([ livehash1(i) for i in iterator(x) ]))


def livehash1__skip(x, skip=set()):
    iterator = t2sort__skip.get(type(x), True)
    if iterator is True:
        return hash(x)
    return hash(tuple([ livehash1(i) for i in iterator(x, skip) ]))


def livehash1_combine(*args):
    return hash(args)


def livehashZ(x):
    return zlib.adler32(cPickle.dumps(convert(x), -1))


def livehashZ__skip(x, skip=set()):
    return zlib.adler32(cPickle.dumps(convert__skip(x, skip), -1))


from struct import pack, unpack

def adler32_combine(*sums):
    a, b = (0, 1)
    for n in sums:
        aa, bb = unpack('>HH', pack('>l', n))
        a = (a + aa) % 65521
        b = (b + bb + 65520) % 65521

    return unpack('>l', pack('>HH', a, b))[0]


livehashZ_combine = adler32_combine

def _sortret(a):
    a.sort()
    return a


t2hashable = {dict: lambda x: _sortret(x.items()),
 set: lambda x: _sortret(list(x)),
 frozenset: lambda x: _sortret(list(x)),
 list: lambda x: x,
 tuple: lambda x: x}

def convert2(x):
    iterator = t2hashable.get(type(x), True)
    if iterator is True:
        return x
    return tuple([ livehash2(i) for i in iterator(x) ])


def livehash2(x):
    return hash(convert2(x))


def livehash2i(x):
    iterator = t2hashable.get(type(x), True)
    if iterator is True:
        return x
    return hash(tuple([ livehash2i(i) for i in iterator(x) ]))


livehash = livehashZ
livehash__skip = livehashZ__skip
livehash_combine = livehashZ_combine
livehash_emptyVal = livehash(None)

def livehash__skipDeep_fn1(skip={}):
    if not skip:
        return livehash
    if isinstance(skip, set):
        return lambda data: livehash__skip(data, skip)
    skipThisLevel = set()
    skipNextLevel = []
    for x in skip.items():
        skipThisLevel.add(x[0])
        if isinstance(x[1], dict) or isinstance(x[1], set):
            skipNextLevel.append((x[0], livehash__skipDeep_fn(x[1])))

    return lambda data: livehash_combine(livehash__skip(data, skipThisLevel), *[ (fn(data[k]) if k in data else livehash_emptyVal) for k, fn in skipNextLevel ])


livehash__skipDeep_fn = livehash__skipDeep_fn1

class SelectorType:
    pass


class IncludeType(SelectorType):
    pass


class ExcludeType(SelectorType):
    pass


INCLUDE = IncludeType()
EXCLUDE = ExcludeType()

def __split_use(use):
    includeThisLevel = set(use.get(INCLUDE, set()))
    excludeThisLevel = set(use.get(EXCLUDE, set()))
    useNextLevel = []
    for x in sorted(use.items()):
        if isinstance(x[0], SelectorType):
            continue
        excludeThisLevel.add(x[0])
        includeThisLevel.discard(x[0])
        if isinstance(x[1], dict) or isinstance(x[1], set):
            useNextLevel.append(x)

    return (includeThisLevel, excludeThisLevel, useNextLevel)


def __is_iterable(data):
    return bool(getattr(data, '__iter__', None))


def __addIfPresent(d1, key, d2):
    if key in d1:
        d2[key] = d1[key]


def gen_livehash_fn(use={}):
    if not use:
        return livehash
    if not isinstance(use, dict):
        return livehash
    includeThisLevel, excludeThisLevel, useNextLevel = __split_use(use)
    useNextLevel = [ (x[0], gen_livehash_fn(x[1])) for x in useNextLevel ]
    if includeThisLevel:
        includeThisLevel = sorted(list(includeThisLevel))
        if useNextLevel:
            return lambda data: (livehash_combine(*([ (livehash(data[k]) if k in data else livehash_emptyVal) for k in includeThisLevel ] + [ (fn(data[k]) if k in data else livehash_emptyVal) for k, fn in useNextLevel ])) if __is_iterable(data) else livehash(data))
        else:
            return lambda data: (livehash_combine(*[ (livehash(data[k]) if k in data else livehash_emptyVal) for k in includeThisLevel ]) if __is_iterable(data) else livehash(data))
    elif excludeThisLevel:
        if useNextLevel:
            return lambda data: (livehash_combine(livehash__skip(data, excludeThisLevel), *[ (fn(data[k]) if k in data else livehash_emptyVal) for k, fn in useNextLevel ]) if __is_iterable(data) else livehash(data))
        else:
            return lambda data: livehash__skip(data, excludeThisLevel)
    else:
        return livehash


from copy import copy

def gen_delSubkeys_fn(use={}):
    if not use:
        return lambda data: data
    if not isinstance(use, dict):
        return lambda data: data
    includeThisLevel, excludeThisLevel, useNextLevel = __split_use(use)
    useNextLevel = [ (x[0], gen_delSubkeys_fn(x[1])) for x in useNextLevel ]
    if includeThisLevel:
        if useNextLevel:

            def func(data):
                if isinstance(data, dict):
                    data = copy(data)
                    for k in includeThisLevel:
                        data.pop(k, None)
                        data.pop((k, '_r'), None)
                        data.pop((k, '_d'), None)

                    for k, fn in useNextLevel:
                        data[k] = fn(data[k])

                return data

            return func
        else:

            def func(data):
                if isinstance(data, dict):
                    data = copy(data)
                    for k in includeThisLevel:
                        data.pop(k, None)
                        data.pop((k, '_r'), None)
                        data.pop((k, '_d'), None)

                return data

            return func
    elif excludeThisLevel:
        if useNextLevel:

            def func(data):
                if isinstance(data, dict):
                    data = copy(data)
                    for k in data.keys():
                        if k not in excludeThisLevel:
                            data.pop(k, None)
                            data.pop((k, '_r'), None)
                            data.pop((k, '_d'), None)

                    for k, fn in useNextLevel:
                        data[k] = fn(data[k])

                return data

            return func
        else:

            def func(data):
                if isinstance(data, dict):
                    data = copy(data)
                    for k in data.keys():
                        if k not in excludeThisLevel:
                            data.pop(k, None)
                            data.pop((k, '_r'), None)
                            data.pop((k, '_d'), None)

                return data

            return func
    else:
        return lambda data: data


def gen_mergeCache_fn(overwrite=False):
    if overwrite:

        def _mergeAll_overwrite(data, cache):
            if isinstance(data, set) and (isinstance(cache, set) or isinstance(cache, frozenset)):
                data.update(cache)
                return data
            if not isinstance(data, dict) or not isinstance(cache, dict):
                return cache
            for k, v in cache.items():
                if k in data:
                    d = data[k]
                    if __is_iterable(v) and __is_iterable(d):
                        _mergeAll_overwrite(d, v)
                    else:
                        data[k] = v
                data[k] = v

            return data

        return _mergeAll_overwrite
    else:

        def _mergeAll_nooverwrite(data, cache):
            if isinstance(data, set) and isinstance(data, set):
                data.update(cache)
                return data
            if not isinstance(data, dict) or not isinstance(cache, dict):
                return data
            for k, v in cache.items():
                if k in data:
                    d = data[k]
                    if __is_iterable(v) and __is_iterable(d):
                        _mergeAll_nooverwrite(d, v)
                data[k] = v

            return data

        return _mergeAll_nooverwrite


def gen_extract_fn(use={}):
    if not use:
        return lambda data: data
    if not isinstance(use, dict):
        return lambda data: data
    includeThisLevel, excludeThisLevel, useNextLevel = __split_use(use)
    useNextLevel = [ (x[0], gen_extract_fn(x[1])) for x in useNextLevel ]
    if includeThisLevel:
        if useNextLevel:

            def func(data):
                if not isinstance(data, dict):
                    return data
                ret = {}
                for k in includeThisLevel:
                    __addIfPresent(data, k, ret)

                for k, fn in useNextLevel:
                    if k in data:
                        ret[k] = fn(data[k])

                return ret

            return func
        else:

            def func(data):
                if not isinstance(data, dict):
                    return data
                ret = {}
                for k in includeThisLevel:
                    __addIfPresent(data, k, ret)

                return ret

            return func
    elif excludeThisLevel:
        if useNextLevel:

            def func(data):
                if not isinstance(data, dict):
                    return data
                ret = {}
                for k, v in data.items():
                    if k not in excludeThisLevel:
                        ret[k] = v

                for k, fn in useNextLevel:
                    if k in data:
                        ret[k] = fn(data[k])

                return ret

            return func
        else:

            def func(data):
                if not isinstance(data, dict):
                    return data
                ret = {}
                for k, v in data.items():
                    if k not in excludeThisLevel:
                        ret[k] = v

                return ret

            return func
    else:
        return lambda data: data
