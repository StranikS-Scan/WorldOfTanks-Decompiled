# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/event_daily_reward.py
from gui.Scaleform.daapi.view.meta.EventDailyRewardMeta import EventDailyRewardMeta
from gui.impl.gen import R
from gui.impl import backport
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from halloween.hw_constants import PhaseType
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from halloween.gui.shared.event_dispatcher import showDailyBonuseView

class EventDailyReward(EventDailyRewardMeta, IGlobalListener):
    _eventsCache = dependency.descriptor(IEventsCache)
    _eventController = dependency.descriptor(IEventBattlesController)
    _hwController = dependency.descriptor(IHalloweenProgressController)

    def onClick(self):
        showDailyBonuseView()

    def _populate(self):
        super(EventDailyReward, self)._populate()
        self.startGlobalListening()
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._hwController.onChangeActivePhase += self.__onChangeActivePhase
        self._hwController.onQuestsUpdated += self.__onQuestUpdated
        self.__update()

    def _dispose(self):
        self.stopGlobalListening()
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._hwController.onChangeActivePhase -= self.__onChangeActivePhase
        self._hwController.onQuestsUpdated -= self.__onQuestUpdated
        super(EventDailyReward, self)._dispose()

    def __onSyncCompleted(self):
        self.__update()

    def __onChangeActivePhase(self, _):
        self.__update()

    def __onQuestUpdated(self):
        self.__update()

    def __update(self):
        phases = self._hwController.phasesHalloween
        phase = phases.getActivePhase(PhaseType.REGULAR)
        if not phase:
            return
        dailyData = phase.getAbilityInfo(dailyQuest=True)
        if not dailyData:
            return
        equipment, _, dailyMissionData = dailyData
        self.as_setDataS({'rewardReady': not dailyMissionData.event.isCompleted(),
         'phaseIndex': phase.phaseIndex,
         'icon': backport.image(R.images.halloween.gui.maps.icons.artefact.dyn(equipment.descriptor.iconName)())})
