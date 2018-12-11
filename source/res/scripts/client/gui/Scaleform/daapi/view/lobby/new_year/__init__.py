# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/__init__.py
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.NEWYEAR_ALIASES import NEWYEAR_ALIASES
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.new_year.new_year_vehicle_selector_popup import NewYearVehicleSelectorPopup
    return (GroupedViewSettings(NEWYEAR_ALIASES.NEW_YEAR_VEHICLE_SELECTOR_ALIAS, NewYearVehicleSelectorPopup, 'vehicleSelector.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True, isModal=True),)


def getBusinessHandlers():
    return (NewYearPackageBusinessHandler(),)


class NewYearPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((NEWYEAR_ALIASES.NEW_YEAR_VEHICLE_SELECTOR_ALIAS, self.loadViewByCtxEvent),)
        super(NewYearPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
