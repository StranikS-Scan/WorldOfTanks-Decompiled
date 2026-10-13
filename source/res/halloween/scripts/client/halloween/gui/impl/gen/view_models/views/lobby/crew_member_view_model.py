# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/crew_member_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CrewStates(Enum):
    RECEIVED = 'received'
    INSHOP = 'inShop'
    INBASEREWARD = 'inBaseReward'


class CrewMemberViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(CrewMemberViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getVoiceover(self):
        return self._getString(3)

    def setVoiceover(self, value):
        self._setString(3, value)

    def getHasIsShop(self):
        return self._getBool(4)

    def setHasIsShop(self, value):
        self._setBool(4, value)

    def getHasVoiceover(self):
        return self._getBool(5)

    def setHasVoiceover(self, value):
        self._setBool(5, value)

    def getTooltipId(self):
        return self._getString(6)

    def setTooltipId(self, value):
        self._setString(6, value)

    def getState(self):
        return CrewStates(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(CrewMemberViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('voiceover', '')
        self._addBoolProperty('hasIsShop', False)
        self._addBoolProperty('hasVoiceover', False)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('state')
