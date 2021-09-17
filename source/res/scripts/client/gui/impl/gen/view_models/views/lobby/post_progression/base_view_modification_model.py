# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/base_view_modification_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.post_progression.base_modification_model import BaseModificationModel

class BaseViewModificationModel(BaseModificationModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BaseViewModificationModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getTitleRes(self):
        return self._getResource(2)

    def setTitleRes(self, value):
        self._setResource(2, value)

    def getTooltipContentId(self):
        return self._getNumber(3)

    def setTooltipContentId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BaseViewModificationModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('titleRes', R.invalid())
        self._addNumberProperty('tooltipContentId', 0)
