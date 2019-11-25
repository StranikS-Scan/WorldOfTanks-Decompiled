# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_compensation_tooltip_types.py
from frameworks.wulf import ViewModel

class LootBoxCompensationTooltipTypes(ViewModel):
    __slots__ = ()
    BASE = 'base'
    VEHICLE = 'vehicle'
    CREW_SKINS = 'crewSkin'

    def __init__(self, properties=0, commands=0):
        super(LootBoxCompensationTooltipTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootBoxCompensationTooltipTypes, self)._initialize()
