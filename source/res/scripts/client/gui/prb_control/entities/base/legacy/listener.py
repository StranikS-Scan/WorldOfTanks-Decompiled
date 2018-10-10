# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/listener.py
from gui.prb_control.entities.base.listener import IPrbListener

class ILegacyIntroListener(IPrbListener):

    def onLegacyListReceived(self, result):
        pass

    def onLegacyRosterReceived(self, prebattleID, iterator):
        pass


class ILegacyListener(ILegacyIntroListener):

    def onSettingUpdated(self, entity, settingName, settingValue):
        pass

    def onTeamStatesReceived(self, entity, team1State, team2State):
        pass

    def onPlayerAdded(self, entity, playerInfo):
        pass

    def onPlayerRemoved(self, entity, playerInfo):
        pass

    def onRostersChanged(self, entity, rosters, full):
        pass

    def onPlayerTeamNumberChanged(self, entity, team):
        pass

    def onPlayerRosterChanged(self, entity, actorInfo, playerInfo):
        pass

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        pass
