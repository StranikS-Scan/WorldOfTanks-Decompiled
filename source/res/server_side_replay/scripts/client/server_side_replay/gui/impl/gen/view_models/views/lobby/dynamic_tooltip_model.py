# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/dynamic_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class DynamicTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DynamicTooltipModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getResource(0)

    def setHeader(self, value):
        self._setResource(0, value)

    def getBody(self):
        return self._getResource(1)

    def setBody(self, value):
        self._setResource(1, value)

    def getContentId(self):
        return self._getNumber(2)

    def setContentId(self, value):
        self._setNumber(2, value)

    def getTargetId(self):
        return self._getNumber(3)

    def setTargetId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(DynamicTooltipModel, self)._initialize()
        self._addResourceProperty('header', R.invalid())
        self._addResourceProperty('body', R.invalid())
        self._addNumberProperty('contentId', 0)
        self._addNumberProperty('targetId', 0)
