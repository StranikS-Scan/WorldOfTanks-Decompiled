# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/base.py
from collections import defaultdict, namedtuple
import inspect
import operator
from debug_utils import LOG_WARNING
from gui.shared.utils.decorators import ReprInjector

class StatsComponent(object):
    __slots__ = ()

    def clone(self, *exclude):
        raise NotImplementedError

    def clear(self):
        pass

    def addComponent(self, index, component):
        raise NotImplementedError

    def getComponent(self, index):
        raise NotImplementedError

    def getRecordPath(self):
        raise NotImplementedError

    def setRecord(self, record, reusable):
        raise NotImplementedError

    def getField(self):
        raise NotImplementedError

    def getVO(self):
        raise NotImplementedError


class StatsComponentError(Exception):
    pass


@ReprInjector.simple(('_field', 'field'))
class StatsItem(StatsComponent):
    __slots__ = ('_field', '_value', '_path')

    def __init__(self, field, *path):
        super(StatsItem, self).__init__()
        self._field = field
        self._path = path
        self._value = None
        return

    def clone(self):
        return self.__class__(self._field, *self._path)

    def addComponent(self, index, component):
        raise ValueError('StatsItem is not supported method addComponent')

    def getComponent(self, index):
        raise ValueError('StatsItem is not supported method getComponent')

    def getRecordPath(self):
        return self._path

    def setRecord(self, record, reusable):
        if record is not None:
            self._value = self._convert(record, reusable)
        else:
            self._value = None
        return

    def getField(self):
        return self._field

    def getVO(self):
        return self._value

    def _convert(self, value, reusable):
        return value


class DirectStatsItem(StatsItem):
    __slots__ = ('_value',)

    def __init__(self, field, value=None):
        super(DirectStatsItem, self).__init__(field)
        self._value = value

    def clone(self):
        return self.__class__(self._field, value=self._value)

    def setRecord(self, record, reusable):
        self._value = record


class VOMeta(object):
    __slots__ = ('_meta',)

    def __init__(self, meta):
        super(VOMeta, self).__init__()
        self._meta = meta

    def clone(self):
        return self.__class__(self._meta)

    def bind(self, clazz):
        setattr(clazz, '__vo_meta__', self.clone())

    def getDefault(self, field):
        return None

    def isComponentGenerated(self, index):
        return False

    def registerComponent(self, component):
        pass

    def generateComponents(self):
        pass

    def generateVO(self, components):
        raise NotImplementedError


class DictMeta(VOMeta):
    __slots__ = ('_auto', '_unregistered')

    def __init__(self, meta=None, auto=None):
        if meta is None:
            meta = {}
        super(DictMeta, self).__init__(meta)
        self._auto = auto or ()
        self._unregistered = set(meta.keys())
        return

    def clone(self):
        auto = []
        for index, component in self._auto:
            auto.append((index, component.clone()))

        return DictMeta(self._meta, auto)

    def getDefault(self, field):
        return self._meta.get(field)

    def isComponentGenerated(self, index):
        return index in map(operator.itemgetter(0), self._auto)

    def registerComponent(self, component):
        field = component.getField()
        if field:
            if field not in self._meta:
                raise StatsComponentError('Field {} is not found in meta {}'.format(field, self._meta))
            if field not in self._unregistered:
                raise StatsComponentError('Component is already set to field {}'.format(field))
            self._unregistered.discard(field)

    def generateComponents(self):
        for idx, component in self._auto:
            yield (idx, component)

    def generateVO(self, components):
        vo = {}
        for field in self._unregistered:
            vo[field] = self.getDefault(field)

        for component in components:
            if component is None:
                continue
            field = component.getField()
            value = component.getVO()
            if field:
                if value is not None:
                    vo[field] = value
                else:
                    vo[field] = self._meta[field]
            if value is not None:
                vo.update(value)

        return vo


class ListMeta(VOMeta):
    __slots__ = ('_registered', '_runtime')

    def __init__(self, meta=None, registered=False, runtime=True):
        super(ListMeta, self).__init__(meta or [])
        self._registered = registered
        self._runtime = runtime

    def getDefault(self, field):
        return None

    def isComponentGenerated(self, index):
        return not self._runtime

    def registerComponent(self, component):
        self._registered = True

    def generateVO(self, components):
        if not self._registered:
            return self._meta[:]
        vo = []
        for component in components:
            vo.append(component.getVO())

        return vo


def _getPropertyGetter(idx):

    def _getter(self):
        component = self.getComponent(idx)
        return component.getVO() if component is not None else None

    return _getter


def _getPropertySetter(idx):

    def _setter(self, value):
        component = self.getComponent(idx)
        if component is not None:
            if isinstance(value, PropertyValue):
                component.setRecord(value.record, value.reusable)
            else:
                component.setRecord(value, None)
        return

    return _setter


PropertyValue = namedtuple('PropertyValue', 'record reusable')

class PropertyMeta(DictMeta):
    __slots__ = ('_bind',)

    def __init__(self, meta):
        if not isinstance(meta, tuple):
            raise StatsComponentError('Meta must be tuple')
        converted = {}
        self._bind = []
        for idx, item in enumerate(meta):
            if not isinstance(item, tuple):
                raise StatsComponentError('Each item must be tuple in meta')
            length = len(item)
            if length > 1:
                field, default = item[:2]
                converted[field] = default
                if length > 2:
                    self._bind.append((idx,
                     field,
                     item[2],
                     default))
            raise StatsComponentError('Number of items must be more than 1')

        super(PropertyMeta, self).__init__(converted)

    def clone(self):
        auto = []
        for index, component in self.generateComponents():
            auto.append((index, component))

        return DictMeta(self._meta, auto)

    def bind(self, clazz):
        super(PropertyMeta, self).bind(clazz)
        slots = set()
        for parent in inspect.getmro(clazz):
            slots = slots.union(getattr(parent, '__slots__', ()))

        if not slots:
            raise StatsComponentError('__slots__ must be defined in stats component {}'.format(clazz))
        for idx, _, attribute, _ in self._bind:
            if attribute not in slots:
                raise StatsComponentError('Attribute {} is not found in __slots__ for {}'.format(attribute, clazz))
            setattr(clazz, attribute, property(_getPropertyGetter(idx), _getPropertySetter(idx)))

    def generateComponents(self):
        for idx, field, _, default in self._bind:
            if isinstance(default, StatsComponent):
                yield (idx, default.clone())
            yield (idx, DirectStatsItem(field, default))


@ReprInjector.simple(('_field', 'field'), ('_path', 'path'))
class StatsBlock(StatsComponent):
    __slots__ = ('_meta', '_components', '_field', '_path', '_records')
    __vo_meta__ = None

    def __init__(self, meta=None, field='', *path):
        super(StatsBlock, self).__init__()
        if meta is None and self.__vo_meta__ is not None:
            meta = self.__vo_meta__
        if isinstance(meta, VOMeta):
            self._meta = meta.clone()
        else:
            raise StatsComponentError('Type of meta must be VOMeta. Received type is {}'.format(type(meta)))
        self._components = []
        self._field = field
        self._path = path
        self._records = defaultdict(list)
        for index, component in self._meta.generateComponents():
            self.addComponent(index, component)

        return

    def clone(self, *exclude):
        block = self.__class__(self._meta.clone(), self._field, *self._path)
        for index, component in enumerate(self._components):
            if index in exclude or self._meta.isComponentGenerated(index):
                continue
            if component is not None:
                block.addComponent(index, component.clone())

        return block

    def addComponent(self, index, component):
        if index < 0:
            raise StatsComponentError('Index must be positive. Received index is {}'.format(index))
        while index > len(self._components) - 1:
            self._components.append(None)

        if self._components[index] is not None:
            raise StatsComponentError('Component is already set to position {}'.format(index))
        self._meta.registerComponent(component)
        self._records[component.getRecordPath()].append(index)
        self._components[index] = component
        return

    def getComponent(self, index):
        return self._components[index] if -1 < index < len(self._components) else None

    def addNextComponent(self, component):
        self.addComponent(self.getNextComponentIndex(), component)

    def getNextComponentIndex(self):
        return len(self._components)

    def getRecordPath(self):
        return self._path

    def setRecord(self, result, reusable):
        bypass = sorted(self._records.iteritems(), key=lambda item: len(item[0]))
        for path, idxs in bypass:
            record = result
            for sub in path:
                if sub in record:
                    record = record[sub]
                LOG_WARNING('Path of record is not found', path)
                record = None

            for idx in idxs:
                component = self._components[idx]
                if component is not None:
                    component.setRecord(record, reusable)

        return

    def getField(self):
        return self._field

    def getVO(self):
        return self._meta.generateVO(self._components)
