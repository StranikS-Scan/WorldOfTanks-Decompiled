# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_entry_point.py
import time
from functools import partial
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.marathon.marathon_entry_point_model import MarathonEntryPointModel
from gui.marathon.marathon_constants import MarathonState
from gui.server_events.event_items import Quest
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared import event_dispatcher, g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.server_events import IEventsCache
from helpers.time_utils import ONE_DAY, ONE_HOUR
from gui.impl import backport
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
_MARATHON_PREFIX = 'sabaton_marathon'
_eventsCache = dependency.descriptor(IEventsCache)

@dependency.replace_none_kwargs(marathonsCtrl=IMarathonEventsController)
def isMarathonEntryPointAvailable(marathonsCtrl=None):
    marathonEvent = marathonsCtrl.getMarathon(_MARATHON_PREFIX)
    if marathonEvent is not None:
        state = marathonEvent.getState()
    else:
        state = None
    if state in (MarathonState.NOT_STARTED, MarathonState.IN_PROGRESS):
        return True
    else:
        return True if state == MarathonState.FINISHED and not (marathonEvent.isRewardObtained() and marathonEvent.isPostRewardObtained()) else False


class MarathonEntryPoint(ViewImpl):
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.marathon.EntryPoint())
        settings.flags = flags
        settings.model = MarathonEntryPointModel()
        super(MarathonEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MarathonEntryPoint, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(MarathonEntryPoint, self)._initialize(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self._marathonsCtrl.onFlagUpdateNotify += self.__updateViewModel
        self._marathonsCtrl.onMarathonDataChanged += self.__updateViewModel
        self._eventsCache.onProgressUpdated += self.__updateViewModel

    def _finalize(self):
        super(MarathonEntryPoint, self)._finalize()
        self.viewModel.onClick -= self.__onClick
        self._marathonsCtrl.onFlagUpdateNotify -= self.__updateViewModel
        self._marathonsCtrl.onMarathonDataChanged -= self.__updateViewModel
        self._eventsCache.onProgressUpdated -= self.__updateViewModel

    def _onLoading(self, *args, **kwargs):
        super(MarathonEntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self, *_):
        if isMarathonEntryPointAvailable():
            marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
            with self.viewModel.transaction() as tx:
                state = marathonEvent.getState()
                currentPhase, phaseCount = marathonEvent.getMarathonProgress()
                timeTillNextState = marathonEvent.getClosestStatusUpdateTime()
                _, timeTillNextQuest = marathonEvent.getQuestTimeInterval()
                currentGrindQuest = self._eventsCache.getHiddenQuests(partial(self.__marathonFilterFunc, postfix=marathonEvent.grindPostfix)).values()
                currentProQuest = self._eventsCache.getHiddenQuests(partial(self.__marathonFilterFunc, postfix=marathonEvent.proPostfix)).values()
                currentPostQuest = self._eventsCache.getHiddenQuests(partial(self.__marathonPostFilterFunc, postfix=marathonEvent.postPostfix)).values()
                userTokens = marathonEvent.getTokensData(prefix=marathonEvent.tokenPrefix)
                if state in MarathonState.DISABLED_STATE:
                    state = MarathonEntryPointModel.STATE_MARATHON_DISABLED
                tx.progressGrind.clearItems()
                tx.progressPro.clearItems()
                tx.progressPost.clearItems()
                for quest in currentGrindQuest:
                    packer = BattleQuestUIDataPacker(quest)
                    tx.progressGrind.addViewModel(packer.pack())

                for quest in currentProQuest:
                    packer = BattleQuestUIDataPacker(quest)
                    tx.progressPro.addViewModel(packer.pack())

                for quest in currentPostQuest:
                    packer = BattleQuestUIDataPacker(quest)
                    tx.progressPost.addViewModel(packer.pack())

                for token in userTokens:
                    tx.getUserTokens().addString(token)

                tx.progressGrind.invalidate()
                tx.progressPro.invalidate()
                tx.progressPost.invalidate()
                tx.setState(state)
                tx.setTimeTillNextState(timeTillNextState)
                tx.setFormattedTimeTillNextState(self.__getFormattedTillTimeString(timeTillNextState, marathonEvent))
                tx.setTimeTillNextQuest(timeTillNextQuest)
                tx.setFormattedTimeTillNextQuest(self.__getFormattedTillTimeString(timeTillNextQuest, marathonEvent))
                tx.setCurrentPhase(currentPhase)
                isRewardObtained = marathonEvent.isRewardObtained()
                tx.setRewardObtained(marathonEvent.isRewardObtained())
                tx.setDiscount(marathonEvent.getMarathonDiscount(isPostprogress=isRewardObtained))
                tx.setIsPremShopURL(not marathonEvent.hasIgbLink())
                tx.setIsPostProgression(currentPhase == phaseCount)
                tx.setTokenTemplate(marathonEvent.tokenPrefix)
                tx.setTokenDoneTemplate(marathonEvent.stageDoneTemplate)
        else:
            self.destroy()

    def __onClick(self):
        marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
        if marathonEvent.getState() != MarathonState.FINISHED:
            showMissionsMarathon(marathonEvent.prefix)
            return
        self.__purchasePackage(marathonEvent)

    @process
    def __purchasePackage(self, marathonEvent):
        if marathonEvent.isRewardObtained():
            urlStyle = yield marathonEvent.getMarathonStyleUrlIgb()
            event_dispatcher.showShop(urlStyle)
            return
        if marathonEvent.hasIgbLink():
            url = yield marathonEvent.getMarathonVehicleUrlIgb()
            event_dispatcher.showShop(url)
        else:
            url = yield marathonEvent.getMarathonVehicleUrl()
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url=url))

    def __getFormattedTillTimeString(self, timeValue, marathonEvent):
        gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            text = backport.text(marathonEvent.entryTooltip.daysShort, value=str(gmtime.tm_yday))
        elif timeValue >= ONE_HOUR:
            text = backport.text(marathonEvent.entryTooltip.hoursShort, value=str(gmtime.tm_hour + 1))
        else:
            text = backport.text(marathonEvent.entryTooltip.minutesShort, value=str(gmtime.tm_min + 1))
        return text

    def __marathonFilterFunc(self, q, postfix=''):
        marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
        currentPhase, _ = marathonEvent.getMarathonProgress()
        return q.getID().startswith('{0}s{1}{2}'.format(marathonEvent.tokenPrefix, currentPhase + 1, postfix))

    def __marathonPostFilterFunc(self, q, postfix=''):
        marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
        return q.getID().startswith('{0}{1}s'.format(marathonEvent.tokenPrefix, postfix)) and q.isAvailable()[0]
