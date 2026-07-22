# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/shared/gui_items/processors/offers.py
from helpers import dependency
from gui.shared.gui_items.processors import makeSuccess
from gui.shared.gui_items.processors.offers import ReceiveOfferGiftProcessor
from gui.Scaleform.Waiting import Waiting
from skeletons.gui.system_messages import ISystemMessages
from tank_academy.gui.gui_constants import SCH_CLIENT_MSG_TYPE

class TankAcademyOfferProcessor(ReceiveOfferGiftProcessor):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loadContent')
        self.__systemMessages.proto.serviceChannel.pushClientMessage(ctx, SCH_CLIENT_MSG_TYPE.TANK_ACADEMY_TOKEN_AWARD)
        return makeSuccess(auxData=ctx)
