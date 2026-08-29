# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/personal_mission_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class PersonalMissionModel(ViewModel):
    __slots__ = ()
    STATE_ACTIVE = 'active'
    STATE_IMPROVE = 'improve'
    STATE_COMPLETE = 'complete'
    STATE_WRONG_VEHICLE = 'wrongVehicle'
    STATE_WARNING = 'warning'
    ANIMATION_NONE = 'none'
    ANIMATION_TANK_CHANGE = 'tankChange'
    ANIMATION_NEW_MISSION = 'newMission'

    def __init__(self, properties=10, commands=0):
        super(PersonalMissionModel, self).__init__(properties=properties, commands=commands)

    def getCampaignId(self):
        return self._getNumber(0)

    def setCampaignId(self, value):
        self._setNumber(0, value)

    def getMissionId(self):
        return self._getNumber(1)

    def setMissionId(self, value):
        self._setNumber(1, value)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getVehicleIcon(self):
        return self._getResource(4)

    def setVehicleIcon(self, value):
        self._setResource(4, value)

    def getMissionState(self):
        return self._getString(5)

    def setMissionState(self, value):
        self._setString(5, value)

    def getAnimationType(self):
        return self._getString(6)

    def setAnimationType(self, value):
        self._setString(6, value)

    def getWarningMessage(self):
        return self._getString(7)

    def setWarningMessage(self, value):
        self._setString(7, value)

    def getWarningTooltipHeader(self):
        return self._getString(8)

    def setWarningTooltipHeader(self, value):
        self._setString(8, value)

    def getWarningTooltipBody(self):
        return self._getString(9)

    def setWarningTooltipBody(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(PersonalMissionModel, self)._initialize()
        self._addNumberProperty('campaignId', 0)
        self._addNumberProperty('missionId', 0)
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('vehicleIcon', R.invalid())
        self._addStringProperty('missionState', '')
        self._addStringProperty('animationType', 'none')
        self._addStringProperty('warningMessage', '')
        self._addStringProperty('warningTooltipHeader', '')
        self._addStringProperty('warningTooltipBody', '')
