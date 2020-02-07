# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_award_types.py
from frameworks.wulf import ViewModel

class RankedAwardTypes(ViewModel):
    __slots__ = ()
    SMALL = 'small'
    MEDIUM = 'medium'
    BIG = 'big'
    LARGE = 'large'

    def __init__(self, properties=0, commands=0):
        super(RankedAwardTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(RankedAwardTypes, self)._initialize()
