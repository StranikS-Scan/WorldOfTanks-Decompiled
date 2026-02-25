# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/info_page_model.py
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.game_mode_model import GameModeModel

class InfoPageModel(ViewModel):
    __slots__ = ('onOpenVideo', 'onClose')

    def __init__(self, properties=9, commands=2):
        super(InfoPageModel, self).__init__(properties=properties, commands=commands)

    @property
    def modesSH(self):
        return self._getViewModel(0)

    @staticmethod
    def getModesSHType():
        return LeaderboardRewardTooltipModel

    @property
    def eventInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def getStartDate(self):
        return self._getNumber(2)

    def setStartDate(self, value):
        self._setNumber(2, value)

    def getEndDate(self):
        return self._getNumber(3)

    def setEndDate(self, value):
        self._setNumber(3, value)

    def getIsModeSelector(self):
        return self._getBool(4)

    def setIsModeSelector(self, value):
        self._setBool(4, value)

    def getPlatoonTimeToResurrect(self):
        return self._getNumber(5)

    def setPlatoonTimeToResurrect(self, value):
        self._setNumber(5, value)

    def getPlatoonRespawnPeriod(self):
        return self._getNumber(6)

    def setPlatoonRespawnPeriod(self, value):
        self._setNumber(6, value)

    def getSoloRespawnPeriod(self):
        return self._getNumber(7)

    def setSoloRespawnPeriod(self, value):
        self._setNumber(7, value)

    def getModesBP(self):
        return self._getArray(8)

    def setModesBP(self, value):
        self._setArray(8, value)

    @staticmethod
    def getModesBPType():
        return GameModeModel

    def _initialize(self):
        super(InfoPageModel, self)._initialize()
        self._addViewModelProperty('modesSH', LeaderboardRewardTooltipModel())
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isModeSelector', False)
        self._addNumberProperty('platoonTimeToResurrect', 0)
        self._addNumberProperty('platoonRespawnPeriod', 0)
        self._addNumberProperty('soloRespawnPeriod', 0)
        self._addArrayProperty('modesBP', Array())
        self.onOpenVideo = self._addCommand('onOpenVideo')
        self.onClose = self._addCommand('onClose')
