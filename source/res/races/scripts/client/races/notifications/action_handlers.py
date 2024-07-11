# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/notifications/action_handlers.py
from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.game_control import IRacesBattleController

@dependency.replace_none_kwargs(ctrl=IRacesBattleController)
def _switchRaces(ctrl=None):
    ctrl.selectRaces()
    ctrl.closeRewardScreen()
    ctrl.closePostBattleScreen()


class RacesOpenHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        _switchRaces()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class RacesLootBoxesAccrualHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        showStorageView()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass
