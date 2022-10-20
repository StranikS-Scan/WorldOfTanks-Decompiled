# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_progress_controller.py
from itertools import chain
import typing
import time
from functools import partial
from collections import namedtuple
import BigWorld
import HWAccountSettings
from constants import EVENT_CLIENT_DATA
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events import conditions
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.shared.gui_items.artefacts import Equipment
from gui.shared.utils.requesters import REQ_CRITERIA
from halloween.hw_constants import PhaseType, INVALID_PHASE_INDEX, HALLOWEEN_GROUP_PHASES_PREFIX, HALLOWEEN_GROUP_POST_PHASES_PREFIX, HALLOWEEN_GROUP_PHASES_SUFFIX, GROUP_PREFIX_TO_PHASE_TYPE, QUEST_SUFFIX_TO_TYPE, QuestType, PhaseState, HWBonusesType, ORDERED_EQUIPMENT_LIST
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from helpers import dependency
from items import tankmen
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from shared_utils import findFirst
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from halloween.hw_constants import AccountSettingsKeys
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest

def parseIndex(quest):
    return int(quest.getID().split('_')[-1])


PhaseBoosterInfo = namedtuple('PhaseBoosterInfo', ('bonusName', 'bonusValue', 'isActive', 'startTime', 'finishTime', 'timeLeft'))

class PhaseTransition(object):
    STARTED = 1
    ENDED = 2


class PhaseNotifiable(object):

    def __init__(self):
        super(PhaseNotifiable, self).__init__()
        self.startNotificators = {}
        self.endNotificators = {}

    def clearNotification(self):
        for notificationCallbackID in chain(self.startNotificators.itervalues(), self.endNotificators.itervalues()):
            if notificationCallbackID:
                BigWorld.cancelCallback(notificationCallbackID)

        self.startNotificators.clear()
        self.endNotificators.clear()

    def cancelNotification(self, phaseIndex, transition):
        notificators = self.startNotificators if transition == PhaseTransition.STARTED else self.endNotificators
        notificationCallbackID = notificators.get(phaseIndex)
        if notificationCallbackID:
            BigWorld.cancelCallback(notificationCallbackID)
        notificators[phaseIndex] = None
        return

    def addNotification(self, phaseIndex, transition, delta, callback):
        notificators = self.startNotificators if transition == PhaseTransition.STARTED else self.endNotificators
        notificators[phaseIndex] = BigWorld.callback(delta, callback)


class HalloweenProgressController(IHalloweenProgressController, PhaseNotifiable):
    eventsCache = dependency.descriptor(IEventsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)
    _PHASE_TIME_OFFSET = 1

    def __init__(self):
        super(HalloweenProgressController, self).__init__()
        self._em = EventManager()
        self.onQuestsUpdated = Event(self._em)
        self.onSyncCompleted = Event(self._em)
        self.onChangeActivePhase = Event(self._em)
        self.onCompleteActivePhase = Event(self._em)
        self.phasesHalloween = HalloweenPhases()

    def init(self):
        super(HalloweenProgressController, self).init()
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self._onQuestsUpdated,
         'tokens': self._onSyncCompleted})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._em.clear()
        self.phasesHalloween.fini()
        super(HalloweenProgressController, self).fini()

    def onAccountBecomePlayer(self):
        super(HalloweenProgressController, self).onAccountBecomePlayer()
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self.eventsCache.onProgressUpdated += self._onSyncCompleted
        self._onSyncCompleted()
        self.phasesHalloween.onAccountBecomePlayer()

    def onAccountBecomeNonPlayer(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.eventsCache.onProgressUpdated -= self._onSyncCompleted
        self.phasesHalloween.onAccountBecomeNonPlayer()
        self.clearNotification()
        super(HalloweenProgressController, self).onAccountBecomeNonPlayer()

    def isPostPhase(self):
        return self.phasesHalloween.getActivePhase(PhaseType.POST) is not None

    def _onQuestsUpdated(self, diff):
        self.phasesHalloween.onQuestsUpdated(diff)
        self._setNotifier()
        self.onQuestsUpdated()

    def _onSyncCompleted(self, *args, **kwargs):
        self.phasesHalloween.onSyncCompleted()
        self._setNotifier()
        self.onSyncCompleted()

    def _setNotifier(self):
        self._addNextActivePhaseNotifiers()

    def _addNextActivePhaseNotifiers(self):
        self._addActivePhaseEndNotifier()
        self._addActivePhaseStartNotifier()

    def _addActivePhaseStartNotifier(self):
        nextActivePhase = self.phasesHalloween.getNextActivePhase()
        return self.__addNotificatorCallbacks(nextActivePhase, PhaseTransition.STARTED)

    def _addActivePhaseEndNotifier(self):
        activePhase = self.phasesHalloween.getActivePhase()
        return self.__addNotificatorCallbacks(activePhase, PhaseTransition.ENDED)

    def __addNotificatorCallbacks(self, phase, transition):
        if phase is None:
            return
        else:
            self.cancelNotification(phase.phaseIndex, transition)
            callback = partial(self.__onPhaseStateUpdateCallback, phase.phaseIndex, transition)
            self.addNotification(phase.phaseIndex, transition, self.__getTimer(phase.phaseIndex, transition), callback)
            return

    def __getTimer(self, phaseIndex, transition):
        phase = self.phasesHalloween.getPhaseByIndex(phaseIndex)
        if not phase:
            return 0
        isPhaseStarted = transition == PhaseTransition.STARTED
        timeLeft = phase.getTimeLeftToStart() if isPhaseStarted else phase.getTimeLeftToFinish()
        return timeLeft + self._PHASE_TIME_OFFSET

    def __onPhaseStateUpdateCallback(self, phaseIndex, transition):
        if transition == PhaseTransition.STARTED:
            self.onChangeActivePhase(phaseIndex)
        else:
            self.onCompleteActivePhase(phaseIndex)
            self.__eventBattlesCtrl.onCompleteActivePhase()
        self.cancelNotification(phaseIndex, transition)
        self._addNextActivePhaseNotifiers()
        self.__sendSystemMessage(phaseIndex, transition)

    def __sendSystemMessage(self, phaseIndex, transition):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'phaseIndex': phaseIndex,
         'transition': transition}, SCH_CLIENT_MSG_TYPE.EVENT_LIFETIME_TYPE)


class Phases(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, questGroupPrefixes):
        super(Phases, self).__init__()
        self._items = {}
        self._questGroupPrefixes = questGroupPrefixes
        self._arenaActivePhaseIndex = INVALID_PHASE_INDEX
        self.onArenaActivePhaseChanged = Event()

    def fini(self):
        self.onArenaActivePhaseChanged.clear()

    def onAccountBecomePlayer(self):
        self._arenaActivePhaseIndex = INVALID_PHASE_INDEX

    def onAccountBecomeNonPlayer(self):
        self._items = {}

    def getCountPhases(self):
        return len(self._items)

    def getActivePhase(self, phaseType=PhaseType.ALL):
        return findFirst(lambda phase: phase.isActive() and phase.phaseType & phaseType, self._items.itervalues())

    def setArenaActivePhaseIndex(self, activePhaseIndex):
        self._arenaActivePhaseIndex = activePhaseIndex
        self.onArenaActivePhaseChanged(activePhaseIndex)

    def getActivePhaseIndex(self, phaseType=PhaseType.ALL):
        activePhase = self.getActivePhase()
        return activePhase.phaseIndex if activePhase and activePhase.phaseType & phaseType else self._arenaActivePhaseIndex

    def getPhaseByIndex(self, phaseIndex):
        return self._items.get(phaseIndex)

    def getPhasesByType(self, phaseType=PhaseType.ALL):
        return [ phase for phase in self._items.itervalues() if phase.phaseType & phaseType ]

    def getNextActivePhase(self):
        activePhase = self.getActivePhase()
        if activePhase is not None:
            return self._items.get(activePhase.phaseIndex + 1)
        else:
            for phaseIndex in xrange(1, self.getCountPhases() + 1):
                phase = self._items.get(phaseIndex)
                if phase and phase.getTimeLeftToStart() > 0:
                    return phase

            return

    def hasActiveRegularePhase(self):
        return self.getActivePhase(phaseType=PhaseType.REGULAR) is not None

    def onSyncCompleted(self):
        raise NotImplementedError

    def onQuestsUpdated(self, diff):
        raise NotImplementedError

    def _isMyGroup(self, group):
        groupID = group.getID()
        return groupID and any((groupID.startswith(prefix) for prefix in self._questGroupPrefixes))

    def _getGroupPrefix(self, group):
        prefix, _ = group.getID().split(':')
        return prefix


class HalloweenPhases(Phases):

    def __init__(self):
        super(HalloweenPhases, self).__init__([HALLOWEEN_GROUP_PHASES_PREFIX, HALLOWEEN_GROUP_POST_PHASES_PREFIX])

    def getPrevPhase(self):
        return HWAccountSettings.getSettings(AccountSettingsKeys.PREVIOUS_PHASE)

    def setPrevPhase(self, phase):
        HWAccountSettings.setSettings(AccountSettingsKeys.PREVIOUS_PHASE, phase)

    def onSyncCompleted(self):
        phases = {(parseIndex(g), self._getGroupPrefix(g)) for g in self.eventsCache.getGroups().itervalues() if self._isMyGroup(g)}
        self._items = {phaseIndex:Phase(phaseIndex, group, HALLOWEEN_GROUP_PHASES_SUFFIX.format(index=phaseIndex)) for phaseIndex, group in phases}

    def onQuestsUpdated(self, diff):
        for phase in self._items.itervalues():
            phase.onQuestsUpdated()


class Phase(object):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, phaseIndex, questGroupPrefix, questGroupSuffix):
        super(Phase, self).__init__()
        self._items = []
        self._phaseIndex = phaseIndex
        self._questGroupPrefix = questGroupPrefix
        self._questGroupSuffix = questGroupSuffix
        self.onQuestsUpdated()

    @property
    def items(self):
        return self._items

    @property
    def phaseIndex(self):
        return self._phaseIndex

    @property
    def phaseType(self):
        return GROUP_PREFIX_TO_PHASE_TYPE.get(self._questGroupPrefix, PhaseType.NONE)

    def getQuestsByType(self, questType):
        return [ item for item in self._items if item.getType() == questType ]

    def onQuestsUpdated(self):
        self._items = []
        quests = sorted([ q for q in self.eventsCache.getAllQuests(noSkip=True).itervalues() if self._isMyPhaseQuest(q) ], key=parseIndex)
        for quest in quests:
            self._items.append(ProgressQuest(quest))

    def isActive(self):
        quest = self.__getModelQuest()
        return quest.getStartTimeLeft() <= 0 and quest.getFinishTimeLeft() > 0 if quest else False

    def isOutOfDate(self):
        return self.getTimeLeftToFinish() <= 0

    def isLock(self):
        return self.getTimeLeftToStart() > 0

    def getState(self):
        if self.isActive():
            return PhaseState.ACTIVE
        return PhaseState.OUT_OF_DATE if self.isOutOfDate() else PhaseState.LOCK

    def getStartTime(self):
        quest = self.__getModelQuest()
        return quest.getStartTime() if quest else 0

    def getFinishTime(self):
        quest = self.__getModelQuest()
        return quest.getFinishTime() if quest else time.time()

    def getTimeLeftToStart(self):
        quest = self.__getModelQuest()
        return quest.getStartTimeLeft() if quest else 0

    def getTimeLeftToFinish(self):
        quest = self.__getModelQuest()
        return quest.getFinishTimeLeft() if quest else 0

    def hasPlayerTmanBonus(self):
        tokenID = self.getTmanTokenBonus()
        if not tokenID:
            return False
        count = self.eventsCache.questsProgress.getTokenCount(tokenID)
        if count > 0:
            return True
        tmen = self.itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.ACTIVE ^ REQ_CRITERIA.TANKMAN.DISMISSED)
        groupName = tokenID.split(':')[3]
        for tman in tmen.itervalues():
            group = findFirst(lambda g: g.name == groupName, tankmen.getNationGroups(tman.descriptor.nationID, tman.descriptor.isPremium).itervalues())
            if not group:
                continue
            if tman.descriptor.firstNameID in group.firstNames and tman.descriptor.lastNameID in group.lastNames and tman.descriptor.iconID in group.icons:
                return True

        return False

    def getTmanTokenBonus(self):
        for q in self.getQuestsByType(QuestType.HALLOWEEN):
            bonusesInfo = q.getBonusesInfo()
            _, _, tokenID, _ = findFirst(lambda item: item[0] == 'tmanToken', bonusesInfo, (None, None, None, None))
            if not tokenID:
                continue
            return tokenID

        return ''

    def getAbilityInfo(self, dailyQuest=False):
        missionData = None
        for quest in self.getQuestsByType(QuestType.RANDOM):
            data = getMissionInfoData(quest.getQuest())
            if data.event.bonusCond.isDaily() == dailyQuest:
                missionData = data
                break

        if not missionData:
            return
        else:
            abilityBonus = findFirst(lambda bonus: any((isinstance(item, Equipment) for item in bonus.getItems())), missionData.getSubstituteBonuses())
            if not abilityBonus:
                return
            equipment, countItem = findFirst(lambda item: isinstance(item[0], Equipment) and item[0].name in ORDERED_EQUIPMENT_LIST, abilityBonus.getItems().iteritems(), (None, 0))
            return None if not equipment else (equipment, countItem, missionData)

    def _isMyPhaseQuest(self, quest):
        groupID = quest.getGroupID()
        return groupID and groupID.startswith(self._questGroupPrefix) and groupID.endswith(self._questGroupSuffix)

    def __getModelQuest(self):
        return self._items[0]


def getProgressInfo(quest):
    info = {'currentProgress': 0,
     'totalProgress': 0,
     'key': ''}
    for condition in quest.bonusCond.getConditions().items:
        if isinstance(condition, conditions._Cumulativable):
            info.update({'key': condition.getKey(),
             'totalProgress': condition.getTotalValue()})
            break

    if quest.isCompleted():
        info.update({'currentProgress': info['totalProgress']})
    else:
        progress = quest.getProgressData().get(None, {})
        if progress:
            info.update({'currentProgress': progress.get(info['key'], 0)})
    return info


def sortedFunction(item):
    eqName, type, _, _ = item
    if type == HWBonusesType.EQUIPMENT:
        typeIndex = HWBonusesType.ORDERED_LIST.index(type) if type in HWBonusesType.ORDERED_LIST else -1
        eqIndex = HWBonusesType.EQUIPMENT_LIST.index(eqName) if eqName in HWBonusesType.EQUIPMENT_LIST else -1
        return typeIndex + eqIndex
    return HWBonusesType.ORDERED_LIST.index(type) if type in HWBonusesType.ORDERED_LIST else 0


class ProgressQuest(object):

    def __init__(self, quest):
        super(ProgressQuest, self).__init__()
        self._quest = quest

    def getQuest(self):
        return self._quest

    def getQuestId(self):
        return self._quest.getID().replace(':', '_')

    def getType(self):
        _, suffix = self._quest.getID().split(':')
        key, _ = suffix.split('_')
        return QUEST_SUFFIX_TO_TYPE.get(key, QuestType.NONE)

    def getBonusesInfo(self):
        info = []
        for bonuses in getMissionInfoData(self._quest).getSubstituteBonuses():
            bonusesName = bonuses.getName()
            if bonusesName == 'tmanToken':
                for tmanTokenID, data in bonuses.getValue().iteritems():
                    info.append((bonusesName,
                     HWBonusesType.TANKMAN,
                     tmanTokenID,
                     data['count']))

            if bonusesName == 'customizations':
                for item in bonuses.getValue():
                    info.append((bonusesName,
                     item['custType'],
                     item['id'],
                     item['value']))

            if bonusesName == 'crystal':
                info.append((bonusesName,
                 HWBonusesType.CRYSTAL,
                 None,
                 bonuses.getValue()))
            if bonusesName == 'items':
                for item, count in bonuses.getItems().iteritems():
                    info.append((item.descriptor.groupName,
                     HWBonusesType.EQUIPMENT,
                     item,
                     count))

        return sorted(info, key=sortedFunction)

    def setQuest(self, quest):
        self._quest = quest

    def isAvailable(self):
        return self._quest.isAvailable().isValid

    def isCompleted(self):
        return self._quest.isCompleted()

    def isOutOfDate(self):
        return self._quest.getFinishTimeLeft() <= 0

    def isLock(self):
        return self.getStartTimeLeft() > 0

    def isUnlocked(self):
        return self.getStartTimeLeft() <= 0

    def getStartTime(self):
        return self._quest.getStartTime()

    def getStartTimeLeft(self):
        return self._quest.getStartTimeLeft()

    def getFinishTimeLeft(self):
        return self._quest.getFinishTimeLeft()

    def getFinishTime(self):
        return self._quest.getFinishTime()

    def getProgressInfo(self):
        return getProgressInfo(self._quest)
