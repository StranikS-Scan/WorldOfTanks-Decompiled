# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/hangar_tank_model.py
from gui.impl.gen.view_models.views.lobby.halloween.tank_model import TankModel

class HangarTankModel(TankModel):
    __slots__ = ()
    DEFAULT = 'default'
    LOCKED = 'locked'
    IN_BATTLE = 'inBattle'
    NOT_IN_HANGAR = 'notInHangar'
    IN_PLATOON = 'inPlatoon'

    def __init__(self, properties=7, commands=0):
        super(HangarTankModel, self).__init__(properties=properties, commands=commands)

    def getHasDaily(self):
        return self._getBool(4)

    def setHasDaily(self, value):
        self._setBool(4, value)

    def getDailyBonus(self):
        return self._getNumber(5)

    def setDailyBonus(self, value):
        self._setNumber(5, value)

    def getState(self):
        return self._getString(6)

    def setState(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(HangarTankModel, self)._initialize()
        self._addBoolProperty('hasDaily', False)
        self._addNumberProperty('dailyBonus', 0)
        self._addStringProperty('state', '')
