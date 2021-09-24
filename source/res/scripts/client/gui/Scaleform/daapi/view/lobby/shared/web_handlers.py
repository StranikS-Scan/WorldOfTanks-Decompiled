# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from web.web_client_api import webApiCollection
from web.web_client_api.frontline import FrontLineWebApi
from web.web_client_api.mapbox import MapboxWebApi
from web.web_client_api.marathon import MarathonWebApi
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi, HangarSoundWebApi, SoundStateWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, OpenTabWebApi, NotificationWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from web.web_client_api.blueprints_convert_sale import BlueprintsConvertSaleWebApi
from web.web_client_api.birthday_calendar import BirthdayCalendarWebApi
from web.web_client_api.wt import WtWebApi
_DEFAULT_WEB_API_COLLECTION = (CloseWindowWebApi,
 OpenWindowWebApi,
 NotificationWebApi,
 OpenTabWebApi,
 RequestWebApi,
 ShopWebApi,
 SoundWebApi,
 SoundStateWebApi,
 HangarSoundWebApi,
 UtilWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 RewardsWebApi,
 SocialWebApi,
 BlueprintsConvertSaleWebApi,
 PlatformWebApi,
 MapboxWebApi,
 FrontLineWebApi,
 BirthdayCalendarWebApi,
 MarathonWebApi,
 WtWebApi)

def createBrowserOverlayWebHandlers():
    return webApiCollection(*_DEFAULT_WEB_API_COLLECTION)


def createPremAccWebHandlers():
    return webApiCollection(*_DEFAULT_WEB_API_COLLECTION)
