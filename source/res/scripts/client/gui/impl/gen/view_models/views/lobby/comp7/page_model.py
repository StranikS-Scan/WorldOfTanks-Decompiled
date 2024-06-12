# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/page_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Types(IntEnum):
    PAGE = 0
    MAPS = 1
    SEASONVEHICLES = 2


class PageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PageModel, self).__init__(properties=properties, commands=commands)

    def getPageType(self):
        return Types(self._getNumber(0))

    def setPageType(self, value):
        self._setNumber(0, value.value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PageModel, self)._initialize()
        self._addNumberProperty('pageType')
        self._addStringProperty('name', '')
