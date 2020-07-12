# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/commander_cmp_tooltips.py
from frameworks.wulf import ViewModel

class CommanderCmpTooltips(ViewModel):
    __slots__ = ()
    TOOLTIP_SIXTH_SENSE_SKILL = 'commander_sixthSense'
    TOOLTIP_EXPERT_SKILL = 'commander_expert'
    TOOLTIP_TANKMAN = 'battleRoyaleTankman'

    def __init__(self, properties=0, commands=0):
        super(CommanderCmpTooltips, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CommanderCmpTooltips, self)._initialize()
