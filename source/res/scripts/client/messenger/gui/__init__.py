# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/__init__.py
from messenger.m_constants import MESSENGER_SCOPE

def setGUIEntries(decorator):
    from gui import GUI_SETTINGS
    from messenger.gui.Scaleform.battle_entry import BattleEntry
    from messenger.gui.Scaleform.lobby_entry import LobbyEntry
    from messenger.gui.Scaleform.legacy_entry import LegacyBattleEntry
    decorator.setEntry(MESSENGER_SCOPE.LOBBY, LobbyEntry())
    if GUI_SETTINGS.useAS3Battle:
        decorator.setEntry(MESSENGER_SCOPE.BATTLE, BattleEntry())
    else:
        decorator.setEntry(MESSENGER_SCOPE.BATTLE, LegacyBattleEntry())
