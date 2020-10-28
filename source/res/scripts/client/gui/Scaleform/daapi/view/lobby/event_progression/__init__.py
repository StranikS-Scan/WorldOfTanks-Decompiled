# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENTPROGRESSION_ALIASES import EVENTPROGRESSION_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.event_progression.event_progression_buy_confirm_view import EventProgressionBuyConfirmView
    return (ViewSettings(EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_ALIAS, EventProgressionBuyConfirmView, EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_UI, WindowLayer.TOP_WINDOW, EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (EventProgressionPackageBusinessHandler(),)


class EventProgressionPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((EVENTPROGRESSION_ALIASES.EVENT_PROGRESION_BUY_CONFIRM_VIEW_ALIAS, self.loadViewByCtxEvent),)
        super(EventProgressionPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
