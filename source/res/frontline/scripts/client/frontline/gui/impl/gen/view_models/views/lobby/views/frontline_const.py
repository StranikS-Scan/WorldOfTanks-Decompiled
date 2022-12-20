# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/frontline_const.py
from enum import Enum
from frameworks.wulf import ViewModel

class FrontlineState(Enum):
    ANNOUNCE = 'announce'
    ACTIVE = 'active'
    FINISHED = 'finished'
    FROZEN = 'frozen'


class FrontlineConst(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(FrontlineConst, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FrontlineConst, self)._initialize()
