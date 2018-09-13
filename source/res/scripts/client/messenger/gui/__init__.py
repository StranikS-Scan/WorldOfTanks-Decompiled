# Embedded file name: scripts/client/messenger/gui/__init__.py
from messenger.m_constants import MESSENGER_SCOPE

def setGUIEntries(decorator):
    from messenger.gui.Scaleform.LobbyEntry import LobbyEntry
    from messenger.gui.Scaleform.BattleEntry import BattleEntry
    decorator.setEntry(MESSENGER_SCOPE.LOBBY, LobbyEntry())
    decorator.setEntry(MESSENGER_SCOPE.BATTLE, BattleEntry())
