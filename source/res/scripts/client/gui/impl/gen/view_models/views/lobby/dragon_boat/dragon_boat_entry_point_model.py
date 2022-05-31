# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dragon_boat/dragon_boat_entry_point_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dragon_boat.quest_model import QuestModel

class DragonBoatEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)
    STATE_NOT_STARTED = 0
    STATE_START = 1
    STATE_FINISH = 2
    STATE_END = 3
    TEAM_1 = 1
    TEAM_2 = 2
    TEAM_3 = 3
    TEAM_4 = 4
    TEAM_5 = 5

    def __init__(self, properties=9, commands=1):
        super(DragonBoatEntryPointModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressDay(self):
        return self._getViewModel(0)

    @property
    def progressWeek(self):
        return self._getViewModel(1)

    def getState(self):
        return self._getNumber(2)

    def setState(self, value):
        self._setNumber(2, value)

    def getTeam(self):
        return self._getNumber(3)

    def setTeam(self, value):
        self._setNumber(3, value)

    def getTimeTillNextDayUpdate(self):
        return self._getNumber(4)

    def setTimeTillNextDayUpdate(self, value):
        self._setNumber(4, value)

    def getFormattedTimeTillNextUpdate(self):
        return self._getString(5)

    def setFormattedTimeTillNextUpdate(self, value):
        self._setString(5, value)

    def getIsDayQuestObtained(self):
        return self._getBool(6)

    def setIsDayQuestObtained(self, value):
        self._setBool(6, value)

    def getIsDayQuestDone(self):
        return self._getBool(7)

    def setIsDayQuestDone(self, value):
        self._setBool(7, value)

    def getIsWeekQuestDone(self):
        return self._getBool(8)

    def setIsWeekQuestDone(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(DragonBoatEntryPointModel, self)._initialize()
        self._addViewModelProperty('progressDay', QuestModel())
        self._addViewModelProperty('progressWeek', QuestModel())
        self._addNumberProperty('state', 0)
        self._addNumberProperty('team', -1)
        self._addNumberProperty('timeTillNextDayUpdate', -1)
        self._addStringProperty('formattedTimeTillNextUpdate', '')
        self._addBoolProperty('isDayQuestObtained', False)
        self._addBoolProperty('isDayQuestDone', False)
        self._addBoolProperty('isWeekQuestDone', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
