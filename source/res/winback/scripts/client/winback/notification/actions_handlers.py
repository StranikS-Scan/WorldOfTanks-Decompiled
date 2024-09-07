# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/notification/actions_handlers.py
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from winback.gui.shared.event_dispatcher import showProgressionView, showWinbackSelectRewardView

class ShowWinbackProgressionActionHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        showProgressionView()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class OpenWinbackSelectableRewardView(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.WINBACK_SELECTABLE_REWARD_AVAILABLE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showWinbackSelectRewardView()


class OpenWinbackSelectableRewardViewFromQuest(OpenWinbackSelectableRewardView):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE
