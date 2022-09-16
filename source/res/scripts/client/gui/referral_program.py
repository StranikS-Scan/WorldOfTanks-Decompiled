# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/referral_program.py
from adisp import adisp_process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.referral_program import referral_program_helpers as helpers
from gui.game_control.links import URLMacros
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showReferralProgramWindow
from gui.shared.gui_items.items_actions.actions import showInventoryMsg
from shared_utils import CONST_CONTAINER

class REFERRAL_PROGRAM_SOUNDS(CONST_CONTAINER):
    RECRUITER_AWARD = 'gui_hangar_simple_execution_screen'


@adisp_process
def showGetVehiclePage(vehicle, params=None):
    if vehicle.isInInventory and not vehicle.isRented:
        showInventoryMsg('already_exists', vehicle, msgType=SystemMessages.SM_TYPE.Warning)
        event_dispatcher.selectVehicleInHangar(vehicle.intCD)
        return
    url = helpers.getObtainVehicleURL()
    if url:
        url = yield URLMacros().parse(url, params=params)
        showReferralProgramWindow(url)
