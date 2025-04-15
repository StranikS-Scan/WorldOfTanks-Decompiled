# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_lobby_view/cosmic_lobby_view.py
import logging
from time import time
import typing
from cosmic_event.gui.battle_results import CosmicBattleResultEvent
from cosmic_event_common.cosmic_event_common import ScoreEvents
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers.CallbackDelayer import CallbackDelayer
from Event import Event
from adisp import adisp_process
from cosmic_account_settings import setLastVisitedProgressionLevel, getLastVisitedProgressionLevel, setLastSelectedVehicleID, getLastSelectedVehicleID
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import CosmicLobbyViewModel, LobbyRouteEnum
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.rules_entry_point_tooltip_model import RulesEntryPointTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.specification_tooltip_model import SpecificationTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_selector_tooltip_model import VehicleSelectorTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.cosmic_simple_tooltip_model import CosmicSimpleTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_ability_tooltip_model import VehicleAbilityTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_shell_tooltip_model import VehicleShellTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.progression_entry_point_tooltip_model import ProgressionEntryPointTooltipModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringTypeEnum
from cosmic_event.gui.impl.lobby.quest_helpers import fillDailyQuestModel, getDailyQuestModelFromQuest
from cosmic_event.gui.impl.lobby.quest_packer import DailyCosmicQuestUIDataPacker, getCosmicBonusPacker
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from cosmic_sound import CosmicHangarSounds
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, ViewStatus
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl import backport
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.event_dispatcher import showBrowserOverlayView, showShop
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getCosmic2024ShopUrl
from helpers import dependency, time_utils
from skeletons.gui.impl import INotificationWindowController, IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import RoverEnum
from frameworks.wulf import Array
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.rovers_model import RoversModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.medal_model import MedalModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.parameters_model import ParametersModel, ParameterEnum
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import AbilityModel
from cosmic_event.gui.gui_constants import ABILITY_TYPE_BY_EQUIP_NAME
from cosmic_event.cosmic_constants import OLD_VEHICLE_NAME
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import Ability
import items
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.server_events.bonuses import DossierBonus
from gui.shared.missions.packers.bonus import DossierBonusUIPacker
if typing.TYPE_CHECKING:
    from collections import OrderedDict
    from typing import Tuple, Sequence, Callable, Optional, List
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.event_items import Quest
    from cosmic_event.gui.game_control.battle_controller import CosmicEventBattleController
    from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.progression_model import ProgressionModel
    from gui.shared.missions.packers.bonus import BonusUIPacker
_logger = logging.getLogger(__name__)
_SCORE_EVENTS_TO_MODEL_ENUM = {ScoreEvents.ARTIFACT_SCAN: ScoringTypeEnum.SCAN,
 ScoreEvents.KILL: ScoringTypeEnum.KILL,
 ScoreEvents.PICKUP: ScoringTypeEnum.PICKUP,
 ScoreEvents.RAMMING: ScoringTypeEnum.RAM,
 ScoreEvents.SHOT: ScoringTypeEnum.SHOT,
 ScoreEvents.ABILITY_HIT: ScoringTypeEnum.ABILITYHIT,
 ScoreEvents.ASSIST: ScoringTypeEnum.ASSIST,
 ScoreEvents.FIRST_BLOOD: ScoringTypeEnum.FIRSTBLOOD,
 ScoreEvents.KILL_STREAK: ScoringTypeEnum.KILLSTREAK,
 ScoreEvents.PICKUP_MASTER: ScoringTypeEnum.PICKUPMASTER,
 ScoreEvents.REVENGE: ScoringTypeEnum.REVENGE,
 ScoreEvents.BOOST_ME: ScoringTypeEnum.BOOSTME}
_SCORE_EVENTS_TO_ORDERED_LIST = [ScoreEvents.FIRST_BLOOD,
 ScoreEvents.PICKUP_MASTER,
 ScoreEvents.KILL,
 ScoreEvents.REVENGE,
 ScoreEvents.KILL_STREAK,
 ScoreEvents.ASSIST,
 ScoreEvents.ARTIFACT_SCAN,
 ScoreEvents.PICKUP,
 ScoreEvents.RAMMING,
 ScoreEvents.SHOT,
 ScoreEvents.ABILITY_HIT,
 ScoreEvents.BOOST_ME]
COSMIC_SOUND_SPACE = CommonSoundSpaceSettings(name='hangar', entranceStates={'STATE_hangar_place': 'STATE_hangar_place_garage'}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
_VEHICLE_PARAMETERS = {'czech:Cz00_COSM_Gravizapa': {ParameterEnum.STABILITY: 24,
                               ParameterEnum.ACCELERATION: 24,
                               ParameterEnum.MAX_SPEED: 24,
                               ParameterEnum.FIRE_RATE: 18,
                               ParameterEnum.SHOT_POWER: 30},
 'czech:Cz00_COSM_Pepelac': {ParameterEnum.STABILITY: 18,
                             ParameterEnum.ACCELERATION: 30,
                             ParameterEnum.MAX_SPEED: 30,
                             ParameterEnum.FIRE_RATE: 24,
                             ParameterEnum.SHOT_POWER: 18}}

def _getScoreEventTypeEnum(eventName):
    return _SCORE_EVENTS_TO_MODEL_ENUM[ScoreEvents[eventName]]


def _getScoreEventListOrder(eventName):
    return _SCORE_EVENTS_TO_ORDERED_LIST.index(ScoreEvents[eventName])


class CosmicLobbyView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__tooltipData', '__currentRoute', '__callbackDelayer', '_previouslySeenPoints', '_postBattleOpenedAfterBattle', '_soundProgressionObject', '__selectedVehicleID', '__availableVehicleIDs', '__vehicles', '__isProgressionAmbientPlaying')
    _cosmicController = dependency.descriptor(ICosmicEventBattleController)
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _uiLoader = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = COSMIC_SOUND_SPACE
    _STR_VEH_TOOLTIP = R.strings.cosmicEvent.vehicle.tooltip
    _IMG_VEH_TOOLTIP = R.images.cosmic_event.gui.maps.icons.vehicleSelect.roverIcons.gold.dyn('c_64x64')
    _STR_ABILITY_TOOLTIP = R.strings.artefacts.cosmic.ability.tooltip
    _IMG_ABILITY_TOOLTIP = R.images.cosmic_event.gui.maps.icons.battle.ability_panel.size_135x135

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CosmicLobbyViewModel()
        super(CosmicLobbyView, self).__init__(settings)
        self.__tooltipData = {}
        self.__currentRoute = self._cosmicController.getLobbyRoute()
        self.__callbackDelayer = CallbackDelayer()
        self._previouslySeenPoints = 0
        self._postBattleOpenedAfterBattle = False
        self._soundProgressionObject = None
        self.__selectedVehicleID = 1
        self.__availableVehicleIDs = set([ x.value for x in RoverEnum ])
        self.__vehicles = {}
        self.__isProgressionAmbientPlaying = False
        g_eventBus.addListener(CosmicBattleResultEvent.POST_BATTLE_SCREEN_OPENING, self._postBattleOpening, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @property
    def viewModel(self):
        return super(CosmicLobbyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CosmicLobbyView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            return data

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.cosmic_event.lobby.tooltips.DailyQuestsTooltip():
            missionId = event.getArgument('missionId')
            quests = self._cosmicProgression.getDailyQuests()
            quest = quests.get(missionId, None)
            if quest is None:
                return
            self._cosmicProgression.setQuestProgressAsViewed(quest)
            questUIPacker = DailyCosmicQuestUIDataPacker(quest)
            model = questUIPacker.pack()
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.DailyQuestsTooltip(), model=model))
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            lootBox = self.__getLootBoxByEvent(event)
            if lootBox:
                return LootboxTooltip(lootBox)
        if contentID == R.views.cosmic_event.lobby.tooltips.RulesEntryPointTooltip():
            model = RulesEntryPointTooltipModel()
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.RulesEntryPointTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.SpecificationTooltip():
            parameterName = event.getArgument('parameterName')
            model = SpecificationTooltipModel()
            self.__fillSpecificationTooltipModel(parameterName, model)
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.SpecificationTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.VehicleSelectorTooltip():
            vehicleId = int(event.getArgument('vehicleId'))
            model = VehicleSelectorTooltipModel()
            self.__fillVehicleSelectorTooltipModel(vehicleId, model)
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.VehicleSelectorTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.VehicleAbilityTooltip():
            ability = event.getArgument('ability')
            model = VehicleAbilityTooltipModel()
            self.__fillEquipmentTooltipModel(ability, model)
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.VehicleAbilityTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.VehicleShellTooltip():
            model = VehicleShellTooltipModel()
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.VehicleShellTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.CosmicSimpleTooltip():
            model = CosmicSimpleTooltipModel()
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.CosmicSimpleTooltip(), model=model))
        elif contentID == R.views.cosmic_event.lobby.tooltips.ProgressionEntryPointTooltip():
            model = ProgressionEntryPointTooltipModel()
            self.__fillProgressionEntryPointTooltipModel(model)
            return ViewImpl(ViewSettings(R.views.cosmic_event.lobby.tooltips.ProgressionEntryPointTooltip(), model=model))
        else:
            return super(CosmicLobbyView, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self, *args, **kwargs):
        super(CosmicLobbyView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader()

    def __onViewStatusChanged(self, uniqueID, newStatus):
        view = self._uiLoader.windowsManager.getView(uniqueID)
        postBattleLayoutID = R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView()
        if view and view.layoutID == postBattleLayoutID and self._postBattleOpenedAfterBattle:
            if self.viewModel.getLobbyRoute() == LobbyRouteEnum.ARTEFACT:
                if newStatus == ViewStatus.LOADING:
                    with self.viewModel.transaction() as model:
                        points = self._cosmicProgression.getLastSeenPoints() - 1
                        model.setArtefactProgressDeltaFrom(points)
                newStatus == ViewStatus.DESTROYING and self._cosmicProgression.updateLastSeenPoints(self._previouslySeenPoints)
                self._fillModel()
                self._cosmicProgression.updateLastSeenPoints()
                self._postBattleOpenedAfterBattle = False

    def _getEvents(self):
        return ((self.viewModel.onLobbyRouteChange, self.onLobbyRouteChange),
         (self.viewModel.onClose, self.onClose),
         (self.viewModel.onAboutEvent, self.onAboutEvent),
         (self.viewModel.onShopClicked, self.onShopClicked),
         (self.viewModel.onVehicleChange, self.__onVehicleChange),
         (self._itemsCache.onSyncCompleted, self._onItemSyncCompleted),
         (self._cosmicProgression.onProgressPointsUpdated, self._fillModel),
         (self._cosmicController.onLobbyRouteChange, self.onLobbyRouteChangeImpl),
         (self._cosmicController.onVehicleSelected, self.__onVehicleSelected),
         (self._eventsCache.onSyncCompleted, self._onEventSyncCompleted),
         (self._uiLoader.windowsManager.onViewStatusChanged, self.__onViewStatusChanged))

    def _onLoading(self, *args, **kwargs):
        super(CosmicLobbyView, self)._onLoading(*args, **kwargs)
        self.__vehicles = {id:data for id, data in self._cosmicController.getEventVehicles()}
        self._setLastVisitedProgressionLevel()
        self.__selectVehicle(getLastSelectedVehicleID())
        self._fillModel(self.__currentRoute)

    def _onLoaded(self, *args, **kwargs):
        super(CosmicLobbyView, self)._onLoaded(*args, **kwargs)
        self._notificationMgr.releasePostponed()
        self.__playProgressionSound()

    def _fillModel(self, newRoute=None):
        with self.viewModel.transaction() as model:
            model.setLobbyRoute(newRoute or self.__currentRoute)
            currentPoints, currentStage, limitPoints = self._cosmicProgression.getProgression()
            lastVisitedLevel = getLastVisitedProgressionLevel()
            lastSeenPoints = self._cosmicProgression.getLastSeenPoints()
            model.setMarsPoints(min(currentPoints, limitPoints))
            model.setMarsPointsLimit(limitPoints)
            model.setCurrentProgressSectionIndex(currentStage)
            model.setArtefactProgressDeltaFrom(lastSeenPoints)
            model.setFadeOut(False)
            model.setIsSomethingHappeningWithArtefact(currentStage != lastVisitedLevel)
            model.setIsProgressionFinished(self._cosmicProgression.isProgressionFinished())
            if newRoute == LobbyRouteEnum.ARTEFACT:
                self._cosmicProgression.updateLastSeenPoints()
                self._previouslySeenPoints = lastSeenPoints
                self._fillScoreModel(model=model)
                self._fillProgression(model=model)
                self._setLastVisitedProgressionLevel()
                setLastVisitedProgressionLevel(currentStage)
                self.__setRTPCForProgression()
                self.__playProgressionAmbient()
            else:
                self.__stopProgressionAmbient()
            self._fillMissionsModel(model=model)
            self.__updateVehicleModel(model)
            self.__updateAllVehiclesModel(model)
            self._updateVehicleState(model=model)
            self.__fillMedals(model)

    def _setLastVisitedProgressionLevel(self):
        with self.viewModel.transaction() as model:
            lastVisitedLevel = getLastVisitedProgressionLevel()
            self._fillModelWithLastVisitedProgressionLevel(model, lastVisitedLevel)

    def _fillModelWithLastVisitedProgressionLevel(self, model, lastVisitedLevel):
        model.setLastVisitedProgressionLevel(lastVisitedLevel)

    def _fillProgression(self, model):
        packer = getCosmicBonusPacker()
        progression = self._cosmicProgression.getBonuses()
        progressionArray = model.getProgression()
        progressionArray.clear()
        progressionArray.reserve(len(progression))
        self.__tooltipData = {}
        for pointsCondition, bonuses in progression:
            progressionModel = model.getProgressionType()()
            progressionModel.setMarsPoints(pointsCondition)
            bonusArray = progressionModel.getBonuses()
            bonusArray.clear()
            bonusArray.reserve(len(bonuses))
            packBonusModelAndTooltipData(bonuses, bonusArray, self.__tooltipData, packer)
            bonusArray.invalidate()
            progressionArray.addViewModel(progressionModel)

        progressionArray.invalidate()

    def _fillScoreModel(self, model):
        scoresSystem = sorted(self._getScoreSystem(), key=lambda scoreEvent: _getScoreEventListOrder(scoreEvent[0]))
        scoreArray = model.getScoring()
        scoreArray.clear()
        scoreArray.reserve(len(scoresSystem))
        for event, data in scoresSystem:
            scoringModel = model.getScoringType()()
            eventType = _getScoreEventTypeEnum(event)
            scoringModel.setType(eventType)
            if eventType == ScoringTypeEnum.PICKUPMASTER:
                points = data.get('points', 0)
            elif eventType == ScoringTypeEnum.KILLSTREAK:
                points = [ int(d) for d in data.split() ][1]
            else:
                points = data
            scoringModel.setMarsPoints(points)
            scoreArray.addViewModel(scoringModel)

        scoreArray.invalidate()

    def _getScoreSystem(self):
        scoreSystem = self._cosmicController.getModeSettings().scoreSystem
        return scoreSystem.get('eventsConfig', {}).items()

    @replaceNoneKwargsModel
    def _fillMissionsModel(self, model=None):
        quests = self._cosmicProgression.collectSortedRelevantDailyQuests()
        missionsModel = model.getMissions()
        missionsModel.clear()
        missionsModel.reserve(len(quests))
        for quest in quests.values():
            dailyQuestModel = WidgetQuestModel()
            fullQuestModel = getDailyQuestModelFromQuest(quest)
            fillDailyQuestModel(dailyQuestModel, fullQuestModel)
            missionsModel.addViewModel(dailyQuestModel)
            fullQuestModel.unbind()

        missionsModel.invalidate()

    def _finalize(self):
        self.__stopProgressionAmbient()
        if self._soundProgressionObject and self._soundProgressionObject.isPlaying:
            self._soundProgressionObject.stop()
            self._soundProgressionObject = None
        self.resumeLobbyHeader()
        g_eventBus.removeListener(CosmicBattleResultEvent.POST_BATTLE_SCREEN_OPENING, self._postBattleOpening, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__callbackDelayer.clearCallbacks()
        self.__availableVehicleIDs.clear()
        self.__availableVehicleIDs = None
        self.__tooltipData = None
        self.__currentRoute = None
        self.__callbackDelayer = None
        self._previouslySeenPoints = None
        self._postBattleOpenedAfterBattle = None
        self.__selectedVehicleID = None
        self.__vehicles = None
        self.__isProgressionAmbientPlaying = None
        super(CosmicLobbyView, self)._finalize()
        return

    def onLobbyRouteChangeImpl(self, newRoute):
        self.__currentRoute = newRoute
        self._fillModel(self.__currentRoute)
        self._cosmicController.setLobbyRoute(self.__currentRoute)

    @args2params(str)
    def onLobbyRouteChange(self, newRoute):
        self.onLobbyRouteChangeImpl(LobbyRouteEnum(newRoute))

    def onClose(self):
        if not self.__callbackDelayer.hasDelayedCallback(self.closeLobby):
            self.viewModel.setFadeOut(True)
            self.__callbackDelayer.delayCallback(time_utils.ONE_SECOND, self.closeLobby)

    @adisp_process
    def closeLobby(self, *args, **kwargs):
        dispatcher = g_prbLoader.getDispatcher()
        result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if result:
            self._cosmicController.setLobbyRoute(LobbyRouteEnum.MAIN)
            self.destroyWindow()

    def onAboutEvent(self, *args, **kwargs):
        self._showInfoPage()

    @replaceNoneKwargsModel
    def _updateVehicleState(self, model=None):
        vehicle = self._cosmicController.getEventVehicle()
        with self.viewModel.transaction() as commonModel:
            self.__updateAllVehiclesModel(commonModel)
            model.setIsVehicleInBattle(vehicle.isInBattle)

    def _onItemSyncCompleted(self, *_):
        self._updateVehicleState()

    def _onEventSyncCompleted(self, *_):
        self._fillMissionsModel()
        self.__playProgressionSound()

    def _getInfoPageURL(self):
        return GUI_SETTINGS.cosmicInfoPageURL

    def _showInfoPage(self):
        url = self._getInfoPageURL()
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _postBattleOpening(self, *args, **kwargs):
        self._postBattleOpenedAfterBattle = True

    def onShopClicked(self):
        self.closeLobby()
        showShop(getCosmic2024ShopUrl())

    def __onVehicleChange(self, args):
        vehicleSelected = int(args.get('vehicleSelected', 0))
        if vehicleSelected and self.__selectedVehicleID != vehicleSelected:
            self.__selectVehicle(vehicleSelected)
            setLastSelectedVehicleID(vehicleSelected)

    def __playProgressionSound(self):
        currentStage = self._cosmicProgression.getCurrentStage()
        self._soundProgressionObject = CosmicHangarSounds.CosmicProgression.getSoundObject(currentStage)
        if self._soundProgressionObject:
            self._soundProgressionObject.play()
        else:
            _logger.error('Error on playing sound for cosmic progression for %r stage', currentStage)

    def __onVehicleSelected(self):
        g_eventBus.handleEvent(events.FightButtonEvent(events.FightButtonEvent.FIGHT_BUTTON_UPDATE), EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as model:
            self.__updateVehicleModel(model)

    def __selectVehicle(self, vehicleID):
        self.__selectedVehicleID = vehicleID
        self._cosmicController.selectVehicle(self.__selectedVehicleID)

    def __updateVehicleModel(self, model):
        resource = self._cosmicController.getResourceIconForSelectedVehicle()
        model.setSelectedVehicleResource(resource)
        if self.__selectedVehicleID in self.__availableVehicleIDs:
            model.setSelectedVehicle(RoverEnum(self.__selectedVehicleID))

    def __updateAllVehiclesModel(self, model):
        roversArray = model.getRovers()
        roversArray.clear()
        roversArray.reserve(len(self.__vehicles))
        for id, vehicle in self.__vehicles.iteritems():
            name = vehicle.get('name')
            vehCD = vehicle.get('vehCD')
            rover = RoversModel()
            rover.setVehicleName(name)
            rover.setVehicle(RoverEnum(id))
            vehicleItem = self._itemsCache.items.getItemByCD(vehCD)
            rover.setIsVehicleInBattle(vehicleItem.isInBattle)
            parametrsArray = Array()
            paramsDict = _VEHICLE_PARAMETERS[name]
            for param in ParameterEnum:
                parametr = ParametersModel()
                parametr.setValue(paramsDict[param])
                parametr.setParameterName(param)
                parametr.setIcon(backport.image(R.images.cosmic_event.gui.maps.icons.specifications.dyn(param.value)()))
                parametr.setParameterDesc(backport.text(R.strings.cosmicEvent.specifications.dyn(param.value).desc()))
                parametrsArray.addViewModel(parametr)

            rover.setParameters(parametrsArray)
            abilities = Array()
            abilityNames = vehicle.get('abilities')
            for abilityName in abilityNames:
                ability = AbilityModel()
                ability.setAbility(ABILITY_TYPE_BY_EQUIP_NAME[abilityName])
                abilities.addViewModel(ability)

            rover.setAbilities(abilities)
            roversArray.addViewModel(rover)

        roversArray.invalidate()

    def __fillMedals(self, model):
        achievements = self._cosmicController.getAchievements()
        medals = model.getMedals()
        medals.clear()
        medals.reserve(len(achievements))
        for achvievement in achievements:
            record = tuple(achvievement.split(':'))
            factory = getAchievementFactory(record, self._itemsCache.items.getAccountDossier())
            item = factory.create()
            bonus = DossierBonus('dossier', {1: {(record[0], record[1]): {'unique': True,
                                          'type': 'set',
                                          'value': 1}}})
            tooltipIndex = 0 if self.__tooltipData is None else len(self.__tooltipData)
            tooltipIdx = str(tooltipIndex)
            self.__tooltipData[tooltipIdx] = DossierBonusUIPacker().getToolTip(bonus)[0]
            medal = MedalModel()
            medal.setName(record[1])
            medal.setTooltipId(tooltipIdx)
            medal.setIsReceived(item.isInDossier())
            medals.addViewModel(medal)

        medals.invalidate()
        return

    def __fillProgressionEntryPointTooltipModel(self, model):
        currentPoints, currentStage, limitPoints = self._cosmicProgression.getProgression()
        model.setMarsPoints(currentPoints)
        model.setMarsPointsLimit(limitPoints)
        model.setCurrentProgressSectionIndex(currentStage)
        model.setIsProgressionFinished(self._cosmicProgression.isProgressionFinished())
        curTimeStamp = time()
        delta = 0
        curSeason = self._cosmicController.getCurrentSeason()
        if curSeason is not None:
            delta = curSeason.getEndDate() - curTimeStamp
        model.setSeasonEnd(max(delta, 0))
        lastVisitedLevel = getLastVisitedProgressionLevel()
        if currentStage != lastVisitedLevel:
            model.setIsSomethingHappeningWithArtefact(True)
        bonuses = self._cosmicProgression.getBonusesForCurrentStage()
        bonusArray = model.getBonuses()
        bonusArray.clear()
        bonusArray.reserve(len(bonuses))
        packer = getCosmicBonusPacker()
        packBonusModelAndTooltipData(bonuses, bonusArray, None, packer)
        bonusArray.invalidate()
        return

    def __fillSpecificationTooltipModel(self, parameterName, model):
        model.setTitle(backport.text(R.strings.cosmicEvent.specifications.dyn(parameterName).title()))
        model.setDescription(backport.text(R.strings.cosmicEvent.specifications.dyn(parameterName).desc()))
        model.setIcon(backport.image(R.images.cosmic_event.gui.maps.icons.specifications.tooltip.dyn(parameterName)()))

    def __fillVehicleSelectorTooltipModel(self, vehicleId, model):
        name = self.__vehicles.get(vehicleId, {}).get('name')
        if name:
            path = 'oldVehicle' if name == OLD_VEHICLE_NAME else 'newVehicle'
            model.setRoverName(backport.text(self._STR_VEH_TOOLTIP.dyn(path).title()))
            model.setShortDescription(backport.text(self._STR_VEH_TOOLTIP.dyn(path).shortDesc()))
            model.setLongDescription(backport.text(self._STR_VEH_TOOLTIP.dyn(path).longDesc()))
            model.setIcon(backport.image(self._IMG_VEH_TOOLTIP.dyn(path)()))

    def __fillEquipmentTooltipModel(self, ability, model):
        abilitiesByEnum = {data.value:key for key, data in ABILITY_TYPE_BY_EQUIP_NAME.iteritems()}
        abilityName = abilitiesByEnum.get(ability)
        if not abilityName:
            return
        abilityId = items.vehicles.g_cache.equipmentIDs()[abilityName]
        item = items.vehicles.g_cache.equipments()[abilityId]
        model.setAbilityName(backport.text(self._STR_ABILITY_TOOLTIP.dyn(ability).name()))
        if ability == Ability.STUN_SHOT.value:
            duration = item.stunDuration
        else:
            duration = item.duration
        model.setDescription(backport.text(self._STR_ABILITY_TOOLTIP.dyn(ability).descr(), time=int(duration)))
        model.setCooldown(int(item.cooldownSeconds))
        model.setIcon(backport.image(self._IMG_ABILITY_TOOLTIP.dyn(ability)()))

    def __getLootBoxByEvent(self, event):
        tooltipId = event.getArgument('tooltipId')
        lootBoxIdStr = self.__tooltipData.get(tooltipId)
        return self._itemsCache.items.tokens.getLootBoxByID(int(lootBoxIdStr)) if lootBoxIdStr else None

    def __setRTPCForProgression(self):
        curPoints = self._cosmicProgression.getCurrentPoints()
        soundMgr = self.soundManager
        soundMgr.setRTPC(CosmicHangarSounds.CosmicProgression.COSMIC_RTPC_PROGRESSION, self.__getRTPCValue(curPoints))

    def __getRTPCValue(self, curPoints):
        maxValue = 100.0
        step = 1000
        return min(float(curPoints / step), maxValue)

    def __playProgressionAmbient(self):
        if not self.__isProgressionAmbientPlaying:
            CosmicHangarSounds.CosmicProgression.playAmbient()
        self.__isProgressionAmbientPlaying = True

    def __stopProgressionAmbient(self):
        if self.__isProgressionAmbientPlaying:
            CosmicHangarSounds.CosmicProgression.stopAmbient()
        self.__isProgressionAmbientPlaying = False
