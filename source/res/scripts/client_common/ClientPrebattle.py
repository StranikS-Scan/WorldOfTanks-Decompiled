# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientPrebattle.py
import cPickle
import Event
from constants import PREBATTLE_UPDATE, PREBATTLE_TEAM_STATE
from debug_utils import LOG_DEBUG_DEV

class ClientPrebattle(object):
    __onUpdate = {PREBATTLE_UPDATE.ROSTER: '_ClientPrebattle__onRosterReceived',
     PREBATTLE_UPDATE.PLAYER_ADDED: '_ClientPrebattle__onPlayerAdded',
     PREBATTLE_UPDATE.PLAYER_REMOVED: '_ClientPrebattle__onPlayerRemoved',
     PREBATTLE_UPDATE.PLAYER_STATE: '_ClientPrebattle__onPlayerStateChanged',
     PREBATTLE_UPDATE.PLAYER_ROSTER: '_ClientPrebattle__onPlayerRosterChanged',
     PREBATTLE_UPDATE.PLAYER_GROUP: '_ClientPrebattle__onPlayerGroupChanged',
     PREBATTLE_UPDATE.TEAM_STATES: '_ClientPrebattle__onTeamStatesReceived',
     PREBATTLE_UPDATE.SETTINGS: '_ClientPrebattle__onSettingsReceived',
     PREBATTLE_UPDATE.SETTING: '_ClientPrebattle__onSettingUpdated',
     PREBATTLE_UPDATE.KICKED_FROM_QUEUE: '_ClientPrebattle__onKickedFromQueue',
     PREBATTLE_UPDATE.PROPERTIES: '_ClientPrebattle__onPropertiesReceived',
     PREBATTLE_UPDATE.PROPERTY: '_ClientPrebattle__onPropertyUpdated'}

    def __init__(self, prebattleID):
        self.id = prebattleID
        self.settings = None
        self.properties = None
        self.rosters = {}
        self.teamStates = [None, PREBATTLE_TEAM_STATE.NOT_READY, PREBATTLE_TEAM_STATE.NOT_READY]
        self.__eventManager = Event.EventManager()
        em = self.__eventManager
        self.onRosterReceived = Event.Event(em)
        self.onPlayerAdded = Event.Event(em)
        self.onPlayerRemoved = Event.Event(em)
        self.onPlayerStateChanged = Event.Event(em)
        self.onPlayerGroupChanged = Event.Event(em)
        self.onPlayerRosterChanged = Event.Event(em)
        self.onTeamStatesReceived = Event.Event(em)
        self.onSettingsReceived = Event.Event(em)
        self.onSettingUpdated = Event.Event(em)
        self.onKickedFromQueue = Event.Event(em)
        self.onPropertiesReceived = Event.Event(em)
        self.onPropertyUpdated = Event.Event(em)
        return

    def destroy(self):
        self.__eventManager.clear()

    def update(self, updateType, argStr):
        delegateName = self.__onUpdate.get(updateType, None)
        if delegateName is not None:
            getattr(self, delegateName)(argStr)
        return

    def __accInfoAsDict(self, accInfoAsTuple):
        pID, name, dbID, badges, roster, state, time, vehCompDescr, igrType, clanDBID, clanAbbrev, group = accInfoAsTuple
        return (roster, pID, {'name': name,
          'dbID': dbID,
          'badges': badges,
          'state': state,
          'time': time,
          'vehCompDescr': vehCompDescr,
          'clanDBID': clanDBID,
          'clanAbbrev': clanAbbrev,
          'igrType': igrType,
          'group': group})

    def __onRosterReceived(self, argStr):
        rostersAsList = cPickle.loads(argStr)
        self.rosters.clear()
        for accInfoAsTuple in rostersAsList:
            roster, pID, accInfo = self.__accInfoAsDict(accInfoAsTuple)
            self.rosters.setdefault(roster, {})[pID] = accInfo

        self.onRosterReceived()

    def __onPlayerAdded(self, argStr):
        accInfoAsTuple = cPickle.loads(argStr)
        roster, pID, accInfo = self.__accInfoAsDict(accInfoAsTuple)
        self.rosters.setdefault(roster, {})[pID] = accInfo
        self.onPlayerAdded(pID, roster)

    def __onPlayerRemoved(self, argStr):
        pID, roster = cPickle.loads(argStr)
        name = self.rosters.get(roster, {}).pop(pID, {}).get('name', '')
        self.onPlayerRemoved(pID, roster, name)

    def __onPlayerStateChanged(self, argStr):
        pID, roster, state, vehCompDescr, igrType, badges, clanDBID, clanAbbrev = cPickle.loads(argStr)
        LOG_DEBUG_DEV('__onPlayerStateChanged', pID, roster, state, vehCompDescr, igrType, clanDBID, clanAbbrev)
        accInfo = self.rosters.get(roster, {}).get(pID, None)
        if accInfo is None:
            return
        else:
            accInfo['state'] = state
            accInfo['vehCompDescr'] = vehCompDescr
            accInfo['igrType'] = igrType
            accInfo['badges'] = badges
            accInfo['clanDBID'] = clanDBID
            accInfo['clanAbbrev'] = clanAbbrev
            self.onPlayerStateChanged(pID, roster)
            return

    def __onPlayerRosterChanged(self, argStr):
        pID, prevRoster, roster, actorID = cPickle.loads(argStr)
        accInfo = self.rosters.get(prevRoster, {}).pop(pID, None)
        self.rosters.setdefault(roster, {})[pID] = accInfo
        self.onPlayerRosterChanged(pID, prevRoster, roster, actorID)
        return

    def __onPlayerGroupChanged(self, argStr):
        groupId, prevRoster, roster, group, actorID = cPickle.loads(argStr)
        accInfo = self.rosters.get(prevRoster, {}).pop(groupId, None)
        self.rosters.setdefault(roster, {})[groupId] = accInfo
        self.rosters.setdefault(roster, {}).setdefault(groupId, {})['group'] = group
        self.onPlayerGroupChanged(groupId, prevRoster, roster, group, actorID)
        return

    def __onTeamStatesReceived(self, argStr):
        team1, team2 = cPickle.loads(argStr)
        self.teamStates = [None, team1, team2]
        self.onTeamStatesReceived()
        return

    def __onSettingsReceived(self, argStr):
        self.settings = cPickle.loads(argStr)
        self.onSettingsReceived()

    def __onSettingUpdated(self, argStr):
        name, value = cPickle.loads(argStr)
        self.settings[name] = value
        self.onSettingUpdated(name)

    def __onPropertiesReceived(self, argStr):
        self.properties = cPickle.loads(argStr)
        self.onPropertiesReceived()

    def __onPropertyUpdated(self, argStr):
        name, value = cPickle.loads(argStr)
        self.properties[name] = value
        self.onPropertyUpdated(name)

    def __onKickedFromQueue(self, argStr):
        self.onKickedFromQueue()
