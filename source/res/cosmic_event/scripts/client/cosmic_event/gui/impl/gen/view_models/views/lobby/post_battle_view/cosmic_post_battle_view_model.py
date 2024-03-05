# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/post_battle_view/cosmic_post_battle_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.cosmic_daily_missions import CosmicDailyMissions
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.player_entry import PlayerEntry

class CosmicPostBattleViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=8, commands=1):
        super(CosmicPostBattleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentPlayerEntry(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentPlayerEntryType():
        return PlayerEntry

    def getBattleOverTimestamp(self):
        return self._getNumber(1)

    def setBattleOverTimestamp(self, value):
        self._setNumber(1, value)

    def getTotalPoints(self):
        return self._getNumber(2)

    def setTotalPoints(self, value):
        self._setNumber(2, value)

    def getKillAmount(self):
        return self._getNumber(3)

    def setKillAmount(self, value):
        self._setNumber(3, value)

    def getPickupAmount(self):
        return self._getNumber(4)

    def setPickupAmount(self, value):
        self._setNumber(4, value)

    def getPlayersList(self):
        return self._getArray(5)

    def setPlayersList(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPlayersListType():
        return PlayerEntry

    def getDailyQuests(self):
        return self._getArray(6)

    def setDailyQuests(self, value):
        self._setArray(6, value)

    @staticmethod
    def getDailyQuestsType():
        return CosmicDailyMissions

    def getHasDailyQuests(self):
        return self._getBool(7)

    def setHasDailyQuests(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(CosmicPostBattleViewModel, self)._initialize()
        self._addViewModelProperty('currentPlayerEntry', PlayerEntry())
        self._addNumberProperty('battleOverTimestamp', 0)
        self._addNumberProperty('totalPoints', 0)
        self._addNumberProperty('killAmount', 0)
        self._addNumberProperty('pickupAmount', 0)
        self._addArrayProperty('playersList', Array())
        self._addArrayProperty('dailyQuests', Array())
        self._addBoolProperty('hasDailyQuests', False)
        self.onClose = self._addCommand('onClose')
