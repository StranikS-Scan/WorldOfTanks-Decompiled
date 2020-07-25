# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/need_repair_bottom_content_type.py
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType

class NeedRepairBottomContentType(BuyAndExchangeBottomContentType):
    __slots__ = ()
    NOT_NEED_REPAIR = 'notNeedRepair'

    def __init__(self, properties=0, commands=0):
        super(NeedRepairBottomContentType, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NeedRepairBottomContentType, self)._initialize()
