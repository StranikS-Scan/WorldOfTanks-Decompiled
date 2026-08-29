# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_portal_rewardList.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_bonus_model import WtPortalBonusModel

class slotType(Enum):
    DEFAULT = 'default'
    EPIC = 'epic'


class WtPortalRewardlist(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(WtPortalRewardlist, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getProbability(self):
        return self._getString(1)

    def setProbability(self, value):
        self._setString(1, value)

    def getProbabilityIconPath(self):
        return self._getString(2)

    def setProbabilityIconPath(self, value):
        self._setString(2, value)

    def getIndex(self):
        return self._getNumber(3)

    def setIndex(self, value):
        self._setNumber(3, value)

    def getSlotType(self):
        return slotType(self._getString(4))

    def setSlotType(self, value):
        self._setString(4, value.value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return WtPortalBonusModel

    def _initialize(self):
        super(WtPortalRewardlist, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('probability', '')
        self._addStringProperty('probabilityIconPath', '')
        self._addNumberProperty('index', 0)
        self._addStringProperty('slotType')
        self._addArrayProperty('rewards', Array())
