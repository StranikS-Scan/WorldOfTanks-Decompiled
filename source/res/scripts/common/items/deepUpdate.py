# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/deepUpdate.py
import collections
import inspect
import itertools
import BigWorld
from Math import Vector2, Vector3
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION

def deepUpdate(dst, src, path=None):
    if path is None:
        path = '/'
    if dst is None or src is None or dst is src:
        return
    elif isinstance(src, collections.Mapping):
        return __deepUpdate_map(dst, src, path)
    elif isinstance(src, basestring):
        return
    elif isinstance(src, collections.Sequence):
        return __deepUpdate_seq(dst, src, path)
    elif isinstance(src, float):
        return __deepUpdate_float(dst, src, path)
    elif isinstance(src, bool):
        return src
    elif isinstance(src, int):
        return src
    elif type(src) == Vector2:
        return __deepUpdate_Vec2v(dst, src, path)
    elif type(src) == Vector3:
        return __deepUpdate_Vec3v(dst, src, path)
    elif type(src) == frozenset:
        return
    elif type(src) == set:
        return
    elif hasattr(src, '__slots__'):
        return __deepUpdate_slots2slots(dst, src, path)
    else:
        return __deepUpdate_map(dst, src.__dict__, path) if hasattr(src, '__dict__') else None


def __deepUpdate_map(dst, src_dict, path):
    if isinstance(dst, collections.Mapping):
        dst_dict = dst
    else:
        if hasattr(dst, '__slots__'):
            return __deepUpdate_dict2slots(dst, src_dict, path)
        if hasattr(dst, '__dict__'):
            dst_dict = dst.__dict__
            path += '.__dict__'
        else:
            LOG_ERROR('Type mismatch: dst is %s  VS src is %s path=%s' % (type(dst), type(src_dict), path))
            return
    for key, src_val in src_dict.iteritems():
        src_ = deepUpdate(dst_dict.get(key), src_val, path + '[%s]' % key)
        if src_ is not None:
            dst_dict[key] = src_

    return


def __deepUpdate_slots2slots(dst, src, path):
    if not hasattr(dst, '__slots__'):
        LOG_ERROR('Type mismatch: dst is %s  VS src is %s path=%s' % (type(dst), type(src), path))
        return
    else:
        for name in __getSpecAttrNames(src):
            src_ = deepUpdate(getattr(dst, name), getattr(src, name), path + '.%s' % name)
            if src_ is not None:
                setattr(dst, name, src_)

        return


def __deepUpdate_dict2slots(dst, src_dict, path):
    dst_names = set(__getSpecAttrNames(dst))
    names = dst_names.intersection(src_dict.keys())
    for name in names:
        src_ = deepUpdate(getattr(dst, name), src_dict[name], path + '.%s' % name)
        if src_ is not None:
            setattr(dst, name, src_)

    return


def __deepUpdate_seq(dst_seq, src_seq, path):
    if isinstance(dst_seq, collections.MutableSequence):
        return __deepUpdate_list(dst_seq, src_seq, path)
    if isinstance(dst_seq, tuple):
        return __deepUpdate_tuple(dst_seq, src_seq, path)
    if isinstance(dst_seq, basestring):
        return
    if type(dst_seq) == Vector2:
        return __deepUpdate_Vec2s(dst_seq, src_seq, path)
    if type(dst_seq) == Vector3:
        return __deepUpdate_Vec2s(dst_seq, src_seq, path)
    LOG_ERROR('Unexpected dst type: %s  VS src is %s path=%s' % (type(dst_seq), type(src_seq), path))


def __deepUpdate_list(dst_lst, src_lst, path):
    dst_len = len(dst_lst)
    for i, src_val in enumerate(src_lst[:dst_len]):
        src_ = deepUpdate(dst_lst[i], src_val, path + '[%d]' % i)
        if src_ is not None:
            dst_lst[i] = src_

    for src_val in src_lst[dst_len:]:
        LOG_WARNING('DeepUpdate ignores', src_val, path)

    return


def __deepUpdate_tuple(dst_tpl, src_lst, path):
    success = True
    failIndices = []
    dst_len = len(dst_tpl)
    for i, src_val in enumerate(src_lst[:dst_len]):
        src_ = deepUpdate(dst_tpl[i], src_val, path + '[%d]' % i)
        if src_ is not None:
            success = False
            failIndices.append(i)
            LOG_DEBUG('DeepUpdate needs wg_PyTuple_SetItem to %s of type %s' % (path + '[%d]' % i, type(dst_tpl[i])))

    for src_val in src_lst[dst_len:]:
        LOG_WARNING('DeepUpdate ignores', src_val, path)

    if success:
        return
    else:
        res = list(dst_tpl)
        for i in failIndices:
            res[i] = src_lst[i]

        return tuple(res)


def __deepUpdate_float(dst_flt, src_flt, path):
    if not isinstance(dst_flt, float):
        LOG_ERROR('Type mismatch: dst is %s  VS src is %s path=%s' % (type(dst_flt), type(src_flt), path))
        return
    return None if dst_flt == src_flt else src_flt


def __deepUpdate_Vec2v(dst_v, src_v, path):
    if type(dst_v) == Vector2:
        dst_v.x = src_v.x
        dst_v.y = src_v.y
    else:
        LOG_ERROR('Type mismatch: dst is %s  VS src is %s path=%s' % (type(dst_v), type(src_v), path))


def __deepUpdate_Vec3v(dst_v, src_v, path):
    if type(dst_v) == Vector3:
        dst_v.x = src_v.x
        dst_v.y = src_v.y
        dst_v.z = src_v.z
    else:
        LOG_ERROR('Type mismatch: dst is %s  VS src is %s path=%s' % (type(dst_v), type(src_v), path))


def __deepUpdate_Vec2s(dst_v, src_seq, path):
    src_len = len(src_seq)
    if src_len < 1:
        return
    else:
        if isinstance(src_seq[0], float):
            dst_v.x = src_seq[0]
        elif src_seq[0] is not None:
            LOG_ERROR('Type mismatch: float  VS src is %s path=%s' % (type(src_seq[0]), path + '[0]'))
        if src_len < 2:
            return
        if isinstance(src_seq[1], float):
            dst_v.y = src_seq[1]
        elif src_seq[1] is not None:
            LOG_ERROR('Type mismatch: float  VS src is %s path=%s' % (type(src_seq[1]), path + '[1]'))
        if src_len > 2:
            LOG_ERROR('Length mismatch: Vec2  VS src %s len=%dpath=%s' % (type(src_seq), src_len, path))
        return


def __deepUpdate_Vec3s(dst_v, src_seq, path):
    src_len = len(src_seq)
    if src_len < 1:
        return
    else:
        if isinstance(src_seq[0], float):
            dst_v.x = src_seq[0]
        elif src_seq[0] is not None:
            LOG_ERROR('Type mismatch: float  VS src is %s path=%s' % (type(src_seq[0]), path + '[0]'))
        if src_len < 2:
            return
        if isinstance(src_seq[1], float):
            dst_v.y = src_seq[1]
        elif src_seq[1] is not None:
            LOG_ERROR('Type mismatch: float  VS src is %s path=%s' % (type(src_seq[1]), path + '[1]'))
        if src_len < 3:
            return
        if isinstance(src_seq[2], float):
            dst_v.z = src_seq[2]
        elif src_seq[2] is not None:
            LOG_ERROR('Type mismatch: float  VS src is %s path=%s' % (type(src_seq[2]), path + '[2]'))
        if src_len > 3:
            LOG_ERROR('Length mismatch: Vec2  VS src %s len=%dpath=%s' % (type(src_seq), src_len, path))
        return


def __getAllSlotNames(obj):
    gen = itertools.chain.from_iterable((cls.__slots__ for cls in inspect.getmro(type(obj)) if hasattr(cls, '__slots__')))
    names = filter(lambda n: hasattr(obj, n), gen)
    return names


def __getSpecAttrNames(obj):
    names = filter(lambda n: not n.startswith('_') and hasattr(obj, n), dir(obj))
    return names
