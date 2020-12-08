# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_talisman_consts.py
from frameworks.wulf import ViewModel

class NyTalismanConsts(ViewModel):
    __slots__ = ()
    TALISMAN_DISABLED = 'disabled'
    TALISMAN_SELECT_FIRST = 'selectFirst'
    TALISMAN_SELECT_NEW = 'selectNew'
    TALISMAN_GIFT_WAIT = 'giftWait'
    TALISMAN_GIFT_READY = 'giftReady'
    TALISMAN_FINISHED = 'finished'
    TAB_TOY_TYPE = 1
    TAB_MASCOT_TYPE = 2
    TAB_CELEBRITY_TYPE = 3

    def __init__(self, properties=0, commands=0):
        super(NyTalismanConsts, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NyTalismanConsts, self)._initialize()
