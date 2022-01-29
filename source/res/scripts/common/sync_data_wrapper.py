# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/sync_data_wrapper.py
import marshal
from copy import deepcopy
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

class Storage(object):

    def __init__(self, key, data):
        self.key = key
        self.data = data


class UpdatebleStorage(Storage):

    @staticmethod
    def _createWrapper(wrapped, key, child):
        base = wrapped if wrapped._fastBase is None else wrapped._fastBase
        if isinstance(child, dict):
            return DictWrapper(wrapped, key, child, base=base)
        elif isinstance(child, list):
            return ListWrapper(wrapped, key, child, base=base)
        else:
            return SetWrapper(wrapped, key, child, base=base) if isinstance(child, set) else None

    def __getitem__(self, key):
        return self._createWrapper(self, key, self.data[key])

    def __setitem__(self, key, value):
        pass


class DiffBase(object):

    def propagateDiff(self, child):
        pass

    def placement(self):
        pass

    def deepcopy(self, data):
        pass

    def onDataChange(self):
        pass


class DictDiff(DiffBase):

    def __init__(self, parentDiff, onDataChange, copier=marshal, **kwargs):
        super(DictDiff, self).__init__(**kwargs)
        self._parentDiff = parentDiff
        self._onDataChange = onDataChange
        self._copier = copier

    def deepcopy(self, data):
        if hasattr(data, '__fast_copy__'):
            return data.__fast_copy__()
        copier = self._copier
        if copier:
            try:
                return copier.loads(copier.dumps(data))
            except Exception as e:
                LOG_CURRENT_EXCEPTION()
                LOG_ERROR("{} module can't dumps the data {}. Deepcopy will be used instead. Error [{}]".format(copier, data, e))

        return deepcopy(data)

    def onDataChange(self):
        if self._onDataChange:
            self._onDataChange()

    def propagateDiff(self, child):
        return self._parentDiff.setdefault(child.key, child.placement())


class Decorator(DiffBase):

    def __init__(self, parent, base=None, **kwargs):
        super(Decorator, self).__init__(**kwargs)
        self._parent = parent
        self._fastBase = parent if base is None else base
        return

    @property
    def parent(self):
        return self._parent

    def onDataChange(self):
        self._fastBase.onDataChange()

    def deepcopy(self, data):
        return self._fastBase.deepcopy(data)

    def propagateDiff(self, child):
        return self.parent.propagateDiff(child)


class DictWrapper(Decorator, UpdatebleStorage):

    def __init__(self, parent, key, data, **kwargs):
        super(DictWrapper, self).__init__(parent=parent, key=key, data=data, **kwargs)

    def __setitem__(self, key, value):
        diff = Decorator.propagateDiff(self, self)
        diff[key] = self.deepcopy(value)
        self.data[key] = value
        self.onDataChange()

    def propagateDiff(self, child):
        diff = Decorator.propagateDiff(self, self)
        return diff.setdefault(child.key, child.placement())

    def __delitem__(self, key):
        self.pop(key, None)
        return

    def get(self, key, default=None):
        return default if key not in self.data else self.__getitem__(key)

    def setdefault(self, key, default):
        if key not in self.data:
            self.__setitem__(key, default)
        return self.__getitem__(key)

    def pop(self, key, default=None):
        if key not in self.data:
            return default
        else:
            diff = Decorator.propagateDiff(self, self)
            diff[key] = None
            ret = self.data.pop(key)
            self.onDataChange()
            return ret

    def update(self, data):
        diff = Decorator.propagateDiff(self, self)
        diff.update(self.deepcopy(data))
        self.data.update(data)
        self.onDataChange()

    def placement(self):
        return {}


_UPD = 0
_INS = 1
_RM = 2
_OP_MSK = _UPD | _INS | _RM

class ListWrapper(Decorator, UpdatebleStorage):

    @staticmethod
    def createIdx(idx, op=_UPD):
        return idx << 2 | op

    def __init__(self, parent, key, data, **kwargs):
        super(ListWrapper, self).__init__(parent=parent, key=key, data=data, **kwargs)

    def __setitem__(self, idx, value):
        diff = Decorator.propagateDiff(self, self)
        if self.data == diff:
            diff[idx] = self.deepcopy(value)
        else:
            diff.append((self.createIdx(idx), self.deepcopy(value)))
        self.data[idx] = value
        self.onDataChange()

    def propagateDiff(self, child):
        diff = Decorator.propagateDiff(self, self)
        if self.data == diff:
            return diff[child.key]
        updIdx = self.createIdx(child.key)
        if len(diff):
            upd = dict(diff)
            if updIdx in upd:
                return upd[updIdx]
        place = child.placement()
        diff.append((updIdx, place))
        return place

    def append(self, value):
        self.insert(len(self.data), value)

    def insert(self, idx, value):
        diff = Decorator.propagateDiff(self, self)
        if self.data == diff:
            diff.append(self.deepcopy(value))
        else:
            diff.append((self.createIdx(idx, _INS), self.deepcopy(value)))
        self.data.insert(idx, value)
        self.onDataChange()

    def pop(self, idx):
        diff = Decorator.propagateDiff(self, self)
        if self.data == diff:
            diff.pop(idx)
        else:
            diff.append((self.createIdx(idx, _RM), None))
        ret = self.data.pop(idx)
        self.onDataChange()
        return ret

    def placement(self):
        return []


_SET_ADD = '_a'
_SET_DISCARD = '_d'

class SetWrapper(Decorator, Storage):

    def __init__(self, parent, key, data, **kwargs):
        super(SetWrapper, self).__init__(parent=parent, key=key, data=data, **kwargs)

    def placement(self):
        return set()

    def add(self, value):
        diff = Decorator.propagateDiff(self, DictWrapper(self.parent, self.key, {}))
        if self.data == diff:
            diff.add(value)
        else:
            val_d = diff.get((self.key, _SET_DISCARD), None)
            if val_d and value in val_d:
                val_d.discard(value)
            else:
                diff.setdefault((self.key, _SET_ADD), set()).add(value)
        self.data.add(value)
        self.onDataChange()
        return

    def discard(self, value):
        diff = Decorator.propagateDiff(self, DictWrapper(self.parent, self.key, {}))
        if self.data == diff:
            diff.discard(value)
        else:
            val_d = diff.get((self.key, _SET_ADD), None)
            if val_d and value in val_d:
                val_d.discard(value)
            else:
                diff.setdefault((self.key, _SET_DISCARD), set()).add(value)
        self.data.discard(value)
        self.onDataChange()
        return


def _listUnmarshal(idx, value, cache):
    if isinstance(value, dict):
        unmarshal(value, cache[idx])
    elif isinstance(value, list):
        for lstIdx, lstValue in enumerate(value):
            _listUnmarshal(idx, lstValue, cache[idx])

    elif isinstance(value, tuple):
        idxOp, lstValue = value
        op = idxOp & _OP_MSK
        idxOp = idxOp >> 2
        if op == _UPD:
            _listUnmarshal(idxOp, lstValue, cache)
        elif op == _INS:
            cache.insert(idxOp, lstValue)
        elif op == _RM:
            cache.pop(idxOp)
    elif isinstance(value, set):
        cache.setdefault(idx, set()).update(value)
    else:
        cache[idx] = value


def unmarshal(diff, cache):
    for key_u in diff.iterkeys():
        value = diff[key_u]
        if value is None:
            cache.pop(key_u, None)
        if isinstance(value, dict) and value:
            unmarshal(value, cache.setdefault(key_u, {}))
        if isinstance(value, list) and len(value) > 0:
            for idx, lstValue in enumerate(value):
                if not isinstance(lstValue, tuple):
                    cache[key_u] = value
                    break
                _listUnmarshal(idx, lstValue, cache.setdefault(key_u, []))

        if isinstance(value, set):
            if isinstance(key_u, tuple):
                if key_u[1] == _SET_ADD:
                    cache.update(value)
                elif key_u[1] == _SET_DISCARD:
                    cache.difference_update(value)
            else:
                cache.setdefault(key_u, set()).update(value)
        cache[key_u] = value

    return
