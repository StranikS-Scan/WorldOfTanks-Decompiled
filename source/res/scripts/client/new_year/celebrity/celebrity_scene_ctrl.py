# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/celebrity/celebrity_scene_ctrl.py
import logging
import typing
import BigWorld
from Event import Event, EventManager
from account_helpers.AccountSettings import AccountSettings, NY_CELEBRITY_CHALLENGE_VISITED, NY_CELEBRITY_QUESTS_COMPLETED_MASK, NY_CELEBRITY_WELCOME_VIEWED
from helpers import dependency
from items.components.ny_constants import CelebrityQuestTokenParts
from new_year.celebrity.celebrity_quests_helpers import getCelebrityQuestsGroups, getCelebrityQuests, getCelebrityMarathonQuests, getCelebrityTokens, getCelebrityQuestCount
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICelebritySceneController
if typing.TYPE_CHECKING:
    from NewYearCelebrityObject import NewYearCelebrityObject
    from NewYearCelebrityEntryObject import NewYearCelebrityEntryObject
    from gui.server_events.event_items import CelebrityGroup, TokenQuest, CelebrityQuest, CelebrityTokenQuest
_logger = logging.getLogger(__name__)

class _AnimationTriggers(object):
    HANGAR_IDLE = 'hangar_idle'
    CHALLENGE_IDLE = 'challenge_idle'
    CHALLENGE_WELCOME = 'challenge_welcome'
    QUEST_COMPLETED = 'quest_completed'
    QUEST_SIMPLIFIED = 'quest_simplified'


class _AnimationEvents(object):
    WELCOME_COMPLETED = 'ev_reveal_off'


class CelebritySceneController(ICelebritySceneController):
    __slots__ = ('__eventsManager', '__celebrityEntity', '__questGroups', '__quests', '__isInChallengeView', '__tokens', '__marathonQuests', '__completedQuestsMask', '__questsCount', '__completedQuestsCount')
    __newYearController = dependency.descriptor(INewYearController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(CelebritySceneController, self).__init__()
        self.__eventsManager = EventManager()
        self.onQuestsUpdated = Event(self.__eventsManager)
        self.onExitIntroScreen = Event(self.__eventsManager)
        self.__celebrityEntity = None
        self.__celebrityEntryEntity = None
        self.__questGroups = {}
        self.__quests = {}
        self.__tokens = {}
        self.__marathonQuests = {}
        self.__completedQuestsMask = 0
        self.__questsCount = 0
        self.__completedQuestsCount = 0
        self.__isInChallengeView = False
        return

    @property
    def isChallengeVisited(self):
        return AccountSettings.getUIFlag(NY_CELEBRITY_CHALLENGE_VISITED)

    @property
    def isWelcomeAnimationViewed(self):
        return AccountSettings.getUIFlag(NY_CELEBRITY_WELCOME_VIEWED)

    @property
    def isInChallengeView(self):
        return self.__isInChallengeView

    @property
    def isChallengeCompleted(self):
        return self.completedQuestsCount == self.questsCount

    @property
    def hasNewCompletedQuests(self):
        completedQuestsMask = self.__getCompletedQuestsMask()
        return bool(completedQuestsMask ^ self.__completedQuestsMask)

    @property
    def questGroups(self):
        return self.__questGroups

    @property
    def quests(self):
        return self.__quests

    @property
    def tokens(self):
        return self.__tokens

    @property
    def marathonQuests(self):
        return self.__marathonQuests

    @property
    def completedQuestsMask(self):
        return self.__completedQuestsMask

    @property
    def questsCount(self):
        return self.__questsCount

    @property
    def completedQuestsCount(self):
        return self.__completedQuestsCount

    def fini(self):
        self.__destroy()
        super(CelebritySceneController, self).fini()

    def onLobbyInited(self, _):
        self.__subscribe()
        self.__updateQuests()

    def onDisconnected(self):
        self.__destroy()

    def onAvatarBecomePlayer(self):
        self.__destroy()

    def addCelebrityEntity(self, entity):
        self.__celebrityEntity = entity

    def removeCelebrityEntity(self):
        self.__delEdgeDetect(self.__celebrityEntity)
        self.__celebrityEntity = None
        return

    def addCelebrityEntryEntity(self, entity):
        self.__celebrityEntryEntity = entity

    def removeCelebrityEntryEntity(self):
        self.__delEdgeDetect(self.__celebrityEntryEntity)
        self.__celebrityEntryEntity = None
        return

    def onEnterChallenge(self):
        self.__isInChallengeView = True
        if self.isChallengeCompleted:
            animationTrigger = _AnimationTriggers.QUEST_COMPLETED
        elif not self.isChallengeVisited and not self.isWelcomeAnimationViewed:
            animationTrigger = _AnimationTriggers.CHALLENGE_WELCOME
        elif self.hasNewCompletedQuests:
            animationTrigger = _AnimationTriggers.QUEST_COMPLETED
        else:
            animationTrigger = _AnimationTriggers.CHALLENGE_IDLE
        self.__setAnimationTrigger(animationTrigger)
        self.__saveCompletedQuestsMask()

    def onExitChallenge(self):
        self.__setAnimationTrigger(_AnimationTriggers.HANGAR_IDLE)
        self.__isInChallengeView = False

    def onSimplifyQuest(self):
        self.__setAnimationTrigger(_AnimationTriggers.QUEST_SIMPLIFIED)

    def onAnimatorEvent(self, name):
        if name == _AnimationEvents.WELCOME_COMPLETED:
            AccountSettings.setUIFlag(NY_CELEBRITY_WELCOME_VIEWED, True)

    def addEdgeDetect(self):
        self.__addEdgeDetect(self.__celebrityEntity)
        self.__addEdgeDetect(self.__celebrityEntryEntity)

    def delEdgeDetect(self):
        self.__delEdgeDetect(self.__celebrityEntity)
        self.__delEdgeDetect(self.__celebrityEntryEntity)

    def __addEdgeDetect(self, entity):
        if entity is not None:
            BigWorld.wgAddEdgeDetectEntity(entity, 3, entity.edgeMode, False)
        return

    def __delEdgeDetect(self, entity):
        if entity is not None:
            BigWorld.wgDelEdgeDetectEntity(entity)
        return

    def __destroy(self):
        self.__unsubscribe()
        self.__eventsManager.clear()
        self.__celebrityEntity = None
        self.__celebrityEntryEntity = None
        self.__questGroups.clear()
        self.__quests.clear()
        self.__tokens.clear()
        self.__marathonQuests.clear()
        self.__isInChallengeView = False
        return

    def __subscribe(self):
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__eventsCache.onQuestConditionUpdated += self.__onSyncCompleted

    def __unsubscribe(self):
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__eventsCache.onQuestConditionUpdated -= self.__onSyncCompleted

    def __onSyncCompleted(self):
        self.__updateQuests()

    def __setAnimationTrigger(self, triggerName):
        if not self.__hangarSpace.spaceInited:
            return
        elif self.__celebrityEntity is None:
            _logger.error('Failed to set animation state machine trigger: %s. Missing Celebrity Entity', triggerName)
            return
        else:
            self.__celebrityEntity.setAnimatorTrigger(triggerName)
            return

    def __updateQuests(self):
        self.__questGroups = getCelebrityQuestsGroups()
        self.__quests = getCelebrityQuests()
        self.__marathonQuests = getCelebrityMarathonQuests()
        self.__tokens = getCelebrityTokens()
        self.__completedQuestsMask = 0
        for groupId, group in self.__questGroups.iteritems():
            group.update(self.quests)
            if not group.isGroupCompleted:
                continue
            dayNum = CelebrityQuestTokenParts.getDayNum(groupId)
            dayNumBit = 1 << dayNum - 1
            self.__completedQuestsMask |= dayNumBit

        self.__questsCount = getCelebrityQuestCount()
        self.__completedQuestsCount = bin(self.completedQuestsMask).count('1')
        if self.__isInChallengeView:
            self.__saveCompletedQuestsMask()
        self.onQuestsUpdated()

    def __getCompletedQuestsMask(self):
        completedQuestsMask = AccountSettings.getUIFlag(NY_CELEBRITY_QUESTS_COMPLETED_MASK)
        return completedQuestsMask

    def __saveCompletedQuestsMask(self):
        AccountSettings.setUIFlag(NY_CELEBRITY_QUESTS_COMPLETED_MASK, self.__completedQuestsMask)
