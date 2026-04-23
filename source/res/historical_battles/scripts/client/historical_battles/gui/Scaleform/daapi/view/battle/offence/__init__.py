# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/offence/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, getSwfExtensionUrl
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.Scaleform.daapi.view import battle
from historical_battles.gui.Scaleform.daapi.view.battle.offence.page import HistoricalBattlesOffencePage

def getContextMenuHandlers():
    return battle.getHBContextMenuHandlers()


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.HISTORICAL_BATTLES, HistoricalBattlesOffencePage, getSwfExtensionUrl('historical_battles', 'HBOffenceBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),) + battle.getHBViewSettings()


def getBusinessHandlers():
    return battle.getHBBusinessHandlers()
