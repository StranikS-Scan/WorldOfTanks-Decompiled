# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleAfkController.py
import BigWorld
from messenger import MessengerEntry, g_settings
from gui.impl import backport
from gui.impl.gen import R

class WTVehicleAfkController(BigWorld.DynamicScriptComponent):

    def set_warningCount(self, prev):
        if prev == self.warningCount:
            return
        if self.entity.id != BigWorld.player().inputHandler.ctrl.curVehicleID:
            return
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': backport.text(R.strings.white_tiger.notification.afkWarning())}))
