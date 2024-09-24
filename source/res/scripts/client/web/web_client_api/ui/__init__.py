# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/__init__.py
from web.web_client_api import w2capi, w2c, W2CSchema
from web.web_client_api.seniority_awards import OpenSeniorityAwardsWebApi
from web.web_client_api.ui.battle_royale import OpenBattleRoyaleHangarMixin
from web.web_client_api.ui.calendar import OpenCalendarWindowWebApiMixin
from web.web_client_api.ui.chat import ChatWebApiMixin
from web.web_client_api.ui.maps_training import OpenMapsTrainingMixin
from web.web_client_api.ui.resource_well import ResourceWellWebApiMixin
from web.web_client_api.ui.shop import ShopWebApiMixin
from web.web_client_api.ui.badges import BadgesWebApiMixin
from web.web_client_api.ui.boosters import BoostersWindowWebApiMixin
from web.web_client_api.ui.browser import OpenBrowserWindowWebApiMixin
from web.web_client_api.ui.browser import CloseBrowserWindowWebApiMixin
from web.web_client_api.ui.browser import CloseBrowserViewWebApiMixin
from web.web_client_api.ui.browser import OpenExternalBrowserWebApiMixin
from web.web_client_api.ui.browser import OpenBrowserOverlayWebApiMixin, OpenBuyGoldWebApiMixin
from web.web_client_api.ui.barracks import BarracksWebApiMixin
from web.web_client_api.ui.clan import ClanWindowWebApiMixin
from web.web_client_api.ui.dialogs import DialogsWebApiMixin
from web.web_client_api.ui import hangar
from web.web_client_api.ui.manual import ManualPageWebApiMixin
from web.web_client_api.ui.menu import UserMenuWebApiMixin
from web.web_client_api.ui.missions import MissionsWebApiMixin, PersonalMissionsWebApiMixin
from web.web_client_api.ui.notification import NotificationWebApiMixin
from web.web_client_api.ui.premium import PremiumViewsWebApiMixin
from web.web_client_api.ui.profile import ProfileTabWebApiMixin, ProfileWindowWebApiMixin
from web.web_client_api.ui.squad import SquadWebApiMixin
from web.web_client_api.ui.storage import StorageWebApiMixin
from web.web_client_api.ui.strongholds import StrongholdsWebApiMixin
from web.web_client_api.ui.tankman import OpenTankmanWebApiMixin
from web.web_client_api.ui.techtree import TechTreeTabWebApiMixin
from web.web_client_api.ui.util import UtilWebApiMixin
from web.web_client_api.ui.vehicle import VehicleSellWebApiMixin
from web.web_client_api.ui.vehicle import VehicleCompareWebApiMixin
from web.web_client_api.ui.vehicle import VehiclePreviewWebApiMixin
from web.web_client_api.ui.vehicle import VehicleComparisonBasketWebApiMixin
from web.web_client_api.ui.waiting import WaitingWebApiMixin
from web.web_client_api.ui.ranked import OpenRankedPagesMixin
from web.web_client_api.ui.frontline import OpenFrontLinePagesMixin
from web.web_client_api.ui.referral import ReferralProgramPagesMixin

@w2capi(name='open_window', key='window_id')
class OpenWindowWebApi(OpenBrowserWindowWebApiMixin, ClanWindowWebApiMixin, ProfileWindowWebApiMixin, OpenExternalBrowserWebApiMixin, VehicleSellWebApiMixin, hangar.HangarWindowsWebApiMixin, BoostersWindowWebApiMixin, ManualPageWebApiMixin, ChatWebApiMixin, SquadWebApiMixin, OpenBrowserOverlayWebApiMixin, PremiumViewsWebApiMixin, OpenCalendarWindowWebApiMixin, OpenBuyGoldWebApiMixin, OpenTankmanWebApiMixin, DialogsWebApiMixin, OpenRankedPagesMixin, OpenSeniorityAwardsWebApi):
    pass


@w2capi(name='close_window', key='window_id')
class CloseWindowWebApi(CloseBrowserWindowWebApiMixin):
    pass


@w2capi('close_window', 'window_id')
class CloseViewWebApi(CloseBrowserViewWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class OpenTabWebApi(hangar.HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin, TechTreeTabWebApiMixin, VehicleComparisonBasketWebApiMixin, MissionsWebApiMixin, BarracksWebApiMixin, ShopWebApiMixin, StorageWebApiMixin, StrongholdsWebApiMixin, PersonalMissionsWebApiMixin, BadgesWebApiMixin, OpenFrontLinePagesMixin, ReferralProgramPagesMixin, OpenMapsTrainingMixin, ResourceWellWebApiMixin, OpenBattleRoyaleHangarMixin):

    @classmethod
    def addTabIdCallback(cls, tabId, callback):
        decorator = w2c(W2CSchema, tabId)
        decoratedCallback = decorator(callback)
        setattr(cls, tabId, decoratedCallback)


@w2capi()
class NotificationWebApi(NotificationWebApiMixin):
    pass


@w2capi(name='context_menu', key='menu_type')
class ContextMenuWebApi(UserMenuWebApiMixin):
    pass


@w2capi(name='util', key='action')
class UtilWebApi(UtilWebApiMixin, VehicleCompareWebApiMixin, WaitingWebApiMixin):
    pass
