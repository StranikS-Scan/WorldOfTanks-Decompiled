# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year_personality.py
from debug_utils import LOG_DEBUG
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from NewYearBonusesClient import NewYearBonusesClient
from new_year_common.items import new_year, collectibles
from new_year.gui.game_control import registerNewYearGameControllers
from new_year.notification import registerNewYearNotifications
from new_year.messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.gui.constants import VIEW_ALIAS
from new_year.messenger.formatters.collections_by_type import registerNewYearMessengerFormatters
from new_year.gui.game_control.award_controller import registerNewYearAwardControllerHandlers
from new_year.gui.Scaleform import registerNewYearScaleform
from new_year.gui import replaceNewYearNavigation, addNewYearVignetteSettings
from new_year.gui.Scaleform.daapi.view.lobby import replaceHangarSoundSpace
from new_year.ny_constants import ACCOUNT_DEFAULT_SETTINGS

def preInit():
    LOG_DEBUG('preInit', __name__)
    newYearBonuses = NewYearBonusesClient(__name__)
    newYearBonuses.registerBonusClient()
    collectibles.init()
    new_year.init()
    registerNewYearGameControllers()
    registerNewYearNotifications()
    SCH_CLIENT_MSG_TYPE.inject(__name__)
    VIEW_ALIAS.inject(__name__)
    registerNewYearMessengerFormatters()
    registerNewYearAwardControllerHandlers()
    registerNewYearScaleform()
    addNewYearVignetteSettings(__name__)


def init():
    LOG_DEBUG('init', __name__)
    replaceNewYearNavigation()
    replaceHangarSoundSpace()
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def start():
    pass


def fini():
    pass
