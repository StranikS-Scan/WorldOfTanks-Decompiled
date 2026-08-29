# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/shared/events.py
from gui.shared.events import HasCtxEvent

class DynamicFactorsEvent(HasCtxEvent):
    UPDATE_LEVEL = 'dynamicFactors/updateLevel'


class WTCrosshairVisibilityEvents(HasCtxEvent):
    SHOW_CROSSHAIR = 'WTCrosshairVisibility/showCrossHair'
