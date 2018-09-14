# Embedded file name: scripts/client/gui/battle_control/DRRScaleController.py
import weakref
import BigWorld
import Keys
from gui import g_repeatKeyHandlers
from helpers import drr_scale
from Event import Event
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS

class DRRScaleController(object):

    def __init__(self):
        super(DRRScaleController, self).__init__()
        self.__ui = None
        self.onDRRChanged = Event()
        return

    def start(self, ui):
        self.__ui = weakref.proxy(ui)
        g_repeatKeyHandlers.add(self.__handleRepeatKeyEvent)

    def stop(self):
        self.__ui = None
        g_repeatKeyHandlers.remove(self.__handleRepeatKeyEvent)
        return

    def handleKey(self, key, isDown):
        if key in [Keys.KEY_MINUS, Keys.KEY_NUMPADMINUS] and BigWorld.isKeyDown(Keys.KEY_RSHIFT) and isDown and not g_settingsCore.getSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED):
            result = drr_scale.stepDown()
            if result is not None and self.__ui:
                self.__ui.vMsgsPanel.showMessage('DRR_SCALE_STEP_DOWN', {'scale': drr_scale.getPercent(result)})
                self.onDRRChanged()
            return True
        elif key in [Keys.KEY_EQUALS, Keys.KEY_ADD] and BigWorld.isKeyDown(Keys.KEY_RSHIFT) and isDown and not g_settingsCore.getSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED):
            result = drr_scale.stepUp()
            if result is not None and self.__ui:
                self.__ui.vMsgsPanel.showMessage('DRR_SCALE_STEP_UP', {'scale': drr_scale.getPercent(result)})
                self.onDRRChanged()
            return True
        else:
            return False

    def __handleRepeatKeyEvent(self, event):
        self.handleKey(event.key, event.isKeyDown())
