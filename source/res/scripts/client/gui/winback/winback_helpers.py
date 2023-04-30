# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/winback/winback_helpers.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import Winback
from adisp import adisp_process
from gui.impl.gen import R
from gui.impl.lobby.winback.winback_leave_mode_dialog_view import WinbackLeaveModeDialogView
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, events

@adisp_process
def leaveWinbackMode(reason, showConfirmDialog=False, callback=None):
    from gui.shared.gui_items.processors.winback import WinbackTurnOffBattlesProcessor
    confirmDialog = None
    if showConfirmDialog:
        confirmDialog = WinbackLeaveModeDialogView
    result = yield WinbackTurnOffBattlesProcessor(reason, confirmDialog).request()
    if result.success and callback is not None:
        callback()
    return


@adisp_process
def selectRandom():
    from gui.prb_control.dispatcher import g_prbLoader
    prbDispatcher = g_prbLoader.getDispatcher()
    if prbDispatcher is not None:
        yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
    g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(R.views.lobby.mode_selector.ModeSelectorView()))
    return


def getWinbackSetting(settingName):
    return AccountSettings.getSettings(Winback.WINBACK_SETTINGS).get(settingName)


def setWinbackSetting(settingName, settingValue):
    settings = AccountSettings.getSettings(Winback.WINBACK_SETTINGS)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(Winback.WINBACK_SETTINGS, settings)
