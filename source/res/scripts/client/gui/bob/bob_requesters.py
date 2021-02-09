# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_requesters.py
import logging
import weakref
import typing
import Event
import async
from adisp import process
from bob_common import deserializeActivatedSkill, deserializeRecalculate
from gui.bob.bob_data_containers import TeamSkillData, TeamData, RecalculationData
from gui.game_control.reactive_comm import Subscription
from gui.wgcg.bob.contexts import BobGetTeamsCtx, BobGetTeamSkillsCtx
from helpers import dependency, isPlayerAvatar
from skeletons.gui.game_control import IReactiveCommunicationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import IBobController
_logger = logging.getLogger(__name__)

class AbstractRequester(object):
    __slots__ = ('onUpdated', '_bobController', '__cache', '__isStarted', '__subscription', '_eventsManager')
    __webController = dependency.descriptor(IWebController)
    __RCService = dependency.descriptor(IReactiveCommunicationService)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, bobController):
        super(AbstractRequester, self).__init__()
        self._bobController = weakref.proxy(bobController)
        self.__cache = dict()
        self.__isStarted = False
        self.__subscription = None
        self._eventsManager = Event.EventManager()
        self.onUpdated = Event.Event(self._eventsManager)
        return

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def dataType(self):
        raise NotImplementedError

    def start(self):
        isBobSeasonActive = self._bobController.isRegistrationPeriodEnabled() or bool(self._bobController.getCurrentSeason())
        if not self.__isStarted and self._bobController.isRegistered() and isBobSeasonActive:
            self.__isStarted = True
            self._request()
            self._itemsCache.onSyncCompleted += self._onSyncCompleted

    def resume(self):
        if not self.__isStarted:
            return
        self._itemsCache.onSyncCompleted += self._onSyncCompleted
        self.__subscride()

    def suspend(self):
        if not self.__isStarted:
            return
        self._itemsCache.onSyncCompleted -= self._onSyncCompleted
        self.__clearSubscription()
        self._eventsManager.clear()

    def stop(self):
        self.__isStarted = False
        self._itemsCache.onSyncCompleted -= self._onSyncCompleted
        self.__clearSubscription()
        self._eventsManager.clear()
        self.__cache.clear()

    def getCache(self):
        return self.__cache

    def isCacheEmpty(self):
        return not bool(self.__cache)

    @process
    def _request(self):
        ctx = self._getCtx()
        response = yield self.__webController.sendRequest(ctx=ctx)
        getLastMessage = True
        if response.isSuccess():
            data = ctx.getDataObj(response.getData())
            self._processingData(data)
            getLastMessage = False
        self.__subscride(getLastMessage=getLastMessage)

    def _getChannelName(self):
        raise NotImplementedError

    def _getCtx(self):
        raise NotImplementedError

    def _processingData(self, data):
        raise NotImplementedError

    def _onSyncCompleted(self, _, diff):
        raise NotImplementedError

    def _onMessage(self, message):
        raise NotImplementedError

    def _updateData(self, newData):
        if newData is None or not hasattr(newData, 'team'):
            return False
        elif newData.team in self.__cache and cmp(self.__cache[newData.team], newData) >= 0:
            return False
        else:
            self.__cache[newData.team] = newData
            return True

    def _updateDataFromDict(self, newData):
        if isinstance(newData, dict) and set(newData.keys()) >= self.dataType.requiredFields():
            return self._updateData(self.dataType(**newData))
        _logger.warning('Dict %s does not have all needed keys %s', newData, self.dataType.requiredFields())
        return False

    def _onUpdate(self, newValues, updateFunc):
        isUpdated = False
        for newValue in newValues:
            isUpdated |= updateFunc(newValue)

        if isUpdated:
            self.onUpdated()

    def __onClosed(self, reason):
        self.__clearSubscription()

    @async.async
    def __subscride(self, getLastMessage=True):
        if isPlayerAvatar():
            return
        self.__subscription = Subscription(self._getChannelName())
        result = yield async.await(self.__RCService.subscribeToChannel(self.__subscription))
        if result:
            self.__subscription.onMessage += self._onMessage
            self.__subscription.onClosed += self.__onClosed
            if getLastMessage:
                self.__RCService.getLastMessageFromChannel(self.__subscription)
        else:
            self.__clearSubscription()

    def __clearSubscription(self):
        if self.__subscription is not None:
            self.__subscription.onMessage -= self._onMessage
            self.__subscription.onClosed -= self.__onClosed
            self.__RCService.unsubscribeFromChannel(self.__subscription)
            self.__subscription = None
        return


class TeamsRequester(AbstractRequester):
    __slots__ = ('onRecalculationUpdated', '__nextRecalculation')

    def __init__(self, bobController):
        super(TeamsRequester, self).__init__(bobController)
        self.__nextRecalculation = None
        self.onRecalculationUpdated = Event.Event(self._eventsManager)
        return

    @property
    def dataType(self):
        return TeamData

    def getTeam(self, teamID):
        team = self.getCache().get(teamID)
        if team is None:
            _logger.warning('Bob team requester does not have team with id = %s.', teamID)
        return team

    def getTeamsList(self):
        return self.getCache().values()

    def getTeamsAsJson(self):
        result = {'teams': [ team.asDict() for team in self.getCache().values() ]}
        if self.__nextRecalculation is not None:
            result.update({'correcting_coefficient': self.__nextRecalculation.asDict()})
        return result

    def getNextRecalculation(self):
        return self.__nextRecalculation

    def _getCtx(self):
        return BobGetTeamsCtx()

    def _getChannelName(self):
        return self._bobController.teamsChannelName

    def _onSyncCompleted(self, _, diff):
        if 'bob' in diff:
            self._onUpdate(self._itemsCache.items.bob.getTeams(), lambda teamID: self._updateData(self._itemsCache.items.bob.getTeamData(teamID)))
            self.__updateRacelculation(self._itemsCache.items.bob.getRecalculationData())

    def _onMessage(self, message):
        newValues = deserializeRecalculate(message)
        if newValues is None or not newValues:
            return
        else:
            self._onUpdate(newValues.get('teams', {}).values(), self._updateDataFromDict)
            self.__updateRacelculation(RecalculationData(is_recalculating=newValues.get('is_recalculating', False), next_recalculation_timestamp=newValues.get('timestamp', 0)))
            return

    def _processingData(self, data):
        self._onUpdate(data.get('teams', []), self._updateDataFromDict)
        self.__updateRecalculationFromDict(data.get('correcting_coefficient', {}))

    def __updateRecalculationFromDict(self, recalculation):
        if isinstance(recalculation, dict) and set(recalculation.keys()) == set(RecalculationData._fields):
            self.__updateRacelculation(RecalculationData(**recalculation))

    def __updateRacelculation(self, recalculationData):
        if self.__nextRecalculation and self.__nextRecalculation > recalculationData:
            return
        self.__nextRecalculation = recalculationData
        self.onRecalculationUpdated()


class TeamSkillsRequester(AbstractRequester):
    __slots__ = ('__timestamp',)

    def __init__(self, bobController):
        super(TeamSkillsRequester, self).__init__(bobController)
        self.__timestamp = None
        return

    @property
    def dataType(self):
        return TeamSkillData

    def getSkill(self, teamID):
        return self.getCache().get(teamID)

    def getCurrentTeamSkill(self):
        return self.getCache().get(self._bobController.getCurrentTeamID())

    def getSkillsAsJson(self):
        return {'skills': [ skill.asDict() for skill in self.getCache().values() ]}

    def doForcedRequest(self, timestamp):
        self.__timestamp = timestamp
        self._request()

    def _getCtx(self):
        timestamp = self.__timestamp
        self.__timestamp = None
        return BobGetTeamSkillsCtx(timestamp=timestamp)

    def _getChannelName(self):
        return self._bobController.teamSkillsChannelName

    def _onSyncCompleted(self, _, diff):
        if 'bob' in diff:
            teamIDs = set(self._itemsCache.items.bob.getSkills().keys())
            teamIDs.update(self.getCache().keys())
            self._onUpdate(teamIDs, lambda teamID: self._updateData(self._itemsCache.items.bob.getTeamSkillData(teamID)))

    def _onMessage(self, message):
        newSkills = deserializeActivatedSkill(message)
        if newSkills is None:
            return
        else:
            cache = self.getCache()
            for teamID in cache:
                if teamID not in newSkills:
                    newSkills[teamID] = dict(team=teamID, skill='', activated_at=0, expire_at=None, count_left=0)

            self._onUpdate(newSkills.values(), self._updateDataFromDict)
            return

    def _processingData(self, data):
        self._onUpdate(data.get('skills', []), self._updateDataFromDict)
