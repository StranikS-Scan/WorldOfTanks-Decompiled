# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/comp7.py
from constants import QUEUE_TYPE
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.utils import SelectorBattleTypesUtils
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.event_dispatcher import showHangar
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from web.web_client_api import W2CSchema, w2c, Field

class _OpenComp7HangarSchema(W2CSchema):
    vehicle_id = Field(required=False, type=int)


class Comp7HangarWebApiMixin(object):

    @w2c(_OpenComp7HangarSchema, 'comp7_hangar')
    def openComp7Hangar(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()
        isPrbActive = False
        if dispatcher is not None:
            isPrbActive = dispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.COMP7)
        if cmd.vehicle_id:
            comp7_prb_helpers.selectVehicleInComp7Hangar(cmd.vehicle_id, False)
        if isPrbActive:
            showHangar()
        else:
            comp7_prb_helpers.selectComp7()
        SelectorBattleTypesUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.COMP7)
        return
