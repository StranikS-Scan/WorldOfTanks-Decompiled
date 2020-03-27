# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/settings.py
import time
from contextlib import contextmanager
from gui.shared import utils
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class _PMSettings(utils.SettingRecord):

    def __init__(self, introShown=False, operationsVisited=None, headerAlert=False):
        super(_PMSettings, self).__init__(introShown=introShown, operationsVisited=operationsVisited or set(), headerAlert=headerAlert)

    def markOperationAsVisited(self, operationID):
        self.update(operationsVisited=self.operationsVisited | {operationID})


class _DQSettings(utils.SettingRecord):

    def __init__(self, lastVisitedDQTabIdx=None, premMissionsTabDiscovered=False, *args, **kwargs):
        super(_DQSettings, self).__init__(lastVisitedDQTabIdx=lastVisitedDQTabIdx, premMissionsTabDiscovered=premMissionsTabDiscovered)

    def setLastVisitedDQTab(self, lastVisitedDQTabIdx):
        self.update(lastVisitedDQTabIdx=lastVisitedDQTabIdx)

    def onPremMissionsTabDiscovered(self):
        self.update(premMissionsTabDiscovered=True)


class _QuestSettings(utils.SettingRootRecord):

    def __init__(self, lastVisitTime=-1, visited=None, naVisited=None, minimized=None, personalMissions=None, dailyQuests=None, questDeltas=None):
        super(_QuestSettings, self).__init__(lastVisitTime=lastVisitTime, visited=visited or set(), naVisited=naVisited or set(), minimized=minimized or set(), personalMissions=_PMSettings(**(personalMissions or {})), dailyQuests=_DQSettings(**(dailyQuests or {})), questDeltas=questDeltas or dict())

    def updateVisited(self, visitSettingName, eventID):
        settingsValue = set(self[visitSettingName])
        if eventID not in settingsValue:
            self.update(**{visitSettingName: tuple(settingsValue | {eventID})})
            return True
        return False

    def removeCompleted(self, completedIDs):
        self.update(visited=tuple(set(self.visited).difference(completedIDs)))
        self.update(naVisited=tuple(set(self.naVisited).difference(completedIDs)))

    def updateExpanded(self, eventID, isExpanded):
        settingsValue = set(self['minimized'])
        if isExpanded:
            self.update(minimized=tuple(settingsValue.difference([eventID])))
        else:
            self.update(minimized=tuple(settingsValue.union([eventID])))

    def save(self):
        self.update(lastVisitTime=time.time())
        super(_QuestSettings, self).save()

    def _asdict(self):
        result = super(_QuestSettings, self)._asdict()
        result.update(personalMissions=self.personalMissions._asdict())
        result.update(dailyQuests=self.dailyQuests._asdict())
        return result

    @classmethod
    def _getSettingName(cls):
        pass


def get():
    return _QuestSettings.load()


def isNewCommonEvent(svrEvent, settings=None):
    settings = settings or get()
    if svrEvent.isAvailable()[0]:
        setting = 'visited'
    else:
        setting = 'naVisited'
    return settings is not None and svrEvent.getID() not in settings[setting] and not svrEvent.isCompleted() and not svrEvent.isOutOfDate()


def isGroupMinimized(groupID, settings=None):
    settings = settings or get()
    return groupID in settings['minimized']


def getNewCommonEvents(events):
    settings = get()
    return [ e for e in events if isNewCommonEvent(e, settings) ]


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def visitEventGUI(event, counters=(), eventsCache=None):
    if event is None:
        return
    else:
        s = get()
        isNaVisitedChanged = s.updateVisited('naVisited', event.getID())
        if event.isAvailable()[0]:
            isVisitedChanged = s.updateVisited('visited', event.getID())
        else:
            isVisitedChanged = False
        if isNaVisitedChanged or isVisitedChanged:
            s.save()
            converted = {}
            for counter in counters:
                key, value = counter(eventsCache)
                converted[key] = value

            eventsCache.onEventsVisited(converted)
        return


def visitEventsGUI(events):
    if events:
        for event in events:
            visitEventGUI(event)


def expandGroup(groupID, isExpanded):
    if groupID is None:
        return
    else:
        s = get()
        s.updateExpanded(groupID, isExpanded)
        s.save()
        return


def updateCommonEventsSettings(svrEvents):
    s = get()
    s.removeCompleted(set((e.getID() for e in svrEvents.itervalues() if e.isCompleted())))
    s.save()


def _updatePMSettings(**kwargs):
    settings = get()
    settings.personalMissions.update(**kwargs)
    settings.save()


def isPMOperationNew(operationID, pmSettings=None):
    pqSettings = pmSettings or get()
    return operationID not in pqSettings.personalMissions.operationsVisited


def isNeedToShowHeaderAlert():
    return get().personalMissions.headerAlert


def markHeaderAlertAsVisited():
    _updatePMSettings(headerAlert=True)


def getDQSettings():
    return get().dailyQuests


@contextmanager
def dailyQuestSettings():
    s = get()
    yield s.dailyQuests
    s.save()
