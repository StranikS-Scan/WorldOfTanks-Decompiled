# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/notification/action_handlers.py
import logging
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController
from notification.actions_handlers import NavigationDisabledActionHandler
from portal.gui.portal_gui_constants import PREBATTLE_ACTION_NAME
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from notification.actions_handlers import ActionHandler
from notification.settings import NOTIFICATION_TYPE
from portal.gui.shared.event_dispatcher import showPortalProgressionView

class _PortalEventHandler(NavigationDisabledActionHandler):
    _portalController = dependency.descriptor(IPortalEventController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    def _canNavigate(self):
        result = super(_PortalEventHandler, self)._canNavigate()
        return self._portalController.isEnabled() and result


class PortalActionHandler(ActionHandler):

    def handleAction(self, model, entityID, action):
        logging.debug('PortalActionHandler.doAction')
        items = battle_selector_items.getItems()
        items.select(PREBATTLE_ACTION_NAME.RANDOM)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class OpenPortalProgressionHandler(_PortalEventHandler):

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self._portalController.doSelectEventPrbAndCallback(showPortalProgressionView)
