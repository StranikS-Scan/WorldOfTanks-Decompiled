# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/defence/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, getSwfExtensionUrl, ComponentSettings
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.Scaleform.daapi.view import battle
from historical_battles.gui.Scaleform.daapi.view.battle.defence.page import HistoricalBattlesDefencePage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    return battle.getHBContextMenuHandlers()


def getViewSettings():
    from historical_battles.gui.Scaleform.daapi.view.battle.spg_panel import HistoricalBattlesSPGPanel
    return (ViewSettings(VIEW_ALIAS.HISTORICAL_BATTLES, HistoricalBattlesDefencePage, getSwfExtensionUrl('historical_battles', 'HBDefenceBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_SPG_PANEL, HistoricalBattlesSPGPanel, ScopeTemplates.DEFAULT_SCOPE)) + battle.getHBViewSettings()


def getBusinessHandlers():
    return battle.getHBBusinessHandlers()
