# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/filter_status_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_base_model import FilterStatusBaseModel

class FilterStatusModel(FilterStatusBaseModel):
    __slots__ = ()
    SIMPLE = 'simple'
    DIVIDER = 'divider'

    def __init__(self, properties=5, commands=0):
        super(FilterStatusModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getIsResetAvailable(self):
        return self._getBool(3)

    def setIsResetAvailable(self, value):
        self._setBool(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(FilterStatusModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addBoolProperty('isResetAvailable', False)
        self._addStringProperty('type', '')
