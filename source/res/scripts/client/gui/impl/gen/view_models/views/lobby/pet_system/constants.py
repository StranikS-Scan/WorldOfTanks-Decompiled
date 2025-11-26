# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/constants.py
from enum import Enum
from frameworks.wulf import ViewModel

class PetState(Enum):
    UNDEFINED = 'undefined'
    PROMO = 'Promo'


class Constants(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(Constants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(Constants, self)._initialize()
