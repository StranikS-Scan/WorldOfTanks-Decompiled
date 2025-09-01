# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/personal_missions_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    CAMPAIGN_NOT_ACTIVATED = 'campaignNotActivated'
    IN_PROGRESS = 'inProgress'
    IN_PROGRESS_FOR_HONORS = 'inProgressForHonors'
    COMPLETED = 'completed'
    COMPLETED_WITH_HONORS = 'completedWithHonors'


class PersonalMissionsModel(ViewModel):
    __slots__ = ('goToCampaigns', 'goToOperation')

    def __init__(self, properties=13, commands=2):
        super(PersonalMissionsModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getAllOperationsCompleted(self):
        return self._getBool(1)

    def setAllOperationsCompleted(self, value):
        self._setBool(1, value)

    def getCampaignName(self):
        return self._getString(2)

    def setCampaignName(self, value):
        self._setString(2, value)

    def getCurrentOperationName(self):
        return self._getString(3)

    def setCurrentOperationName(self, value):
        self._setString(3, value)

    def getCurrentOperationId(self):
        return self._getNumber(4)

    def setCurrentOperationId(self, value):
        self._setNumber(4, value)

    def getNextOperationName(self):
        return self._getString(5)

    def setNextOperationName(self, value):
        self._setString(5, value)

    def getNextOperationId(self):
        return self._getNumber(6)

    def setNextOperationId(self, value):
        self._setNumber(6, value)

    def getStageNumber(self):
        return self._getNumber(7)

    def setStageNumber(self, value):
        self._setNumber(7, value)

    def getDetailId(self):
        return self._getString(8)

    def setDetailId(self, value):
        self._setString(8, value)

    def getVehicleName(self):
        return self._getString(9)

    def setVehicleName(self, value):
        self._setString(9, value)

    def getPreviousProgress(self):
        return self._getNumber(10)

    def setPreviousProgress(self, value):
        self._setNumber(10, value)

    def getCurrentProgress(self):
        return self._getNumber(11)

    def setCurrentProgress(self, value):
        self._setNumber(11, value)

    def getTotalProgress(self):
        return self._getNumber(12)

    def setTotalProgress(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(PersonalMissionsModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('allOperationsCompleted', False)
        self._addStringProperty('campaignName', '')
        self._addStringProperty('currentOperationName', '')
        self._addNumberProperty('currentOperationId', 0)
        self._addStringProperty('nextOperationName', '')
        self._addNumberProperty('nextOperationId', 0)
        self._addNumberProperty('stageNumber', 0)
        self._addStringProperty('detailId', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('previousProgress', 0)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self.goToCampaigns = self._addCommand('goToCampaigns')
        self.goToOperation = self._addCommand('goToOperation')
