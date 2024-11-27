# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/quests/ny_quests_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quest_card_model import NyQuestCardModel

class NyQuestsModel(ViewModel):
    __slots__ = ('onQuestHover', 'onReplayVideo', 'onVideoFinished')

    def __init__(self, properties=9, commands=3):
        super(NyQuestsModel, self).__init__(properties=properties, commands=commands)

    def getVideoUrl(self):
        return self._getResource(0)

    def setVideoUrl(self, value):
        self._setResource(0, value)

    def getSoundUrl(self):
        return self._getResource(1)

    def setSoundUrl(self, value):
        self._setResource(1, value)

    def getMinVehicleLevel(self):
        return self._getNumber(2)

    def setMinVehicleLevel(self, value):
        self._setNumber(2, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(3)

    def setMaxVehicleLevel(self, value):
        self._setNumber(3, value)

    def getBattleMode(self):
        return self._getArray(4)

    def setBattleMode(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBattleModeType():
        return unicode

    def getResetDailyTimeLeft(self):
        return self._getNumber(5)

    def setResetDailyTimeLeft(self, value):
        self._setNumber(5, value)

    def getResetWeeklyTimeLeft(self):
        return self._getNumber(6)

    def setResetWeeklyTimeLeft(self, value):
        self._setNumber(6, value)

    def getDailyQuests(self):
        return self._getArray(7)

    def setDailyQuests(self, value):
        self._setArray(7, value)

    @staticmethod
    def getDailyQuestsType():
        return NyQuestCardModel

    def getWeeklyQuests(self):
        return self._getArray(8)

    def setWeeklyQuests(self, value):
        self._setArray(8, value)

    @staticmethod
    def getWeeklyQuestsType():
        return NyQuestCardModel

    def _initialize(self):
        super(NyQuestsModel, self)._initialize()
        self._addResourceProperty('videoUrl', R.invalid())
        self._addResourceProperty('soundUrl', R.invalid())
        self._addNumberProperty('minVehicleLevel', 1)
        self._addNumberProperty('maxVehicleLevel', 11)
        self._addArrayProperty('battleMode', Array())
        self._addNumberProperty('resetDailyTimeLeft', 0)
        self._addNumberProperty('resetWeeklyTimeLeft', 0)
        self._addArrayProperty('dailyQuests', Array())
        self._addArrayProperty('weeklyQuests', Array())
        self.onQuestHover = self._addCommand('onQuestHover')
        self.onReplayVideo = self._addCommand('onReplayVideo')
        self.onVideoFinished = self._addCommand('onVideoFinished')
