# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/notification/__init__.py
from gui.shared.system_factory import registerNotificationsActionsHandlers
from tank_academy.notification.action_handlers import OpenTankAcademyHandler, OpenTankAcademyVehicleSelectionHandler

def registerClientNotificationHandlers():
    registerNotificationsActionsHandlers((OpenTankAcademyHandler, OpenTankAcademyVehicleSelectionHandler))
