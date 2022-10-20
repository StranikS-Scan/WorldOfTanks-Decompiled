# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_entry_point import HW22EntryPoint
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_progression_entry_point import HW22ProgressionEntryPoint
from halloween.gui.Scaleform.daapi.view.lobby.hangar.event_shop_entry_point import EventShopEntryPoint
from halloween.gui.Scaleform.daapi.view.lobby.hangar.event_global_prgression_entry_point import EventGlobalProgressionEntryPoint
from halloween.gui.Scaleform.daapi.view.lobby.hangar.event_daily_reward import EventDailyReward
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_vehicle_params import HWVehicleParameters
from halloween.gui.Scaleform.daapi.view.lobby.hangar.carousel.tank_carousel import HW22TankCarousel
from halloween.gui.Scaleform.daapi.view.common.filter_popover import HW22CarouselFilterPopover
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, GroupedViewSettings

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ComponentSettings(HANGAR_ALIASES.HW22_EVENT_ENTRY_POINT, HW22EntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_SHOP_ENTRY_POINT, EventShopEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.VEHICLE_PARAMETERS, HWVehicleParameters, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.HW22_TANK_CAROUSEL, HW22TankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER, HW22CarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.WINDOW, VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER, VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_PROGRESSION_ENTRY_POINT, HW22ProgressionEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_DAILY_REWARD, EventDailyReward, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_GLOBAL_PROGRESSION_ENTRY_POINT, EventGlobalProgressionEntryPoint, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (HW22HangarPackageBusinessHandler(),)


class HW22HangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.HW22_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent),)
        super(HW22HangarPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
