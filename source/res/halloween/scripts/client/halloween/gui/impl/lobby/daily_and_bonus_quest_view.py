# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/daily_and_bonus_quest_view.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency, time_utils
from gui.server_events.bonuses import ItemsBonus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from halloween.gui.impl.lobby.base_event_view import BaseEventView
from gui.shared.utils import decorators
from frameworks.wulf import WindowFlags
from gui.shared.view_helpers.blur_manager import CachedBlur
from frameworks.wulf import WindowLayer
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.gui_items.processors import Processor
from frameworks.wulf import ViewFlags, ViewSettings
from halloween.gui.impl.gen.view_models.views.lobby.daily_and_bonus_quest_view_model import DailyAndBonusQuestViewModel
from halloween.hw_constants import HALLOWEEN_GROUP_PHASES_PREFIX, HALLOWEEN_GROUP_PHASES_SUFFIX
from halloween.hw_constants import PhaseType
from helpers.time_utils import getDateTimeInUTC
from skeletons.gui.lobby_context import ILobbyContext
from halloween.gui.shared.event_dispatcher import showHalloweenShop, showMissions
from halloween.gui.sounds.sound_constants import HW_HANGAR_OVERLAYS
from halloween.gui.impl.lobby.tooltips.daily_reward_tooltip import DailyRewardTooltip
_DAILY_QUEST_ID = 0
_BONUS_QUEST_ID = 1
_QUEST_FINISH_TIME_CORRECTION = 60

class HWApplyDailyBonusProcessor(Processor):

    def __init__(self, phaseIndex):
        super(HWApplyDailyBonusProcessor, self).__init__()
        self._phaseIndex = phaseIndex

    def _request(self, callback):
        accountComponent = BigWorld.player().HWAccountComponent
        accountComponent.applyDailyQuest(self._phaseIndex, lambda _, code, errStr, ctx=None: self._response(code, callback, errStr=errStr, ctx=ctx))
        return


class DailyAndBonusQuestView(BaseEventView):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()
    _COMMON_SOUND_SPACE = HW_HANGAR_OVERLAYS

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, DailyAndBonusQuestViewModel())
        super(DailyAndBonusQuestView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyAndBonusQuestView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        isBonusQuestCard = event.getArgument('isBonusQuestCard')
        return DailyRewardTooltip(isBonusQuestCard)

    def _getConfig(self):
        return self.__lobbyContext.getServerSettings().halloweenConfig

    def _initialize(self, *args, **kwargs):
        super(DailyAndBonusQuestView, self)._initialize(*args, **kwargs)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        super(DailyAndBonusQuestView, self)._finalize()

    def _subscribe(self):
        self.viewModel.dailyQuestModel.onGetBonusClick += self.__onDailyBonusClick
        self.viewModel.bonusQuestModel.onGoToTasks += self.__onGoToQuestsClick
        self.viewModel.shopCardModel.onGoToShop += self.__onGoToShopClick
        super(DailyAndBonusQuestView, self)._subscribe()

    def _unsubscribe(self):
        self.viewModel.dailyQuestModel.onGetBonusClick -= self.__onDailyBonusClick
        self.viewModel.bonusQuestModel.onGoToTasks -= self.__onGoToQuestsClick
        self.viewModel.shopCardModel.onGoToShop -= self.__onGoToShopClick
        super(DailyAndBonusQuestView, self)._unsubscribe()

    def _fillViewModel(self):
        super(DailyAndBonusQuestView, self)._fillViewModel()
        phase = self._hwController.phases.getActivePhase(PhaseType.REGULAR)
        if not phase:
            return
        with self.viewModel.transaction() as model:
            self.__fillDaily(phase, model.dailyQuestModel)
            self.__fillBonus(phase, model.bonusQuestModel)
            self.__fillShop(phase, model.shopCardModel)

    @decorators.adisp_process('updating')
    def __applyDailyBonus(self):
        phaseIndex = self._hwController.phases.getActivePhaseIndex(PhaseType.REGULAR)
        if phaseIndex == 0:
            return
        yield HWApplyDailyBonusProcessor(phaseIndex).request()

    def __onDailyBonusClick(self):
        self.__applyDailyBonus()

    def __onGoToShopClick(self):
        showHalloweenShop()
        self.destroyWindow()

    def __onGoToQuestsClick(self):
        phaseIndex = self._hwController.phases.getActivePhaseIndex(PhaseType.REGULAR)
        if phaseIndex == 0:
            return
        groupId = HALLOWEEN_GROUP_PHASES_PREFIX + ':' + HALLOWEEN_GROUP_PHASES_SUFFIX.format(index=phaseIndex)
        showMissions(groupID=groupId)
        self.destroyWindow()

    def __getIconFromBonus(self, bonus):
        if type(bonus) is not ItemsBonus:
            return ''
        equipment, _ = bonus.getItems().items()[0]
        icon, _, _ = equipment.descriptor.icon
        return icon

    def __fillDaily(self, phase, model):
        data = phase.getAbilityInfo(dailyQuest=True)
        if not data:
            return
        equipment, count, missionData = data
        timeToDayEnd = max(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay(), 0)
        model.setNumberOfBoostersAward(count)
        deltaTime = time_utils.getTimeDeltaFromNowInLocal(missionData.event.getFinishTime())
        model.setTimeInSeconds(min(timeToDayEnd, deltaTime))
        model.setIsBonusGot(missionData.event.isCompleted())
        model.setAbilityName(equipment.descriptor.name)
        model.setAbilityIcon(equipment.descriptor.iconName)
        currentTime = getDateTimeInUTC(time_utils.getCurrentTimestamp())
        finishTime = getDateTimeInUTC(missionData.event.getFinishTimeRaw() - _QUEST_FINISH_TIME_CORRECTION)
        lastPhase = phase.phaseIndex == len(self._hwController.phases.getPhasesByType(PhaseType.REGULAR))
        lastQuest = lastPhase and missionData.event.isCompleted() and currentTime.day == finishTime.day
        model.setIsShown(not lastQuest)

    def __fillBonus(self, phase, model):
        data = phase.getAbilityInfo(dailyQuest=False)
        if not data:
            return
        equipment, count, missionData = data
        model.setStartDate(missionData.event.getStartTime())
        model.setEndDate(missionData.event.getFinishTime())
        model.setNumberOfBoostersAward(count)
        model.setTimesCompleted(missionData.event.getBonusCount())
        model.setAbilityName(equipment.descriptor.name)
        model.setAbilityIcon(equipment.descriptor.iconName)

    def __fillShop(self, phase, model):
        hangarSettings = self._getConfig().hangarSettings
        model.setStartingPrice(hangarSettings['shop20MinPrice'])
        data = phase.getAbilityInfo(dailyQuest=False)
        if not data:
            return
        equipment, _, _ = data
        model.setShopIcon(equipment.descriptor.iconName)


class DailyAndBonusQuestWindow(LobbyWindow):

    def __init__(self, layoutID):
        super(DailyAndBonusQuestWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=DailyAndBonusQuestView(layoutID=layoutID))
        self._blur = CachedBlur(enabled=True, ownLayer=WindowLayer.TOP_SUB_VIEW)

    def _finalize(self):
        self._blur.fini()
        super(DailyAndBonusQuestWindow, self)._finalize()
