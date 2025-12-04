# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, GroupedViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from new_year.gui.constants import VIEW_ALIAS

def getContextMenuHandlers():
    pass


def getViewSettings():
    from new_year.gui.impl.lobby.new_year.ny_browser_view import NyBrowserView
    from new_year.gui.impl.new_year.views.ny_select_vehicle_for_discount_popover import NYSelectVehicleForDiscountPopover
    from new_year.gui.impl.lobby.new_year.widgets.ny_main_widget import NyMainWidgetInject
    from new_year.gui.impl.lobby.new_year.env_switcher.env_switcher_btn_view import EnvSwitcherBtnInject
    from new_year.gui.impl.lobby.new_year.env_switcher.env_switcher_btn_tip import EnvSwitcherBtnTipInject
    from new_year.gui.Scaleform.daapi.view.lobby.ny_vehicle_preview import NyVehiclePreview
    return (ViewSettings(VIEW_ALIAS.NY_BROWSER_VIEW, NyBrowserView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.NY_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_VEHICLE_PREVIEW, NyVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.NY_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, NYSelectVehicleForDiscountPopover, 'NYSelectVehiclePopover.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, ScopeTemplates.TOP_WINDOW_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_MAIN_WIDGET_UI, NyMainWidgetInject, None),
     ComponentSettings(HANGAR_ALIASES.NY_TANK_CAROUSEL_BTN_CONTAINER, EnvSwitcherBtnInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.NY_TANK_CAROUSEL_BTN_TIP_CONTAINER, EnvSwitcherBtnTipInject, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_NewYearBusinessHandler(),)


class _NewYearBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.NY_BROWSER_VIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.NY_VEHICLE_PREVIEW, self.loadViewByCtxEvent))
        super(_NewYearBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


def replaceHangarSoundSpace():
    from helpers import dependency
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import HangarSoundSpaceSettings
    from gui.sounds.filters import StatesGroup, States
    from new_year.gui.impl.new_year.sounds import NewYearSoundVars, NewYearSoundStates, NewYearSoundEvents
    settings = HangarSoundSpaceSettings(name='hangar', entranceStates={StatesGroup.HANGAR_PLACE: States.HANGAR_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF,
     NewYearSoundVars.STATE_NEWYEAR_PLACE: NewYearSoundStates.HANGAR}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=NewYearSoundEvents.HANGAR, exitEvent=NewYearSoundEvents.HANGAR_EXIT)
    dependency.replaceInstance(HangarSoundSpaceSettings, settings)
