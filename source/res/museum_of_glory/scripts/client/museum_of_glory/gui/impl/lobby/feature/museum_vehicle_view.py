# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/impl/lobby/feature/museum_vehicle_view.py
import sys
import BigWorld
import CGF
import typing
import Math
from GenericComponents import TransformComponent
from WeakMethod import WeakMethodProxy
from cgf_components.hover_component import SelectionComponent
from debug_utils import LOG_ERROR
from gui.impl.gui_decorators import args2params
from items.type_traits import equalFloat
from messenger.proto.events import g_messengerEvents
from museum_of_glory.cgf.museum_components import MuseumTankBack, TankObjectSoundComponent
from museum_of_glory.cgf.museum_entry_manager import MuseumLobbyEntry
from museum_of_glory.gui.impl.base_transition_view import BaseTransitionView
from museum_of_glory.ui_logger.logger import MuseumLogger
from museum_of_glory_account_settings import getMuseumOfGlorySetting, setMuseumOfGlorySettings
from account_helpers.settings_core.settings_constants import SOUND
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from museum_of_glory.gui.impl.gen.view_models.views.lobby.feature.museum_vehicle_view_model import MuseumVehicleViewModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl import backport
from gui.impl.gen import R
from museum_of_glory.gui.impl.gen.view_models.views.lobby.feature.museum_vehicle_model import MuseumVehicleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.early_access.tooltips.early_access_currency_tooltip_view import EarlyAccessCurrencyTooltipView
from gui.impl.lobby.early_access.tooltips.early_access_state_tooltip import EarlyAccessStateTooltipView
from gui.shared import event_dispatcher
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHangarFeatureStateController, IHangarSpaceSwitchController
from skeletons.account_helpers.settings_core import ISettingsCore
from SoundGroups import g_instance as SoundGroups
from museum_of_glory.museum_of_glory_constants import CHARACTERISTIC_FIELDS, LAST_SEEN_INDEX, AUDIO_GUIDE_ENABLED, IS_INTRO_SEEN
from museum_of_glory.museum_of_glory_constants import MuseumOfGlorySoundEvents as Constants
from museum_of_glory.skeletons.game_control import IMuseumOfGloryController
from museum_of_glory.gui.impl.gen.view_models.views.lobby.feature.museum_vehicle_characteristics import MuseumVehicleCharacteristics, Characteristic
from skeletons.gui.shared.utils import IHangarSpace
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    import Event
    from frameworks.wulf import ViewEvent, View, Window
    from museum_of_glory.dto.vehicle import VehicleDto
MUSEUM_OF_GLORY_SCENE_NAME = 'MUSEUM_OF_GLORY'
VIEW_OPEN_TOKEN = 'museumOfGlory_viewOpen_2026'

class MuseumVehicleView(BaseTransitionView):
    __slots__ = ('__currentVehicleIndex', '__isAnimationFreeze', '__isAnimationPlaying', '__hasDelayedBalanceUpdates', '__vehicles', '__audioEnabled', '__currentYear', '__isExcursionPlaying', '__welcomeCallback', '__uiLogger', '__vehDtos', '__isConfigChanged', '__isExcursionPaused', '__selectedVehID', '__worldSoundPos', '__isSpaceLoaded')
    __museumOfGlory = dependency.descriptor(IMuseumOfGloryController)
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __hangarSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __appLoader = dependency.descriptor(IAppLoader)
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MuseumVehicleViewModel()
        super(MuseumVehicleView, self).__init__(settings)
        self.__uiLogger = MuseumLogger()
        self.__vehDtos = list()
        self.__worldSoundPos = Math.Vector3()
        self.__currentVehicleIndex = None
        self.__selectedVehID = None
        self.__isAnimationFreeze = False
        self.__isAnimationPlaying = False
        self.__hasDelayedBalanceUpdates = False
        self.__vehicles = {}
        self.__audioEnabled = False
        self.__currentYear = None
        self.__isExcursionPlaying = False
        self.__isExcursionPaused = False
        self.__welcomeCallback = None
        self.__isSpaceLoaded = False
        self.__isConfigChanged = False
        return

    @property
    def materialQueryItems(self):
        return (MuseumTankBack,)

    @property
    def viewModel(self):
        return super(MuseumVehicleView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MuseumVehicleView, self).createToolTip(event)

    def onFadeIn(self):
        if self.__selectedVehID is None:
            return
        else:
            self.__hangarFeatureStateController.cgfCameraManager.resetCameraTarget(duration=1)
            self.__changeVehicle()
            self.__selectedVehID = None
            return

    def onFadeOut(self):
        self.viewModel.setIsAllBlocked(False)

    def __updateBackground(self, prevYear, currentYear):
        if not prevYear or prevYear == currentYear:
            return
        prevImage = self.__museumOfGlory.getBackgroundImage(prevYear)
        curImage = self.__museumOfGlory.getBackgroundImage(currentYear)
        if prevImage and curImage:
            self.updateTextures(diffuseMap=prevImage, diffuseMap2=curImage)
            return
        LOG_ERROR('Failed to retrieve config image', prevYear, prevImage, currentYear, curImage)

    def getTooltipData(self, event):
        vehicleCD = event.getArgument('vehicleCD')
        data = createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE, specialArgs=[vehicleCD])
        return data

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCurrencyTooltipView():
            return EarlyAccessCurrencyTooltipView()
        return EarlyAccessStateTooltipView(event.getArgument('state')) if contentID == R.views.lobby.early_access.tooltips.EarlyAccessSimpleTooltipView() else super(MuseumVehicleView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        self.__vehDtos = self.__vehDtos or self.__museumOfGlory.getVehiclesDto()
        self.__logViewOpened()
        self.__loadSpace()
        g_messengerEvents.onNotificationsClear()
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)
        self.__toggleLayerVisibility(False)
        app = self.__appLoader.getApp()
        if app:
            app.setBackgroundAlpha(0.0)
        g_eventBus.handleEvent(events.LobbyInterfaceEvent(events.LobbyInterfaceEvent.TOGGLE_VISIBILITY, ctx={'visible': False,
         'messengerBarVisible': False}), EVENT_BUS_SCOPE.LOBBY)
        super(MuseumVehicleView, self)._initialize()

    def __toggleLayerVisibility(self, state):
        app = self.__appLoader.getApp()
        if app is None:
            LOG_ERROR('app loader is NONE')
            return
        else:
            layers = (WindowLayer.WINDOW, WindowLayer.TOP_WINDOW, WindowLayer.TOP_SUB_VIEW)
            if state:
                app.containerManager.showContainers(layers)
                return
            app.containerManager.hideContainers(layers)
            return

    def _finalize(self):
        self.__toggleLayerVisibility(True)
        super(MuseumVehicleView, self)._finalize()
        self.__hangarSpace.setSelectionEnabled(False)
        g_messengerEvents.onUnlockPopUpMessages()
        self.__stopIntro()
        self.__uiLogger.log()
        self.__unloadSpace()
        g_eventBus.handleEvent(events.LobbyInterfaceEvent(events.LobbyInterfaceEvent.TOGGLE_VISIBILITY, ctx={'visible': True,
         'messengerBarVisible': True}), EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        super(MuseumVehicleView, self)._onLoading(*args, **kwargs)
        SoundGroups.setState(Constants.STATE_PLACE, Constants.STATE_PLACE_GARAGE)
        self.__vehDtos = self.__vehDtos or self.__museumOfGlory.getVehiclesDto()
        SoundGroups.setState(Constants.EXCURSION_STATE, Constants.STATES.get(Constants.EXCURSION_STATE)[0])
        vehID = getMuseumOfGlorySetting(LAST_SEEN_INDEX)
        if vehID >= len(self.__vehDtos):
            vehID = 0
        self.__selectedVehID = vehID
        self.__onYearChanged(self.__museumOfGlory.getMinYear())
        self.__checkIsAudioEnabled()
        self.__updateModel(vehID)

    def _getEvents(self):
        return ((self.viewModel.onSelectVehicle, self.__onVehicleSelected),
         (self.viewModel.onBackToHangar, self.__onBackToHangar),
         (self.viewModel.onStartMoving, self.__onStartMoving),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onAudioCheckboxToggle, self.__onAudioCheckboxClicked),
         (self.viewModel.onExcursionPlay, self.__onExcursionPlay),
         (self.viewModel.onExcursionPause, self.__onExcursionPause),
         (self.__hangarSpace.onSpaceCreate, self.__onSpaceCreate),
         (self.__hangarSpace.onSpaceDestroy, self.__onSpaceDestroy),
         (self.__hangarSpace.onVehicleChanged, self.__onVehicleChanged),
         (self.viewModel.onVehiclePlayTimeLog, self.__onVehiclePlayTimeLog),
         (self.viewModel.onExcursionEnd, self.__onExcursionEnd),
         (self.__museumOfGlory.onConfigUpdate, self.__onConfigUpdate))

    def __loadSpace(self):
        self.__hangarSwitchController.onCheckSceneChange += self.__updateHangarScene
        self.__hangarSwitchController.customEventModeEnabled = True
        self.__hangarSwitchController.processPossibleSceneChange()
        self.__hangarSwitchController.onCheckSceneChange -= self.__updateHangarScene

    @noexcept
    def __unloadSpace(self, isReload=True):
        if not self.__isSpaceLoaded:
            return
        self.__isSpaceLoaded = False
        self.__hangarFeatureStateController.exit(self.layoutID)
        self.__hangarSwitchController.customEventModeEnabled = False
        if isReload:
            self.__hangarSwitchController.processPossibleSceneChange()

    def __updateHangarScene(self):
        self.__hangarSwitchController.hangarSpaceUpdate(MUSEUM_OF_GLORY_SCENE_NAME)

    def __onIntroEnds(self, _):
        self.__welcomeCallback = None
        self.viewModel.setIsIntroPlay(False)
        self.__playAudioGuide()
        return

    def __startIntro(self):
        setMuseumOfGlorySettings(IS_INTRO_SEEN, True)
        if self.isSoundDisabled() or not getMuseumOfGlorySetting(AUDIO_GUIDE_ENABLED):
            return
        else:
            self.__welcomeCallback = SoundGroups.WWgetSoundCallback(Constants.WELCOME_SOUND_EVENT, objectName=None, matrix=None, callback=self.__onIntroEnds)
            self.__welcomeCallback.play()
            return

    def __stopIntro(self):
        if self.__welcomeCallback is None:
            return
        else:
            self.__welcomeCallback.stop()
            self.__welcomeCallback = None
            return

    def __playAudioGuide(self):
        if self.__audioEnabled and not self.__isExcursionPlaying:
            self.__playVehSoundEvent(self.__vehDtos[self.__currentVehicleIndex])

    def isSoundDisabled(self):
        return not self.__settingsCore.getSetting(SOUND.MASTER_TOGGLE) or equalFloat(self.__settingsCore.getSetting(SOUND.MASTER), 0.0) or equalFloat(self.__settingsCore.getSetting(SOUND.VOICE_NOTIFICATION), 0.0)

    def __checkIsAudioEnabled(self):
        self.__audioEnabled = getMuseumOfGlorySetting(AUDIO_GUIDE_ENABLED)
        with self.viewModel.transaction() as vm:
            vm.setIsAudioEnabled(not self.isSoundDisabled())
            vm.setIsAudioChecked(self.__audioEnabled)
        self.__uiLogger.setVoiceoverEnabled(self.__audioEnabled)

    def __updateModel(self, vehID):
        with self.viewModel.transaction() as model:
            model.setCurrentVehicleIndex(vehID)
            model.setIsIntroPlay(True)
            self.__fillVehicles(model)
            model.setIsExcursionPlaying(self.__isExcursionPlaying)
            model.setIsExcursionPaused(self.__isExcursionPaused)

    def __fillVehicles(self, model):

        def fillYear():
            string = R.strings.museum_of_glory.vehicleInfo
            for item in self.__vehDtos:
                vehName = self.__makeBackportVehicleName(item.name)
                vehString = string.dyn(vehName)
                vModel = MuseumVehicleModel()
                fillVehicleModel(vModel, item.vehicle)
                vModel.setName(item.vehicle.descriptor.type.userString)
                vModel.setYear(item.year)
                vModel.setTime(item.voiceoverLength)
                vModel.setVehicleType(item.vehicle.type)
                vModel.setVehicleCD(item.intCD)
                vModel.setNation(item.vehicle.nationName)
                vModel.setHistoricalText(backport.text(vehString.description()))
                vehicleCharactModel = vModel.getCharacteristics()
                vehicleCharactModel.clear()
                self.__formatVehicleSpecs(item, vehicleCharactModel)
                vehicleModelArray.addViewModel(vModel)

        vehicleModelArray = model.getVehicles()
        vehicleModelArray.clear()
        fillYear()
        vehicleModelArray.invalidate()

    def __formatVehicleSpecs(self, item, model):
        for key in CHARACTERISTIC_FIELDS:
            val = item.descriptions.get(key)
            if val is not None:
                md = MuseumVehicleCharacteristics()
                md.setKey(Characteristic(key))
                md.setValue(val)
                model.addViewModel(md)

        model.invalidate()
        return

    def __onYearChanged(self, year):
        self.__currentYear = year

    @staticmethod
    def __makeBackportVehicleName(vehName):
        if ':' in vehName:
            vehName = vehName[vehName.index(':') + 1:]
        return vehName.replace('-', '_')

    def __playVehSoundEvent(self, vehicle):
        event = Constants.SOUND_EVENT_PREFIX + self.__makeBackportVehicleName(vehicle.name)
        SoundGroups.playSoundPos(event, self.__worldSoundPos)

    def __onVehicleSelected(self, event):
        index = int(event.get(MuseumVehicleViewModel.ARG_VEHICLE_INDEX, 0))
        self.viewModel.setIsIntroPlay(False)
        self.__stopIntro()
        self.__selectVehicle(index)
        if not self.__isExcursionPlaying or self.__isExcursionPaused:
            self.__uiLogger.increaseTankClickCount(self.__vehDtos[index].name)

    def __selectVehicle(self, newVehIdx):
        vehDto = self.__vehDtos[newVehIdx]
        if newVehIdx == self.__currentVehicleIndex:
            if self.__audioEnabled and self.__welcomeCallback is None:
                self.__playVehSoundEvent(vehDto)
            return
        else:
            self.viewModel.setIsAllBlocked(True)
            self.__selectedVehID = newVehIdx
            vehicleDto = self.__vehDtos[newVehIdx]
            self.__updateBackground(self.__currentYear, vehicleDto.year)
            self.fade(True)
            return

    def __changeVehicle(self):
        newVehIndex = self.__selectedVehID
        setMuseumOfGlorySettings(LAST_SEEN_INDEX, newVehIndex)
        vehicle = self.__vehDtos[newVehIndex]
        self.__currentVehicleIndex = newVehIndex
        self.viewModel.setCurrentVehicleIndex(newVehIndex)
        self.__onYearChanged(vehicle.year)
        state = self.__museumOfGlory.getEpochMusics(vehicle.year)
        SoundGroups.setState(Constants.DATES_STATE, state)
        outfit = self.__customizationService.getEmptyOutfitWithNationalEmblems(vehicle.strCD, isClanHidden=True, isMarksOnGunHidden=True)
        g_currentPreviewVehicle.selectVehicle(vehicle.intCD, vehicle.strCD, outfit=outfit)
        if self.__audioEnabled and self.__welcomeCallback is None:
            self.__playVehSoundEvent(vehicle)
        if not self.__isExcursionPlaying and not self.__isExcursionPaused and self.__welcomeCallback is None:
            SoundGroups.playSound2D(Constants.RESUME_SOUND_EVENT)
        return

    def __onBackToHangar(self):
        if self.__hangarSpace.spaceLoading():
            return
        self.destroyWindow()
        self.__unloadSpace()
        event_dispatcher.showHangar()

    def __onExcursionPlay(self, event):
        self.__isExcursionPlaying = event.get('isExcursionPlaying')
        if not self.__isExcursionPlaying:
            self.__isExcursionPaused = False
        if not self.__audioEnabled:
            SoundGroups.playSound2D(Constants.EXCURSION_MUTE)
            self.__playVehSoundEvent(self.__vehDtos[self.__currentVehicleIndex])
        if not self.__isExcursionPlaying:
            SoundGroups.playSound2D(Constants.STOP_SOUND_EVENT)
        self.__uiLogger.setAudioGuideInitialIndex(self.__currentVehicleIndex if self.__isExcursionPlaying else sys.maxint)
        with self.viewModel.transaction() as model:
            model.setIsExcursionPlaying(self.__isExcursionPlaying)
            model.setIsExcursionPaused(False)
        eventValue = Constants.STATES[Constants.EXCURSION_STATE][int(self.__isExcursionPlaying)]
        SoundGroups.setState(Constants.EXCURSION_STATE, eventValue)

    def __onVehicleChanged(self):
        if self.__isSpaceLoaded:
            self.fade(False)

    def __onExcursionPause(self, event):
        self.__isExcursionPaused = event.get('isExcursionPaused')
        SoundGroups.playSound2D(Constants.PAUSE_SOUND_EVENT if self.__isExcursionPaused else Constants.RESUME_SOUND_EVENT)
        self.viewModel.setIsExcursionPaused(self.__isExcursionPaused)

    @args2params(int, int)
    def __onVehiclePlayTimeLog(self, index, time):
        if not self.__isSpaceLoaded:
            return False
        if index >= len(self.__vehDtos):
            LOG_ERROR('[museum of glory] Unknown vehicle with index', index, len(self.__vehDtos))
            return
        vehDto = self.__vehDtos[index]
        if self.__isExcursionPlaying:
            self.__uiLogger.updateAudioGuideCount(index)
            return
        if not self.__audioEnabled:
            return
        self.__uiLogger.updateTankVoiceoverTime(vehDto.name, time)

    def __onExcursionEnd(self):
        self.__uiLogger.updateAudioGuideCount(len(self.__vehDtos))

    def __onConfigUpdate(self):
        self.__isConfigChanged = True
        if self.__isSpaceLoaded:
            self.__onBackToHangar()

    def __onSpaceCreate(self):
        self.__hangarSpace.setSelectionEnabled(True)
        self.__isSpaceLoaded = True
        self.__initWorldSoundPosition()
        self.__hangarFeatureStateController.enter(self.layoutID)
        if self.__isConfigChanged:
            nextTick(self.__onBackToHangar)()
            return
        self.__selectVehicle(self.__selectedVehID)
        self.__uiLogger.increaseTankClickCount(self.__vehDtos[self.__currentVehicleIndex].name)
        self.__initExitSign()
        if getMuseumOfGlorySetting(IS_INTRO_SEEN):
            self.viewModel.setIsIntroPlay(False)
            self.__playAudioGuide()
            return
        self.__startIntro()

    def __onSpaceDestroy(self, _):
        if self.__hangarSpace.spacePath == self.__hangarSwitchController.getSpacePath(MUSEUM_OF_GLORY_SCENE_NAME):
            self.__unloadSpace(False)
            self.destroyWindow()

    def __initWorldSoundPosition(self):
        query = CGF.Query(g_currentPreviewVehicle.hangarSpace.spaceID, (TransformComponent, TankObjectSoundComponent))
        values = query.values()
        if len(values) != 1:
            LOG_ERROR('[MUSEUM] failed to init world sound position')
            return False
        self.__worldSoundPos = values[0][0].position

    def __onAudioCheckboxClicked(self):
        self.__audioEnabled = not self.__audioEnabled
        setMuseumOfGlorySettings(AUDIO_GUIDE_ENABLED, self.__audioEnabled)
        if self.__audioEnabled:
            SoundGroups.playSound2D(Constants.EXCURSION_UNMUTE)
        elif not self.__isExcursionPlaying:
            SoundGroups.playSound2D(Constants.STOP_SOUND_EVENT)
        else:
            SoundGroups.playSound2D(Constants.EXCURSION_MUTE)
        self.__checkIsAudioEnabled()
        self.__stopIntro()

    def __logViewOpened(self):
        player = BigWorld.player()
        if player is None:
            LOG_ERROR('Failed to log view open. Avatar is None')
            return False
        else:
            player.requestSingleToken(VIEW_OPEN_TOKEN)
            return

    def __initExitSign(self):
        spaceID = self.__hangarSpace.spaceID
        if not spaceID:
            return False
        for selectionComp, _ in CGF.Query(spaceID, (SelectionComponent, MuseumLobbyEntry)):
            selectionComp.onClickAction += nextTick(WeakMethodProxy(self.__onBackToHangar))

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return
