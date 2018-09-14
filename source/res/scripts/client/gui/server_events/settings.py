# Embedded file name: scripts/client/gui/server_events/settings.py
import time
from gui.shared import utils, events, g_eventBus
_LAST_PQ_INTRO_VERSION = 'fallout'

class _PQSettings(utils.SettingRecord):

    def __init__(self, introShown = False, tilesVisited = set(), headerAlert = False):
        super(_PQSettings, self).__init__(introShown=introShown, tilesVisited=tilesVisited, headerAlert=headerAlert)

    def markTileAsVisited(self, tileID):
        self.update(tilesVisited=self.tilesVisited | {tileID})


class _QuestSettings(utils.SettingRootRecord):

    def __init__(self, lastVisitTime = -1, visited = set(), naVisited = set(), potapov = None):
        super(_QuestSettings, self).__init__(lastVisitTime=lastVisitTime, visited=visited, naVisited=naVisited, potapov=_PQSettings(**(potapov or {})))

    def updateVisited(self, visitSettingName, eventID):
        settingsValue = set(self[visitSettingName])
        if eventID not in settingsValue:
            self.update(**{visitSettingName: tuple(settingsValue | {eventID})})
            return True
        return False

    def removeCompleted(self, completedIDs):
        self.update(visited=tuple(set(self.visited).difference(completedIDs)))
        self.update(naVisited=tuple(set(self.naVisited).difference(completedIDs)))

    def save(self):
        self.update(lastVisitTime=time.time())
        super(_QuestSettings, self).save()

    def _asdict(self):
        result = super(_QuestSettings, self)._asdict()
        result.update(potapov=self.potapov._asdict())
        return result

    @classmethod
    def _getSettingName(cls):
        return 'quests'


def get():
    return _QuestSettings.load()


def isNewCommonEvent(svrEvent, settings = None):
    settings = settings or get()
    if svrEvent.isAvailable()[0]:
        setting = 'visited'
    else:
        setting = 'naVisited'
    return svrEvent.getID() not in settings[setting] and not svrEvent.isCompleted() and not svrEvent.isOutOfDate()


def getNewCommonEvents(svrEvents):
    return filter(lambda e: isNewCommonEvent(e, get()), svrEvents.itervalues())


def visitEventGUI(event):
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
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.EVENTS_UPDATED))
        return


def updateCommonEventsSettings(svrEvents):
    s = get()
    s.removeCompleted(set((e.getID() for e in svrEvents.itervalues() if e.isCompleted())))
    s.save()


def isNeedToShowPQIntro(pqCtrl):
    settings = get()
    isShown = _LAST_PQ_INTRO_VERSION == settings.potapov.introShown
    if not isShown:
        for q in pqCtrl.getQuests().itervalues():
            if q.hasProgress():
                return False

    return not isShown


def _updatePQSettings(**kwargs):
    settings = get()
    settings.potapov.update(**kwargs)
    settings.save()


def markPQIntroAsShown():
    _updatePQSettings(introShown=_LAST_PQ_INTRO_VERSION)


def isPQTileNew(tileID, pqSettings = None):
    pqSettings = pqSettings or get()
    return tileID not in pqSettings.potapov.tilesVisited


def markPQTileAsVisited(tileID):
    settings = get()
    settings.potapov.markTileAsVisited(tileID)
    settings.save()


def isNeedToShowHeaderAlert():
    return get().potapov.headerAlert


def markHeaderAlertAsVisited():
    _updatePQSettings(headerAlert=True)
