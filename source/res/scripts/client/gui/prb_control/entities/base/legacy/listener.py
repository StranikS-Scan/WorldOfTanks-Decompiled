# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/listener.py
from gui.prb_control.entities.base.listener import IPrbListener

class ILegacyIntroListener(IPrbListener):
    """
    Listener interface for intro events.
    """

    def onLegacyListReceived(self, result):
        """
        Event for legacies list receiving.
        Args:
            result: list of prebattle's data
        """
        pass

    def onLegacyRosterReceived(self, prebattleID, iterator):
        """
        Event for receiving prebattle roster for proper prebattle.
        Args:
            prebattleID: prebattle ID
            iterator: rosters list
        """
        pass


class ILegacyListener(ILegacyIntroListener):
    """
    Listener interface for entity events.
    """

    def onSettingUpdated(self, entity, settingName, settingValue):
        """
        Establishes a listener to respond when legacy entity receives changes in settings.
        Args:
            entity: legacy entity
            settingName: setting name, one from PREBATTLE_SETTING_NAME
            settingValue: setting new value
        """
        pass

    def onTeamStatesReceived(self, entity, team1State, team2State):
        """
        Establishes a listener to respond when BasePrbEntity receives states of teams.
        Args:
            entity: legacy entity
            team1State: team state data object
            team2State: team state data object
        """
        pass

    def onPlayerAdded(self, entity, playerInfo):
        """
        Establishes a listener to respond when player added to prebattle.
        Args:
            entity: legacy entity
            playerInfo: added player's info
        """
        pass

    def onPlayerRemoved(self, entity, playerInfo):
        """
        Establishes a listener to respond when player removed from prebattle.
        Args:
            entity: legacy entity
            playerInfo: removed player's info
        """
        pass

    def onRostersChanged(self, entity, rosters, full):
        """
        Establishes a listener to respond when BasePrbEntity receives changes in rosters.
        Args:
            entity: legacy entity
            rosters: new roster data
            full: was it fully updated
        """
        pass

    def onPlayerTeamNumberChanged(self, entity, team):
        """
        Establishes a listener to respond when receives new number of team for current player.
        Args:
            entity: legacy entity
            team: team number
        """
        pass

    def onPlayerRosterChanged(self, entity, actorInfo, playerInfo):
        """
        Establishes listener to respond when receives new roster for player.
        Args:
            entity: legacy entity
            actorInfo: player info who changed roster
            playerInfo: player info whose roster was changed
        """
        pass

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        """
        Establishes a listener to respond when BasePrbEntity receives new player's state.
        Args:
            entity: egacy entity
            roster: number containing player's roster
            accountInfo: player's info
        """
        pass
