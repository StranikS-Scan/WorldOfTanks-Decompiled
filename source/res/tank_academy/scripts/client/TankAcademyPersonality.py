# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/TankAcademyPersonality.py
import logging
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from tank_academy.gui.server_events import registerTankAcademyQuests
from tank_academy.gui.game_control import registerTAGameControllers, registerTAAwardControllers
from tank_academy.messenger.formatters import registerMessengerClientFormatters, registerTankAcademyTokenQuestsSubFormatters
from tank_academy.notification import registerClientNotificationHandlers
_logger = logging.getLogger(__name__)

def preInit():
    registerTAGameControllers()
    registerTAAwardControllers()
    registerTankAcademyQuests()
    registerMessengerClientFormatters()
    registerTankAcademyTokenQuestsSubFormatters()
    registerClientNotificationHandlers()


def init():
    _logger.debug('init')
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['tank_academy.gui.Scaleform.daapi.view.lobby'])


def start():
    pass


def fini():
    pass
