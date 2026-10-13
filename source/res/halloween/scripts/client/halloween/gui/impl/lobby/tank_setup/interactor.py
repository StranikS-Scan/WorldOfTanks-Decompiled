# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tank_setup/interactor.py
from __future__ import absolute_import
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from adisp import adisp_process
from halloween.gui.impl.lobby.tank_setup import HWTankSetupConstants
BUY_AND_INSTALL_HW_CONSUMABLES_ACTION = 'buyAndInstallHWConsumables'

class HalloweenInteractor(ConsumableInteractor):

    def getName(self):
        return HWTankSetupConstants.HW_CONSUMABLES

    @adisp_process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(BUY_AND_INSTALL_HW_CONSUMABLES_ACTION, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return
