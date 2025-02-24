# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/tooltip_constants.py
from frameworks.wulf import ViewModel

class TooltipConstants(ViewModel):
    __slots__ = ()
    TANKMAN = 'tankman'
    HANGAR_MODULE = 'hangarModule'
    TECH_MAIN_SHELL = 'techMainShell'
    PRICE_DISCOUNT = 'priceDiscount'

    def __init__(self, properties=0, commands=0):
        super(TooltipConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TooltipConstants, self)._initialize()
