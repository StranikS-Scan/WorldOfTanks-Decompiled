# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/game_board_view_model.py
from frameworks.wulf import Array
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import HintState
from frameworks.wulf import ViewModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.chapter_model import ChapterModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.mission_model import MissionModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.rewards_model import RewardsModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.tank_card_model import TankCardModel

class GameBoardViewModel(ViewModel):
    __slots__ = ('onClose', 'onNextStep', 'onSwitchChapter', 'onCompletedMissionShown', 'onUpdateContentModel', 'onChangeTank', 'onShowGameBoardInfo', 'onOpenStylePreview', 'onHintViewed')

    def __init__(self, properties=16, commands=9):
        super(GameBoardViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedVehicleIntCD(self):
        return self._getNumber(0)

    def setSelectedVehicleIntCD(self, value):
        self._setNumber(0, value)

    def getChapters(self):
        return self._getArray(1)

    def setChapters(self, value):
        self._setArray(1, value)

    @staticmethod
    def getChaptersType():
        return ChapterModel

    def getCurrentChapter(self):
        return self._getNumber(2)

    def setCurrentChapter(self, value):
        self._setNumber(2, value)

    def getIsTabSwitching(self):
        return self._getBool(3)

    def setIsTabSwitching(self, value):
        self._setBool(3, value)

    def getChapterStartDate(self):
        return self._getNumber(4)

    def setChapterStartDate(self, value):
        self._setNumber(4, value)

    def getChapterFinishDate(self):
        return self._getNumber(5)

    def setChapterFinishDate(self, value):
        self._setNumber(5, value)

    def getCurrentStep(self):
        return self._getNumber(6)

    def setCurrentStep(self, value):
        self._setNumber(6, value)

    def getMaxStep(self):
        return self._getNumber(7)

    def setMaxStep(self, value):
        self._setNumber(7, value)

    def getPrevPoints(self):
        return self._getNumber(8)

    def setPrevPoints(self, value):
        self._setNumber(8, value)

    def getPoints(self):
        return self._getNumber(9)

    def setPoints(self, value):
        self._setNumber(9, value)

    def getIsLastDay(self):
        return self._getBool(10)

    def setIsLastDay(self, value):
        self._setBool(10, value)

    def getMissions(self):
        return self._getArray(11)

    def setMissions(self, value):
        self._setArray(11, value)

    @staticmethod
    def getMissionsType():
        return MissionModel

    def getRewards(self):
        return self._getArray(12)

    def setRewards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getRewardsType():
        return RewardsModel

    def getTankCards(self):
        return self._getArray(13)

    def setTankCards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getTankCardsType():
        return TankCardModel

    def getHintState(self):
        return HintState(self._getString(14))

    def setHintState(self, value):
        self._setString(14, value.value)

    def getIsHintVisible(self):
        return self._getBool(15)

    def setIsHintVisible(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(GameBoardViewModel, self)._initialize()
        self._addNumberProperty('selectedVehicleIntCD', 0)
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('currentChapter', 0)
        self._addBoolProperty('isTabSwitching', False)
        self._addNumberProperty('chapterStartDate', 0)
        self._addNumberProperty('chapterFinishDate', 0)
        self._addNumberProperty('currentStep', 0)
        self._addNumberProperty('maxStep', 0)
        self._addNumberProperty('prevPoints', 0)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('isLastDay', False)
        self._addArrayProperty('missions', Array())
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('tankCards', Array())
        self._addStringProperty('hintState', HintState.NONE.value)
        self._addBoolProperty('isHintVisible', False)
        self.onClose = self._addCommand('onClose')
        self.onNextStep = self._addCommand('onNextStep')
        self.onSwitchChapter = self._addCommand('onSwitchChapter')
        self.onCompletedMissionShown = self._addCommand('onCompletedMissionShown')
        self.onUpdateContentModel = self._addCommand('onUpdateContentModel')
        self.onChangeTank = self._addCommand('onChangeTank')
        self.onShowGameBoardInfo = self._addCommand('onShowGameBoardInfo')
        self.onOpenStylePreview = self._addCommand('onOpenStylePreview')
        self.onHintViewed = self._addCommand('onHintViewed')
