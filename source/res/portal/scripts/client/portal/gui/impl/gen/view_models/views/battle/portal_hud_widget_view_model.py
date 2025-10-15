# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/battle/portal_hud_widget_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from portal.gui.impl.gen.view_models.views.battle.portal_widget_camp import PortalWidgetCamp

class WidgetState(Enum):
    PREBATTLE = 'preBattle'
    DEFAULT = 'default'
    SUPERBOSSFIGHT = 'superBossFight'
    AFTERBATTLE = 'afterBattle'


class PortalHudWidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PortalHudWidgetViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def camps(self):
        return self._getViewModel(0)

    @staticmethod
    def getCampsType():
        return PortalWidgetCamp

    def getCampsCount(self):
        return self._getNumber(1)

    def setCampsCount(self, value):
        self._setNumber(1, value)

    def getCapturedCamps(self):
        return self._getNumber(2)

    def setCapturedCamps(self, value):
        self._setNumber(2, value)

    def getCanBeCapturedCamps(self):
        return self._getNumber(3)

    def setCanBeCapturedCamps(self, value):
        self._setNumber(3, value)

    def getState(self):
        return WidgetState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def getBossMaxHealth(self):
        return self._getNumber(5)

    def setBossMaxHealth(self, value):
        self._setNumber(5, value)

    def getBossCurrentHealth(self):
        return self._getNumber(6)

    def setBossCurrentHealth(self, value):
        self._setNumber(6, value)

    def getBossLastDamage(self):
        return self._getNumber(7)

    def setBossLastDamage(self, value):
        self._setNumber(7, value)

    def getSuperBossMaxHealth(self):
        return self._getNumber(8)

    def setSuperBossMaxHealth(self, value):
        self._setNumber(8, value)

    def getSuperBossCurrentHealth(self):
        return self._getNumber(9)

    def setSuperBossCurrentHealth(self, value):
        self._setNumber(9, value)

    def getSuperBossLastDamage(self):
        return self._getNumber(10)

    def setSuperBossLastDamage(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(PortalHudWidgetViewModel, self)._initialize()
        self._addViewModelProperty('camps', UserListModel())
        self._addNumberProperty('campsCount', 0)
        self._addNumberProperty('capturedCamps', 0)
        self._addNumberProperty('canBeCapturedCamps', 0)
        self._addStringProperty('state')
        self._addNumberProperty('bossMaxHealth', 0)
        self._addNumberProperty('bossCurrentHealth', 0)
        self._addNumberProperty('bossLastDamage', 0)
        self._addNumberProperty('superBossMaxHealth', 0)
        self._addNumberProperty('superBossCurrentHealth', 0)
        self._addNumberProperty('superBossLastDamage', 0)
