# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from event_platform.gui.impl.event_battle_page import EventBattlePage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
__all__ = ('EventBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.CLASSIC_BATTLE_PAGE, EventBattlePage, 'battlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
