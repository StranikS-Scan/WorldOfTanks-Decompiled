# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/commendationStateModel.py
from enum import Enum
from frameworks.wulf import ViewModel

class CommendationStateEnum(Enum):
    UNAVAILABLE = 'unavailable'
    COMMENDFIRST = 'commendFirst'
    COMMENDBACK = 'commendBack'
    OUTGOINGCOMMENDATION = 'outgoingCommendation'
    MUTUALCOMMENDATION = 'mutualCommendation'


class CommendationStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CommendationStateModel, self).__init__(properties=properties, commands=commands)

    def getCommendationState(self):
        return CommendationStateEnum(self._getString(0))

    def setCommendationState(self, value):
        self._setString(0, value.value)

    def getIsNewState(self):
        return self._getBool(1)

    def setIsNewState(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(CommendationStateModel, self)._initialize()
        self._addStringProperty('commendationState', CommendationStateEnum.UNAVAILABLE.value)
        self._addBoolProperty('isNewState', False)
