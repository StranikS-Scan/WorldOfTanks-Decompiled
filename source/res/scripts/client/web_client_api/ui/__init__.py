# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/__init__.py
from web_client_api import w2capi
from web_client_api.ui.calendar import OpenCalendarWindowWebApiMixin
from web_client_api.ui.chat import ChatWebApiMixin
from web_client_api.ui.shop import ShopWebApiMixin
from web_client_api.ui.badges import BadgesWebApiMixin
from web_client_api.ui.boosters import BoostersWindowWebApiMixin, BoostersInfoWebApiMixin
from web_client_api.ui.browser import OpenBrowserWindowWebApiMixin, CloseBrowserWindowWebApiMixin, CloseBrowserViewWebApiMixin, OpenExternalBrowserWebApiMixin, OpenBrowserOverlayWebApiMixin, OpenBuyGoldWebApiMixin
from web_client_api.ui.barracks import BarracksWebApiMixin
from web_client_api.ui.clan import ClanWindowWebApiMixin
from web_client_api.ui import hangar
from web_client_api.ui.manual import ManualPageWebApiMixin
from web_client_api.ui.menu import UserMenuWebApiMixin
from web_client_api.ui.missions import MissionsWebApiMixin, PersonalMissionsWebApiMixin
from web_client_api.ui.notification import NotificationWebApiMixin
from web_client_api.ui.premium import PremiumWindowWebApiMixin, PremiumViewsWebApiMixin
from web_client_api.ui.profile import ProfileTabWebApiMixin, ProfileWindowWebApiMixin
from web_client_api.ui.squad import SquadWebApiMixin
from web_client_api.ui.strongholds import StrongholdsWebApiMixin
from web_client_api.ui.tankman import OpenTankmanWebApiMixin
from web_client_api.ui.techtree import TechTreeTabWebApiMixin
from web_client_api.ui.util import UtilWebApiMixin
from web_client_api.ui.vehicle import VehicleSellWebApiMixin, VehicleCompareWebApiMixin, VehiclePreviewWebApiMixin, VehicleComparisonBasketWebApiMixin
from web_client_api.ui.waiting import WaitingWebApiMixin

@w2capi(name='open_window', key='window_id')
class OpenWindowWebApi(OpenBrowserWindowWebApiMixin, ClanWindowWebApiMixin, ProfileWindowWebApiMixin, OpenExternalBrowserWebApiMixin, VehicleSellWebApiMixin, hangar.HangarWindowsWebApiMixin, BoostersWindowWebApiMixin, PremiumWindowWebApiMixin, ManualPageWebApiMixin, ChatWebApiMixin, SquadWebApiMixin, OpenBrowserOverlayWebApiMixin, PremiumViewsWebApiMixin, OpenBuyGoldWebApiMixin, OpenTankmanWebApiMixin, OpenCalendarWindowWebApiMixin):
    pass


@w2capi(name='close_window', key='window_id')
class CloseWindowWebApi(CloseBrowserWindowWebApiMixin):
    pass


@w2capi('close_window', 'window_id')
class CloseViewWebApi(CloseBrowserViewWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class OpenTabWebApi(hangar.HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin, TechTreeTabWebApiMixin, VehicleComparisonBasketWebApiMixin, MissionsWebApiMixin, BarracksWebApiMixin, ShopWebApiMixin, StrongholdsWebApiMixin, PersonalMissionsWebApiMixin, BadgesWebApiMixin):
    pass


@w2capi()
class NotificationWebApi(NotificationWebApiMixin):
    pass


@w2capi(name='context_menu', key='menu_type')
class ContextMenuWebApi(UserMenuWebApiMixin):
    pass


@w2capi(name='util', key='action')
class UtilWebApi(UtilWebApiMixin, VehicleCompareWebApiMixin, WaitingWebApiMixin, BoostersInfoWebApiMixin):
    pass
