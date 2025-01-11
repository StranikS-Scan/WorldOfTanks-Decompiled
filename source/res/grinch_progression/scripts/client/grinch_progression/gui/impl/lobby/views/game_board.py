# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/game_board.py
from functools import partial
import logging
from grinch.gui.grinch_gui_constants import ABILITY_PANEL_COMMANDS_START
from grinch.overrides.hangar_override import showHangar
from grinch.skeletons.battle_controller import IGrinchController
from grinch_progression.account_helpers.account_settings import getCompletedQuests, setCompletedQuests, getCurrentVehicle, setCurrentVehicle
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.ability_model import AbilityModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.chapter_model import ChapterModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import RewardState, HintState
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.game_board_view_model import GameBoardViewModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.rewards_model import RewardsModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.tank_card_model import TankCardModel, VehicleStates
from grinch_progression.gui.impl.lobby.tooltips.ability_tooltip_view import AbilityTooltipView
from grinch_progression.gui.impl.lobby.tooltips.chapter_info_tooltip_view import ChaptersTooltipView
from grinch_progression.gui.impl.lobby.views.bonus_packer import updateRewardBonuses
from grinch_progression.gui.impl.lobby.views.quests_helper import VehicleRoleStr, vehicleRoleStrToModel, getDailyModifiersQuest, getWeekendQuests, getSpecialQuestQuests
from grinch_progression.gui.impl.lobby.views.quests_packer import getGrinchUIDataPacker
from grinch_progression.gui.impl.sounds import GAME_BOARD_SOUND_SPACE, GrinchProgressionSound
from grinch_progression.gui.shared.event_dispatcher import showGameBoardProgressionInfoView, showIntoVideoWindow
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
import CGF
import SoundGroups
import adisp
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from cgf_components.hangar_camera_manager import HangarCameraManager
from frameworks.wulf import ViewFlags, ViewSettings
from grinch_progression.gui.impl.lobby.views.hints_helper import HintsHelper, BATTLE_BTN_HINT_ID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showStylePreview
from gui.shared import g_eventBus, events
from gui.shared.gui_items.customization.c11n_items import Style
from gui.shared.utils.key_mapping import getReadableKey
from gui.shared.utils.scheduled_notifications import SimpleNotifier, Notifiable
from helpers import dependency, time_utils
from new_year.ny_preview import getVehiclePreviewID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import nextTick
_logger = logging.getLogger(__name__)
_TANK_NAME_TO_VEH_ROLE = {'Ch48_BZ_75_grinch': VehicleRoleStr.ASSAULT,
 'F88_AMX_13_105_grinch': VehicleRoleStr.CARRIER,
 'G89_Leopard1_grinch': VehicleRoleStr.SUPPORT}

def getTankRoleStr(vehicleName):
    return _TANK_NAME_TO_VEH_ROLE.get(vehicleName, VehicleRoleStr.CARRIER)


_AMMO_START_IDX = 0
_AMMO_COUNT = 1
_EQUIPMENT_START_IDX = _AMMO_START_IDX + _AMMO_COUNT
_EQUIPMENT_COUNT = 3
_TOTAL_PANEL_SLOTS = _AMMO_COUNT + _EQUIPMENT_COUNT
_INVALID_STEP_ID = -1

class GameBoardView(ViewImpl, LobbyHeaderVisibility, Notifiable):
    _COMMON_SOUND_SPACE = GAME_BOARD_SOUND_SPACE
    __gpController = dependency.descriptor(IGrinchProgressionController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, layoutID=R.views.grinch_progression.lobby.GameBoard(), *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = GameBoardViewModel()
        super(GameBoardView, self).__init__(settings)
        self.__curChapterId = -1
        self.__hintHelper = HintsHelper()
        self.__isMovingToInfo = False
        ClientSelectableCameraObject.deselectAll()

    @property
    def viewModel(self):
        return super(GameBoardView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.grinch_progression.lobby.tooltips.AbilityTooltipView():
            intCD = event.getArgument('intCD')
            keyString = event.getArgument('keyString')
            return AbilityTooltipView(int(intCD), keyString)
        return ChaptersTooltipView() if contentID == R.views.grinch_progression.lobby.tooltips.ChaptersInfoTooltipView() else super(GameBoardView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return super(GameBoardView, self)._getEvents() + ((self.viewModel.onNextStep, self.__onNextStep),
         (self.viewModel.onSwitchChapter, self.__onSwitchChapter),
         (self.viewModel.onUpdateContentModel, self.__updateContentModel),
         (self.viewModel.onChangeTank, self.__onChangeTank),
         (self.viewModel.onShowGameBoardInfo, self.__onShowGameBoardInfo),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenStylePreview, self.__onOpenStylePreview),
         (self.viewModel.onCompletedMissionShown, self.__onCompletedMissionShown),
         (self.viewModel.onHintViewed, self.__onHintViewed),
         (self.__settingsCore.onOnceOnlyHintsChanged, self.__onOnceOnlyHintsChanged),
         (self.__eventsCache.onSyncCompleted, self.__update),
         (g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.__gpController.onDataUpdated, self.__onDataUpdated))

    def _onLoading(self, *args, **kwargs):
        super(GameBoardView, self)._onLoading(*args, **kwargs)
        if self.__gpController.getIsFirstEntry():
            showIntoVideoWindow()
            self.__gpController.setIsFirstEntry(False)
        g_currentPreviewVehicle.selectNoVehicle()
        self.__selectVehicle()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.startNotification()
        self.__update()

    def _onLoaded(self, *args, **kwargs):
        super(GameBoardView, self)._onLoaded(*args, **kwargs)
        self.__onViewLoaded()
        self.suspendLobbyHeader(self.uniqueID)

    def _subscribe(self):
        super(GameBoardView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onVehicleLockUpdated})

    def _unsubscribe(self):
        super(GameBoardView, self)._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _finalize(self):
        if not self.__isMovingToInfo:
            nextTick(partial(self.__hintHelper.setFightButtonFlag, False))()
        self.__hintHelper.clear()
        self.resumeLobbyHeader(self.uniqueID)
        if self.__hangarSpace.spaceID:
            cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
            if cameraManager is not None:
                cameraManager.switchToTank()
        super(GameBoardView, self)._finalize()
        return

    def __update(self):
        curChapterID, _ = self.__gpController.getCurrentChapterStep()
        currentPounts = self.__gpController.getPoints()
        prevPounts = self.__gpController.getPreviousPointsCount()
        with self.viewModel.transaction() as model:
            self.__updateChapters(model)
            self.__updateHeader(curChapterID)
            self.__updateCurrentChapter(curChapterID, model=model)
            model.setPoints(currentPounts)
            model.setPrevPoints(prevPounts)
            self.__updateCurrentStep(curChapterID)
            if g_currentVehicle.intCD:
                model.setSelectedVehicleIntCD(g_currentVehicle.intCD)
            model.setMaxStep(self.__gpController.getMaxChapterStep())
            self.__updateMissions(model)
            self.__updateRewards(model, curChapterID)
            self.__updateTanksCards(model)
            self.__updateHint(model=model)
            self.__updateIsLastDay(model)
        if prevPounts != currentPounts:
            self.__gpController.setPreviousPointsCount(currentPounts)

    def __updateCurrentStep(self, viewChapterId):
        if self.__curChapterId == viewChapterId:
            return
        curChapterID, stepID = self.__gpController.getCurrentChapterStep()
        if viewChapterId != curChapterID:
            self.viewModel.setCurrentStep(_INVALID_STEP_ID)
        else:
            self.viewModel.setCurrentStep(stepID)
        self.__curChapterId = viewChapterId

    def __updateChapters(self, model=None):
        chaptersModel = model.getChapters()
        chaptersModel.clear()
        curChapterID, curStepID = self.__gpController.getCurrentChapterStep()
        maxStep = self.__gpController.getMaxChapterStep()
        for chapterId in self.__gpController.getCurrentSeasonChapters().iterkeys():
            chapterModel = ChapterModel()
            chapterModel.setChapterId(chapterId)
            isLastStep = curChapterID == chapterId and curStepID == maxStep
            chapterModel.setIsCompleted(curChapterID > chapterId or isLastStep)
            chaptersModel.addViewModel(chapterModel)

        chaptersModel.invalidate()

    @replaceNoneKwargsModel
    def __updateCurrentChapter(self, chapterId, model=None):
        model.setCurrentChapter(chapterId)

    def __updateContentModel(self):
        chapterId = self.viewModel.getCurrentChapter()
        with self.viewModel.transaction() as model:
            self.__updateHeader(chapterId)
            self.__updateCurrentStep(chapterId)
            self.__updateRewards(model, chapterId)
            model.setIsTabSwitching(False)

    def __getTimer(self):
        timeLeft = self.__grinchCtrl.getClosestStateChangeTime() - time_utils.getCurrentLocalServerTimestamp()
        return timeLeft + 1 if timeLeft > 0 else 0

    def __timerUpdate(self):
        self.__updateHeader()

    def __updateHeader(self, chapterID=None):
        chapterId = chapterID or self.viewModel.getCurrentChapter()
        now = time_utils.getCurrentLocalServerTimestamp()
        chapterSeason = self.__getSeasonByChapterID(chapterId)
        if not chapterSeason:
            _logger.warning('chapterSeason empty')
            return
        lastActiveSeason = self.__grinchCtrl.getCurrentSeason() or self.__grinchCtrl.getPreviousSeason()
        if not lastActiveSeason:
            _logger.warning('lastActiveSeason empty')
            return
        with self.viewModel.transaction() as model:
            if now < chapterSeason.getStartDate():
                model.setChapterStartDate(chapterSeason.getStartDate())
                model.setChapterFinishDate(chapterSeason.getEndDate())
            elif lastActiveSeason:
                model.setChapterStartDate(lastActiveSeason.getStartDate())
                model.setChapterFinishDate(lastActiveSeason.getEndDate())

    def __updateIsLastDay(self, model):
        now = time_utils.getServerUTCTime()
        endDate = self.__gpController.getEndEventDate()
        isLastDay = endDate - now <= time_utils.ONE_DAY
        model.setIsLastDay(isLastDay)

    def __updateTanksCards(self, model):
        tankCardsModel = model.getTankCards()
        tankCardsModel.clear()
        for intCD in self.__gpController.getGrinchVehicles():
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            vehicleName = vehicle.name.split(':')[1]
            tankCardModel = TankCardModel()
            tankCardModel.setIntCD(intCD)
            tankCardModel.setResourceKey(vehicleName)
            tankCardModel.setVehicleState(self.__getVehicleState(vehicle))
            tankCardModel.setBonusPoints(self.__getModiferValue(vehicle))
            roleStr = getTankRoleStr(vehicleName)
            tankCardModel.setRole(vehicleRoleStrToModel(roleStr))
            abilitiesModel = tankCardModel.getAbilities()
            abilitiesModel.clear()
            abilitiesModel.addViewModel(self.__getGunAbilityModel(vehicle, _AMMO_START_IDX))
            for index, eqId in enumerate(vehicle.getBuiltInEquipmentIDs()):
                abilitiesModel.addViewModel(self.__getEquipmentAbilityModel(eqId, index + 1))

            tankCardsModel.addViewModel(tankCardModel)
            abilitiesModel.invalidate()

        tankCardsModel.invalidate()

    def __getVehicleState(self, vehicle):
        if vehicle.isInBattle:
            return VehicleStates.INBATTLE
        return VehicleStates.INPLATOON if vehicle.isInUnit else VehicleStates.DEFAULT

    def __getGunAbilityModel(self, vehicle, index):
        abilityModel = AbilityModel()
        abilityModel.setResourceKey(vehicle.gun.descriptor.shots[0].shell.name)
        abilityModel.setIntCD(vehicle.gun.intCD)
        abilityModel.setKeyString(self.__getKeyString(index))
        return abilityModel

    def __getEquipmentAbilityModel(self, eqId, index):
        abilityModel = AbilityModel()
        equipment = self.__itemsCache.items.getItemByCD(eqId)
        abilityModel.setResourceKey(equipment.name)
        abilityModel.setIntCD(eqId)
        abilityModel.setKeyString(self.__getKeyString(index))
        return abilityModel

    def __updateMissions(self, model):
        missionsModel = model.getMissions()
        missionsModel.clear()
        if not g_currentVehicle.intCD:
            return
        quests = []
        quests.extend(getWeekendQuests(role=VehicleRoleStr.ASSAULT))
        quests.extend(getWeekendQuests(role=VehicleRoleStr.CARRIER))
        quests.extend(getWeekendQuests(role=VehicleRoleStr.SUPPORT))
        quests.extend(getSpecialQuestQuests())
        completedQuests = getCompletedQuests()
        for quest in quests:
            seenQuestID = quest.getID()
            missionCompletedVisited = seenQuestID in completedQuests
            if quest.isCompleted():
                if missionCompletedVisited:
                    continue
                else:
                    completedQuests.add(seenQuestID)
            mModel = getGrinchUIDataPacker(quest).pack()
            missionsModel.addViewModel(mModel)

        missionsModel.invalidate()

    def __updateRewards(self, model, viewChapterId, nextStep=None):
        curChapterID, step = self.__gpController.getCurrentChapterStep()
        curStepID = nextStep or step
        remainingPoints = self.__gpController.getPoints()
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        for chapterId, chapterValue in self.__gpController.getCurrentSeasonChapters().iteritems():
            if chapterId != viewChapterId:
                continue
            steps = chapterValue['steps']
            for stepId, stepValue in sorted(steps.items()):
                bonusDict = stepValue['bonus']
                rewardModel = RewardsModel()
                rewardModel.setStep(stepId)
                rewardModel.setPrice(stepValue['price'])
                rewardModel.setChapter(chapterId)
                updateRewardBonuses(bonusDict, rewardModel)
                if chapterId < curChapterID or chapterId == curChapterID and stepId <= curStepID:
                    rewardModel.setState(RewardState.CLAIMED)
                elif remainingPoints >= stepValue['price'] and chapterId == curChapterID:
                    rewardModel.setState(RewardState.AVAILABLE)
                    remainingPoints -= stepValue['price']
                else:
                    rewardModel.setState(RewardState.NOTAVAILABLE)
                    remainingPoints = 0
                rewardsModel.addViewModel(rewardModel)

        rewardsModel.invalidate()

    @replaceNoneKwargsModel
    def __updateHint(self, model=None):
        self.__hintHelper.updateState()
        hintState = self.__hintHelper.hintState
        model.setHintState(hintState)
        model.setIsHintVisible(self.__hintHelper.isHintVisible)
        self.__hintHelper.setFightButtonFlag(True)

    def __onClose(self):
        self.__grinchCtrl.selectRandomMode()
        self.__hintHelper.setFightButtonFlag(False)

    def __onSwitchChapter(self, args):
        chapterId = int(args.get('chapterId'))
        self.__updateCurrentChapter(chapterId)
        self.viewModel.setIsTabSwitching(True)

    @adisp.adisp_process
    def __onNextStep(self):
        result = yield self.__gpController.moveToNextStep()
        if not result.success:
            return
        SoundGroups.g_instance.playSound2D(GrinchProgressionSound.TANK_MOVE)
        with self.viewModel.transaction() as model:
            curChapterID, stepID = self.__gpController.getCurrentChapterStep()
            model.setCurrentStep(stepID)
            self.__updateCurrentChapter(curChapterID)
            self.__updateRewards(model, curChapterID, stepID)
            self.__updateHeader()

    def __onChangeTank(self, args):
        intCD = args.get('intCD')
        if intCD:
            self.__selectVehicle(int(intCD))
            self.__updateMissions(self.viewModel)

    def __onShowGameBoardInfo(self):
        self.__isMovingToInfo = True
        showGameBoardProgressionInfoView()

    def __onVehicleChanged(self):
        if g_currentVehicle.intCD:
            with self.viewModel.transaction() as model:
                model.setSelectedVehicleIntCD(g_currentVehicle.intCD)

    def __getKeyString(self, idx):
        if _AMMO_START_IDX <= idx < _EQUIPMENT_START_IDX:
            _logger.debug('[GameBoardView] Index is of an ammo slot, ammo slots should not have keybindings.')
            return ''
        relativeEquipmentIndex = idx - _EQUIPMENT_START_IDX
        command = ABILITY_PANEL_COMMANDS_START + relativeEquipmentIndex
        return getReadableKey(command)

    def __getModiferValue(self, vehicle):
        for quest in getDailyModifiersQuest():
            if quest.vehicleReqs.isAvailable(vehicle) and not quest.isCompleted():
                return quest.getRawBonuses().get('tokens', {}).get(self.__gpController.token, {}).get('count', 0)

    def __selectVehicle(self, intCD=None):
        if not intCD:
            intCD = getCurrentVehicle()
        if not intCD:
            intCD = self.__gpController.getGrinchVehicles()[0]
        g_currentVehicle.selectVehicleByCD(intCD)
        setCurrentVehicle(intCD)

    def __onOpenStylePreview(self, args):
        styleIntCD = int(args.get('styleId'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None or not isinstance(styleItem, Style):
            return
        else:
            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=showHangar)
            return

    def __onVehicleLockUpdated(self, _):
        with self.viewModel.transaction() as model:
            self.__updateTanksCards(model)

    def __onDataUpdated(self):
        self.__update()

    def __onCompletedMissionShown(self, args):
        seenQuestID = args.get('questId')
        completedQuests = getCompletedQuests()
        completedQuests.add(seenQuestID)
        setCompletedQuests(completedQuests)
        self.__updateMissions(self.viewModel)

    def __onOnceOnlyHintsChanged(self, diff):
        if BATTLE_BTN_HINT_ID not in diff.keys():
            return
        if diff[BATTLE_BTN_HINT_ID]:
            self.__onHintViewed({'hintId': HintState.BATTLE.value})

    def __onHintViewed(self, args):
        hintId = args.get('hintId')
        self.__hintHelper.hideHint(hintId)
        self.__updateHint()

    def __getSeasonByChapterID(self, chupterID):
        for season in self.__grinchCtrl.getAllSeasons():
            if season.getNumber() == chupterID:
                return season

        return None

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))
