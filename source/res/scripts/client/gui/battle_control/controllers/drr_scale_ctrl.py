# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/drr_scale_ctrl.py
import weakref
import BigWorld
import Keys
from Event import Event
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui import g_repeatKeyHandlers
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import drr_scale

class DRRScaleController(IBattleController):

    def __init__(self, messages):
        super(DRRScaleController, self).__init__()
        self.__messages = weakref.proxy(messages)
        self.onDRRChanged = Event()

    def getControllerID(self):
        return BATTLE_CTRL_ID.DRR_SCALE

    def startControl(self):
        g_repeatKeyHandlers.add(self.__handleRepeatKeyEvent)

    def stopControl(self):
        self.__messages = None
        g_repeatKeyHandlers.discard(self.__handleRepeatKeyEvent)
        return

    def handleKey(self, key, isDown):
        if key in (Keys.KEY_MINUS, Keys.KEY_NUMPADMINUS) and BigWorld.isKeyDown(Keys.KEY_RSHIFT) and isDown and not g_settingsCore.getSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED):
            result = drr_scale.stepDown()
            if result is not None and self.__messages:
                self.__messages.showVehicleMessage('DRR_SCALE_STEP_DOWN', {'scale': drr_scale.getPercent(result)})
                self.onDRRChanged()
            return True
        elif key in (Keys.KEY_EQUALS, Keys.KEY_ADD) and BigWorld.isKeyDown(Keys.KEY_RSHIFT) and isDown and not g_settingsCore.getSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED):
            result = drr_scale.stepUp()
            if result is not None and self.__messages:
                self.__messages.showVehicleMessage('DRR_SCALE_STEP_UP', {'scale': drr_scale.getPercent(result)})
                self.onDRRChanged()
            return True
        else:
            return False

    def __handleRepeatKeyEvent(self, event):
        self.handleKey(event.key, event.isKeyDown())
