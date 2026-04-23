# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/dialogs/abilities_incomplete_dialog.py
from __future__ import absolute_import
from PlayerEvents import g_playerEvents
from constants import LoadoutParams
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from last_stand.gui.impl.gen.view_models.views.lobby.dialogs.abilities_inclomplete_dialog_model import AbilitiesInclompleteDialogModel
from last_stand.gui.impl.lobby.states import LastStandConsumableLoadoutState
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from last_stand.gui.impl.lobby.widgets.ls_loadout import getCurrentPreset

def getConsumablesLoadoutParams():
    preset = getCurrentPreset()
    sectionName, groupIndex = LSTankSetupConstants.LS_CONSUMABLES, 0
    for groupIDx, group in enumerate(preset):
        if LSTankSetupConstants.LS_CONSUMABLES in group:
            groupIndex = groupIDx
            break

    return {LoadoutParams.sectionName: sectionName,
     LoadoutParams.groupId: groupIndex,
     LoadoutParams.slotIndex: 0}


class AbilitiesIncompleteDialog(FullScreenDialogBaseView):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.last_stand.mono.lobby.dialogs.abilities_incomplete_confirm(), model=AbilitiesInclompleteDialogModel())
        super(AbilitiesIncompleteDialog, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onSubmitClick, self._onSubmitClick),
         (self.viewModel.onCloseClick, self._onCloseClick),
         (self.viewModel.onCancelClick, self._onCancelClick),
         (g_playerEvents.onAccountBecomeNonPlayer, self.destroyWindow))

    def _onSubmitClick(self):
        self._setResult(DialogButtons.CANCEL)
        LastStandConsumableLoadoutState.goTo(**getConsumablesLoadoutParams())

    def _onCancelClick(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCloseClick(self):
        self._setResult(DialogButtons.CANCEL)
