# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view_model.py
import logging
from contextlib import contextmanager
import typing
from soft_exception import SoftException
from .command import Command
from .array import Array
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectViewModel
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class ViewModel(PyObjectEntity):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(ViewModel, self).__init__(PyObjectViewModel(properties, commands))

    def hold(self):
        self.proxy.hold()

    def commit(self):
        self.proxy.commit()

    def rollback(self):
        self.proxy.rollback()

    @contextmanager
    def transaction(self):
        self.hold()
        yield self
        self.commit()

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
        raise SoftException('Property with type PropertyType.VIEW is not longer supported. Use View.setChildView method to add sub views.')

    def _setArray(self, index, value):
        self.proxy.setArray(index, value.proxy)

    def _setResource(self, index, value):
        return self.proxy.setResource(index, value)

    def _addProperty(self, name, propertType, defaultValue):
        self.proxy.addField(name, propertType, defaultValue)

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
        raise SoftException('Property with type PropertyType.VIEW is not longer supported. Use View.setChildView method to add sub views.')

    def _addArrayProperty(self, name, defaultValue=None):
        if defaultValue is None:
            defaultValue = Array()
        self.proxy.addArrayField(name, defaultValue.proxy)
        return

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
