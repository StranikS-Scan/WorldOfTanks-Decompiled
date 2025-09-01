# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view_model.py
import logging
from contextlib import contextmanager
import typing as t
from soft_exception import SoftException
from .command import Command
from .array import Array
from .map import Map
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectViewModel
if t.TYPE_CHECKING:
    from types import TracebackType
T = t.TypeVar('T', bound='ViewModel')
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class ViewModel(PyObjectEntity):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(ViewModel, self).__init__(PyObjectViewModel(properties, commands))

    def __repr__(self):
        return '{}(fields={})'.format(self.__class__.__name__, self.proxy.toString() if self.proxy is not None else None)

    def __str__(self):
        return self.proxy.toString()

    def __enter__(self):
        self.proxy.hold()
        return self

    def __exit__(self, excType, _, traceback):
        if excType is None:
            self.proxy.commit()
        else:
            self.proxy.rollback()
        return False

    def hold(self):
        self.proxy.hold()

    def commit(self):
        self.proxy.commit()

    def rollback(self):
        self.proxy.rollback()

    @contextmanager
    def transaction(self):
        self.hold()
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def _bind(self, cppObject):
        super(ViewModel, self)._bind(cppObject)
        self._initialize()

    def _unbind(self):
        self._finalize()
        super(ViewModel, self)._unbind()

    def _getValue(self, index, propertyType):
        _logger.warning('Method "_getValue" can be used for debug only.')
        return self.proxy.getValue(index, propertyType)

    def _getNumber(self, index):
        return self.proxy.getNumber(index)

    def _getReal(self, index):
        return self.proxy.getReal(index)

    def _getBool(self, index):
        return self.proxy.getBool(index)

    def _getString(self, index):
        return self.proxy.getString(index)

    def _getViewModel(self, index):
        return self.proxy.getViewModel(index)

    def _getView(self, index):
        return self.proxy.getView(index)

    def _getArray(self, index):
        return self.proxy.getArray(index)

    def _getMap(self, index):
        return self.proxy.getMap(index)

    def _getResource(self, index):
        return self.proxy.getResource(index)

    def _setValue(self, index, propertyType, value):
        _logger.warning('Method "_setValue" can be used for debug only.')
        self.proxy.setValue(index, propertyType, value)

    def _setNumber(self, index, value):
        self.proxy.setNumber(index, int(value))

    def _setReal(self, index, value):
        self.proxy.setReal(index, value)

    def _setBool(self, index, value):
        self.proxy.setBool(index, value)

    def _setString(self, index, value):
        self.proxy.setString(index, value)

    def _setViewModel(self, index, value):
        self.proxy.setViewModel(index, value.proxy)

    def _setView(self, index, pyValue):
        raise SoftException('Property with type ValueType.VIEW is not longer supported. Use View.setChildView method to add sub views.')

    def _setArray(self, index, value):
        self.proxy.setArray(index, value.proxy)

    def _setMap(self, index, value):
        self.proxy.setMap(index, value.proxy)

    def _setResource(self, index, value):
        return self.proxy.setResource(index, value)

    def _addProperty(self, name, propertyType, defaultValue):
        self.proxy.addField(name, propertyType, defaultValue)

    def _addPropertyAsPyObjectEntity(self, name, propertyType, pyValue=None):
        if pyValue is not None:
            proxy = pyValue.proxy
        else:
            proxy = None
        self.proxy.addField(name, propertyType, proxy)
        return

    def _addNumberProperty(self, name, defaultValue=0):
        self.proxy.addNumberField(name, defaultValue)

    def _addRealProperty(self, name, defaultValue=0.0):
        self.proxy.addRealField(name, defaultValue)

    def _addBoolProperty(self, name, defaultValue=False):
        self.proxy.addBoolField(name, defaultValue)

    def _addStringProperty(self, name, defaultValue=''):
        self.proxy.addStringField(name, defaultValue)

    def _addViewModelProperty(self, name, defaultValue):
        self.proxy.addViewModelField(name, defaultValue.proxy)

    def _addViewProperty(self, name, defaultValue=None):
        raise SoftException('Property with type ValueType.VIEW is not longer supported. Use View.setChildView method to add sub views.')

    def _addArrayProperty(self, name, defaultValue=None):
        if defaultValue is None:
            defaultValue = Array()
        self.proxy.addArrayField(name, defaultValue.proxy)
        return

    def _addMapProperty(self, name, value):
        self.proxy.addMapField(name, value.proxy)

    def _addResourceProperty(self, name, defaultValue):
        self.proxy.addResourceField(name, defaultValue)

    def _addCommand(self, name):
        cmd = Command()
        self.proxy.addCommand(name, cmd.proxy)
        return cmd

    def _initialize(self):
        pass

    def _finalize(self):
        pass
