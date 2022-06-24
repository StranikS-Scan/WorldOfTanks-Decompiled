# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_ammunition_setup_selector.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_setup_selector import AmmunitionSetupSelector

class PrebattleAmmunitionSetupSelector(AmmunitionSetupSelector):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PrebattleAmmunitionSetupSelector, self).__init__(properties=properties, commands=commands)

    def getHotKeys(self):
        return self._getArray(3)

    def setHotKeys(self, value):
        self._setArray(3, value)

    @staticmethod
    def getHotKeysType():
        return str

    def _initialize(self):
        super(PrebattleAmmunitionSetupSelector, self)._initialize()
        self._addArrayProperty('hotKeys', Array())
