# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/prestige/prestige_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class PrestigeBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PrestigeBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def emblem(self):
        return self._getViewModel(0)

    @staticmethod
    def getEmblemType():
        return PrestigeEmblemModel

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getMaxProgress(self):
        return self._getNumber(2)

    def setMaxProgress(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PrestigeBaseModel, self)._initialize()
        self._addViewModelProperty('emblem', PrestigeEmblemModel())
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
