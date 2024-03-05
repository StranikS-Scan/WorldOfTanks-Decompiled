# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/notifications/action_handlers.py
import logging
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import LobbyRouteEnum
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(ctrl=ICosmicEventBattleController)
def _switchCosmic(ctrl=None):
    ctrl.switchPrb()
    ctrl.closeRewardScreen()
    ctrl.closePostBattleScreen()


class ProgressionDetailsActionHandler(NavigationDisabledActionHandler):
    _cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def doAction(self, model, entityID, action):
        self._cosmicController.setLobbyRoute(LobbyRouteEnum.ARTEFACT, True)
        _switchCosmic()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class CosmicEventOpenHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        _switchCosmic()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass
