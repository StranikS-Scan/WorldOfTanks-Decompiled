# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/commander_card_constants.py
from frameworks.wulf import ViewModel

class CommanderCardConstants(ViewModel):
    __slots__ = ()
    STATE_AVAILABLE = 'available'
    STATE_DISABLE = 'disable'
    STATE_SELECTED = 'selected'
    COMMANDER_TYPE_NEW = 'new'
    COMMANDER_TYPE_DEFAULT = 'default'
    COMMANDER_TYPE_HISTORICAL = 'historical'
    COMMANDER_TYPE_NON_HISTORICAL = 'non_historical'
    PORTRAIT_TYPE_DOCUMENT = 'document'
    PORTRAIT_TYPE_SKIN = 'skin'

    def __init__(self, properties=0, commands=0):
        super(CommanderCardConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CommanderCardConstants, self)._initialize()
