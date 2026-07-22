# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/notification/action_handlers.py
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from skeletons.account_helpers.settings_core import ISettingsCore
from tank_academy.gui.shared.event_dispatcher import showTankAcademy, showTankAcademyVehicleSelection

class OpenTankAcademyHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showTankAcademy()


class OpenTankAcademyVehicleSelectionHandler(NavigationDisabledActionHandler):
    __settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        if not self.__settingsCore.serverSettings.isTankAcademyWelcomeScreenShown():
            showTankAcademy()
        else:
            notification = model.getNotification(self.getNotType(), entityID)
            savedData = notification.getSavedData()
            rewardToken = savedData.get('rewardToken')
            showTankAcademyVehicleSelection(rewardToken, forceCreate=True)
