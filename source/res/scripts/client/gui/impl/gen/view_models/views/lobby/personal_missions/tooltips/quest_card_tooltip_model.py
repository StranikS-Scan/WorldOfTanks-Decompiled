# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/quest_card_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_model import Pm3QuestModel

class QuestState(Enum):
    NAPREVIOUS = 'previousProgress'
    NAPREVIOUSALL = 'previousProgressAll'
    NATECH = 'noTech'
    AVAILABLE = 'available'
    INPROGRESS = 'inProgress'
    INPROGRESSHONOR = 'inProgressHonor'
    DONE = 'done'
    DONEBASIC = 'doneBasic'
    DONEHONOR = 'doneHonor'


class DescriptionQuestStatus(Enum):
    NOTAVAILABLENOVEHICLE = 'notAvailableNoVehicle'
    NOTAVAILABLESWITCH = 'notAvailableSwitch'
    NOTAVAILABLEPREVQUESTNOTCOMPLETED = 'notAvailablePrevQuestNotCompleted'
    NOTAVAILABLEPREVOPERATIONNOTCOMPLETED = 'notAvailablePrevOperationNotCompleted'
    AVAILABLE = 'available'
    INPROGRESS = 'inProgress'
    DONE = 'done'
    DONEH = 'doneHonor'


class QuestCardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(QuestCardTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def questData(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestDataType():
        return Pm3QuestModel

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIsFinal(self):
        return self._getBool(3)

    def setIsFinal(self, value):
        self._setBool(3, value)

    def getStatus(self):
        return QuestState(self._getString(4))

    def setStatus(self, value):
        self._setString(4, value.value)

    def getDescriptionStatus(self):
        return DescriptionQuestStatus(self._getString(5))

    def setDescriptionStatus(self, value):
        self._setString(5, value.value)

    def getMinVehicleLevel(self):
        return self._getNumber(6)

    def setMinVehicleLevel(self, value):
        self._setNumber(6, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(7)

    def setMaxVehicleLevel(self, value):
        self._setNumber(7, value)

    def getPrevOperationName(self):
        return self._getString(8)

    def setPrevOperationName(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(QuestCardTooltipModel, self)._initialize()
        self._addViewModelProperty('questData', Pm3QuestModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isFinal', False)
        self._addStringProperty('status')
        self._addStringProperty('descriptionStatus')
        self._addNumberProperty('minVehicleLevel', 0)
        self._addNumberProperty('maxVehicleLevel', 0)
        self._addStringProperty('prevOperationName', '')
