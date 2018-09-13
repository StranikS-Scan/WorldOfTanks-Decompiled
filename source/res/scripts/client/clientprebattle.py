# Embedded file name: scripts/client/ClientPrebattle.py
import cPickle
import Event
from constants import PREBATTLE_UPDATE, PREBATTLE_ACCOUNT_STATE, PREBATTLE_TEAM_STATE
from debug_utils import *

class ClientPrebattle(object):
    __onUpdate = {PREBATTLE_UPDATE.ROSTER: '_ClientPrebattle__onRosterReceived',
     PREBATTLE_UPDATE.PLAYER_ADDED: '_ClientPrebattle__onPlayerAdded',
     PREBATTLE_UPDATE.PLAYER_REMOVED: '_ClientPrebattle__onPlayerRemoved',
     PREBATTLE_UPDATE.PLAYER_STATE: '_ClientPrebattle__onPlayerStateChanged',
     PREBATTLE_UPDATE.PLAYER_ROSTER: '_ClientPrebattle__onPlayerRosterChanged',
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
        id, name, dbID, roster, state, time, vehCompDescr, igrType, clanDBID, clanAbbrev = accInfoAsTuple
        return (roster, id, {'name': name,
          'dbID': dbID,
          'state': state,
          'time': time,
          'vehCompDescr': vehCompDescr,
          'clanDBID': clanDBID,
          'clanAbbrev': clanAbbrev,
          'igrType': igrType})

    def __onRosterReceived(self, argStr):
        rostersAsList = cPickle.loads(argStr)
        self.rosters.clear()
        for accInfoAsTuple in rostersAsList:
            roster, id, accInfo = self.__accInfoAsDict(accInfoAsTuple)
            self.rosters.setdefault(roster, {})[id] = accInfo

        self.onRosterReceived()

    def __onPlayerAdded(self, argStr):
        accInfoAsTuple = cPickle.loads(argStr)
        roster, id, accInfo = self.__accInfoAsDict(accInfoAsTuple)
        self.rosters.setdefault(roster, {})[id] = accInfo
        self.onPlayerAdded(id, roster)

    def __onPlayerRemoved(self, argStr):
        id, roster = cPickle.loads(argStr)
        name = self.rosters.get(roster, {}).pop(id, {}).get('name', '')
        self.onPlayerRemoved(id, roster, name)

    def __onPlayerStateChanged(self, argStr):
        id, roster, state, vehCompDescr, igrType, clanDBID, clanAbbrev = cPickle.loads(argStr)
        LOG_DEBUG_DEV('__onPlayerStateChanged', id, roster, state, vehCompDescr, igrType, clanDBID, clanAbbrev)
        accInfo = self.rosters.get(roster, {}).get(id, None)
        if accInfo is None:
            return
        else:
            accInfo['state'] = state
            accInfo['vehCompDescr'] = vehCompDescr
            accInfo['igrType'] = igrType
            accInfo['clanDBID'] = clanDBID
            accInfo['clanAbbrev'] = clanAbbrev
            self.onPlayerStateChanged(id, roster)
            return

    def __onPlayerRosterChanged(self, argStr):
        id, prevRoster, roster, actorID = cPickle.loads(argStr)
        accInfo = self.rosters.get(prevRoster, {}).pop(id, None)
        self.rosters.setdefault(roster, {})[id] = accInfo
        self.onPlayerRosterChanged(id, prevRoster, roster, actorID)
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
