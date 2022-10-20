# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/base_info_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BaseStateEnum(Enum):
    ENEMYCAPTURED = 'EnemyCaptured'
    PLAYERCAPTURED = 'PlayerCaptured'
    NEUTRAL = 'Neutral'


class BaseInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BaseInfoModel, self).__init__(properties=properties, commands=commands)

    def getBaseLetter(self):
        return self._getString(0)

    def setBaseLetter(self, value):
        self._setString(0, value)

    def getBaseState(self):
        return BaseStateEnum(self._getString(1))

    def setBaseState(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(BaseInfoModel, self)._initialize()
        self._addStringProperty('baseLetter', '')
        self._addStringProperty('baseState')
