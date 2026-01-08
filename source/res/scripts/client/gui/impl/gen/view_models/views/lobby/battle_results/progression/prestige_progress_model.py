# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/prestige_progress_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class PrestigeProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/post_battle/elite_system/elite_system.js'

    def __init__(self, properties=11, commands=1):
        super(PrestigeProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentPrestigeEmblemModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentPrestigeEmblemModelType():
        return PrestigeEmblemModel

    @property
    def oldPrestigeEmblemModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getOldPrestigeEmblemModelType():
        return PrestigeEmblemModel

    def getVehCD(self):
        return self._getNumber(2)

    def setVehCD(self, value):
        self._setNumber(2, value)

    def getOldLvl(self):
        return self._getNumber(3)

    def setOldLvl(self, value):
        self._setNumber(3, value)

    def getNewLvl(self):
        return self._getNumber(4)

    def setNewLvl(self, value):
        self._setNumber(4, value)

    def getCurrentXP(self):
        return self._getNumber(5)

    def setCurrentXP(self, value):
        self._setNumber(5, value)

    def getCurrentNextLevelXP(self):
        return self._getNumber(6)

    def setCurrentNextLevelXP(self, value):
        self._setNumber(6, value)

    def getOldXP(self):
        return self._getNumber(7)

    def setOldXP(self, value):
        self._setNumber(7, value)

    def getOldNextLvlXP(self):
        return self._getNumber(8)

    def setOldNextLvlXP(self, value):
        self._setNumber(8, value)

    def getGainedXP(self):
        return self._getNumber(9)

    def setGainedXP(self, value):
        self._setNumber(9, value)

    def getIsNavigationEnabled(self):
        return self._getBool(10)

    def setIsNavigationEnabled(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(PrestigeProgressModel, self)._initialize()
        self._addViewModelProperty('currentPrestigeEmblemModel', PrestigeEmblemModel())
        self._addViewModelProperty('oldPrestigeEmblemModel', PrestigeEmblemModel())
        self._addNumberProperty('vehCD', 0)
        self._addNumberProperty('oldLvl', 0)
        self._addNumberProperty('newLvl', 0)
        self._addNumberProperty('currentXP', 0)
        self._addNumberProperty('currentNextLevelXP', 0)
        self._addNumberProperty('oldXP', 0)
        self._addNumberProperty('oldNextLvlXP', 0)
        self._addNumberProperty('gainedXP', 0)
        self._addBoolProperty('isNavigationEnabled', False)
        self.onNavigate = self._addCommand('onNavigate')
