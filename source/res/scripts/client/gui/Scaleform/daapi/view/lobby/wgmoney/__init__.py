# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wgmoney/__init__.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.WG_MONEY_ALIASES import WG_MONEY_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.wgmoney.wgm_offline_emergency_view import WGMoneyWarningView
    return (ViewSettings(WG_MONEY_ALIASES.WG_MONEY_WARNING_VIEW_ALIAS, WGMoneyWarningView, 'wgMoneyWarningView.swf', ViewTypes.OVERLAY, WG_MONEY_ALIASES.WG_MONEY_WARNING_VIEW_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (WGMoneyPackageBusinessHandler(),)


class WGMoneyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((WG_MONEY_ALIASES.WG_MONEY_WARNING_VIEW_ALIAS, self.loadViewByCtxEvent),)
        super(WGMoneyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
