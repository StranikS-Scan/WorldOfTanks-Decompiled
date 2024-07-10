# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/notification/actions_handlers.py
from comp7_light_progression.gui.shared.event_dispatcher import showProgressionView
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE

class ShowComp7LightProgressionActionHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        showProgressionView()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass
