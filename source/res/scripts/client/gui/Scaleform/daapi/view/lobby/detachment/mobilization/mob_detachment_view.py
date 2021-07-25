# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/mobilization/mob_detachment_view.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.barracks.sound_constants import BARRACKS_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.detachment import MobilizationRecruitPanel
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.DetachmentMobilizationViewMeta import DetachmentMobilizationViewMeta
from gui.Scaleform.genConsts.DETACHMENT_ALIASES import DETACHMENT_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.auxiliary.detachmnet_convert_helper import getDetachmentFromVehicle
from gui.impl.auxiliary.vehicle_helper import getBestRecruitsForVehicle, isReturnCrewOptionAvailable
from gui.impl.gen.view_models.views.lobby.detachment.common.crew_converting_constants import CrewConvertingConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.fast_operation_button_state import FastOperationButtonState
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.mobilization_view_model import MobilizationViewModel as VehStates
from gui.impl.lobby.detachment.mobilization_view import MobilizationView
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showConvertView
from helpers import dependency
from items.components.detachment_constants import DetachmentConvertationPropertiesMasks
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import ACTION, GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class DetachmentMobilizationView(DetachmentMobilizationViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__useCurrentVehicle', '__installRecruit', '__detachmentToCreate', '__skinID', '__recrutState', '__vehicleState', '__validation', '__validationMask', '__ctx')
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    uiLogger = DetachmentLogger(GROUP.MOBILIZE_CREW)

    def __init__(self, ctx=None):
        super(DetachmentMobilizationView, self).__init__()
        self.__useCurrentVehicle = ctx.get('useCurrentVehicle')
        self.__installRecruit = ctx.get('installRecruit')
        self.__detachmentToCreate = None
        self.__recrutState = None
        self.__vehicleState = None
        self.__validation = None
        self.__validationMask = None
        self.__ctx = ctx
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == HANGAR_ALIASES.DETACHMENT_VIEW_INJECT:
            super(DetachmentMobilizationView, self).registerFlashComponent(component, alias, self.__ctx)
        else:
            super(DetachmentMobilizationView, self).registerFlashComponent(component, alias)

    @property
    def recruitPanel(self):
        return self.getComponent(DETACHMENT_ALIASES.MOBILIZATION_RECRUIT)

    @property
    def gfInject(self):
        return self.getComponent(HANGAR_ALIASES.DETACHMENT_VIEW_INJECT).getInjectView()

    def onEscapePress(self):
        self.gfInject.onEscapePress()

    def onEnterPress(self):
        self.__onContinueInjectView()

    @uiLogger.dStartAction(ACTION.OPEN)
    def _populate(self):
        super(DetachmentMobilizationView, self)._populate()
        self.__addListeners()
        self.gfInject.viewModel.setState(CrewConvertingConstants.NO_VEHICLE_SELECTED)
        installRecruit = self.__installRecruit
        useCurrentVehicle = self.__useCurrentVehicle
        vehicle = None
        if useCurrentVehicle:
            vehicle = g_currentVehicle.item
        elif installRecruit:
            vehicle = self.itemsCache.items.getVehicle(installRecruit.vehicleInvID) or self.itemsCache.items.getItemByCD(installRecruit.vehicleNativeDescr.type.compactDescr)
        if vehicle:
            self.as_updateVehicleFilterButtonS(self.__makeVehicleVO(vehicle))
            self.gfInject.selectVehicle(vehicle)
            self.recruitPanel.selectVehicle(vehicle)
            if installRecruit:
                self.recruitPanel.replaceRecruit(installRecruit)
            self.__updateVehicleState()
        self.as_setIsMedallionEnableS(not useCurrentVehicle)
        self.gfInject.viewModel.setIsMedallionEnable(not useCurrentVehicle)
        return

    @uiLogger.dStopAction(ACTION.OPEN)
    def _dispose(self):
        self.__removeListeners()
        super(DetachmentMobilizationView, self)._dispose()

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onLocksUpdate})
        fastOperation = self.gfInject.viewModel.fastOperation
        self.gfInject.onContinue += self.__onContinueInjectView
        self.recruitPanel.onPerformConvert += self.__onContinueInjectView
        self.gfInject.onFlashLayoutUpdate += self.__onFlashLayoutUpdate
        fastOperation.onRetrainClick += self.__onRetrainClick
        fastOperation.onPreviousClick += self.__onPreviousClick
        fastOperation.onDropInBarrackClick += self.__onDropInBarrackClick
        fastOperation.onTopClick += self.__onTopClick
        self.recruitPanel.onUpdate += self.__onRecruitPanelUpdate
        self.addListener(events.DetachmentViewEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.lobbyContext.onServerSettingsChanged += self.__onLobbyServerSettingsChange
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        fastOperation = self.gfInject.viewModel.fastOperation
        self.gfInject.onContinue -= self.__onContinueInjectView
        self.recruitPanel.onPerformConvert -= self.__onContinueInjectView
        self.gfInject.onFlashLayoutUpdate -= self.__onFlashLayoutUpdate
        fastOperation.onRetrainClick -= self.__onRetrainClick
        fastOperation.onPreviousClick -= self.__onPreviousClick
        fastOperation.onDropInBarrackClick -= self.__onDropInBarrackClick
        fastOperation.onTopClick -= self.__onTopClick
        self.recruitPanel.onUpdate -= self.__onRecruitPanelUpdate
        self.removeListener(events.DetachmentViewEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.lobbyContext.onServerSettingsChanged -= self.__onLobbyServerSettingsChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onContinueInjectView(self):
        recruits = self.recruitPanel.vehicleRecruitsWithSlots
        vehicle = self.recruitPanel.vehicle
        if not vehicle or not recruits:
            return
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.MOBILIZE_CREW_CONFIRMATION)
        showConvertView(vehicle, recruits, prevViewID=NavigationViewModel.MOBILIZATION)

    def __onLobbyServerSettingsChange(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self.__onServerSettingsChange

    def __onServerSettingsChange(self, _):
        self.__updateConvertButton()

    def __onLocksUpdate(self, _):
        self.__updateVehicleState()
        self.__updateRecruitsState()
        self.__updateFastOperation()
        self.__updateConvertButton()

    def __onRecruitPanelUpdate(self, validation, validationMask):
        self.__validation = validation
        self.__validationMask = validationMask
        self.__updateRecruitsState()
        self.__updateFastOperation()
        self.__updateConvertButton()

    def __updateRecruitsState(self):
        validation, validationMask = self.__validation, self.__validationMask
        state = CrewConvertingConstants.CONVERTING_AVAILABLE
        recruits = self.recruitPanel.vehicleRecruits
        vehicle = self.recruitPanel.vehicle
        if not vehicle:
            return
        if not any(recruits):
            state = CrewConvertingConstants.NOT_FORMED
        elif vehicle.isInPrebattle or self.__isAnyRecruitInPrebattle(recruits):
            state = CrewConvertingConstants.IN_PLATOON
        elif vehicle.isLocked or self.__isAnyRecruitInBattle(recruits):
            state = CrewConvertingConstants.IN_BATTLE
        elif validationMask & DetachmentConvertationPropertiesMasks.FULL_CREW:
            state = CrewConvertingConstants.NOT_FORMED
        elif validationMask & DetachmentConvertationPropertiesMasks.PRESET:
            state = CrewConvertingConstants.LEADERS_OVERFLOW
        elif validationMask & DetachmentConvertationPropertiesMasks.SPECIALIZATION:
            state = CrewConvertingConstants.NEED_RETRAIN
        elif not validation:
            state = CrewConvertingConstants.NOT_FORMED
        if state != CrewConvertingConstants.NOT_FORMED:
            detDescr, instDescrs, _, skinID = getDetachmentFromVehicle(vehicle, self.recruitPanel.vehicleRecruitsWithSlots)
            self.gfInject.setDetachment(detDescr, instDescrs, skinID)
            self.__detachmentToCreate = detDescr
            self.__skinID = skinID
        self.__recrutState = state
        self.gfInject.viewModel.setState(state)
        self.as_setConversionStateS(state)
        self.as_setRecruitsEnabledS(not vehicle.isInBattle and not vehicle.isInUnit)

    def __updateVehicleState(self):
        vehicle = self.recruitPanel.vehicle
        if not vehicle:
            return
        state = VehStates.VEHICLE_DEFAULT
        if vehicle.isInBattle:
            state = VehStates.VEHICLE_IN_BATTLE
        elif vehicle.isLocked:
            state = VehStates.VEHICLE_IN_PLATOON
        elif vehicle.isCrewLocked:
            state = VehStates.VEHICLE_LOCK_CREW
        elif vehicle.isPremium:
            state = VehStates.VEHICLE_ELITE
        self.__vehicleState = state
        self.gfInject.viewModel.setVehicleStatus(state)

    def __updateConvertButton(self):
        convertAvailable = self.__recrutState == CrewConvertingConstants.CONVERTING_AVAILABLE and self.__vehicleState not in (VehStates.VEHICLE_IN_BATTLE, VehStates.VEHICLE_IN_PLATOON) and self.lobbyContext.getServerSettings().isDetachmentManualConversionEnabled()
        self.recruitPanel.as_setConvertAvailableS(convertAvailable)

    def __updateFastOperation(self):
        vehicle = self.recruitPanel.vehicle
        if not vehicle:
            return
        else:
            recruits = self.recruitPanel.vehicleRecruits
            recruitIDs = [ (recruit.invID if recruit else None) for recruit in recruits ]
            fastOperation = self.gfInject.viewModel.fastOperation
            state = FastOperationButtonState.AVAILABLE
            if not any(recruits):
                state = FastOperationButtonState.EMPTY
            elif not self.__isAnyRecruitNeedTrain(vehicle):
                state = FastOperationButtonState.ALL_IN_PLACE
            elif self.__isAnyRecruitInBattle(recruits) or vehicle.isInBattle:
                state = FastOperationButtonState.IN_BATTLE
            elif self.__isAnyRecruitInPrebattle(recruits) or vehicle.isInPrebattle:
                state = FastOperationButtonState.IN_PLATOON
            fastOperation.setRetrainState(state)
            state = FastOperationButtonState.AVAILABLE
            if vehicle.lastDetachmentID:
                state = FastOperationButtonState.UNKNOWN
            elif not vehicle.lastDetachmentID and not vehicle.lastCrew:
                state = FastOperationButtonState.EMPTY
            else:
                if vehicle.isInBattle:
                    state = FastOperationButtonState.IN_BATTLE
                elif vehicle.isInPrebattle:
                    state = FastOperationButtonState.IN_PLATOON
                if not isReturnCrewOptionAvailable(vehicle, recruitIDs):
                    state = FastOperationButtonState.ALL_IN_PLACE if state == FastOperationButtonState.AVAILABLE else FastOperationButtonState.UNKNOWN
            fastOperation.setPreviousState(state)
            bestRecruitsIds = getBestRecruitsForVehicle(vehicle)
            state = FastOperationButtonState.AVAILABLE
            if vehicle.isCrewLocked:
                state = FastOperationButtonState.LOCK_CREW
            elif all((recruit is None for recruit in bestRecruitsIds)):
                state = FastOperationButtonState.EMPTY
            elif set(bestRecruitsIds) == set(recruitIDs):
                state = FastOperationButtonState.ALL_IN_PLACE
            elif self.__isAnyRecruitInPrebattle((self.itemsCache.items.getTankman(invID) for invID in bestRecruitsIds)) or vehicle.isInPrebattle:
                state = FastOperationButtonState.IN_PLATOON
            elif self.__isAnyRecruitInBattle((self.itemsCache.items.getTankman(invID) for invID in bestRecruitsIds)) or vehicle.isInBattle:
                state = FastOperationButtonState.IN_BATTLE
            fastOperation.setTopState(state)
            state = FastOperationButtonState.AVAILABLE
            if vehicle.isInBattle:
                state = FastOperationButtonState.IN_BATTLE
            elif vehicle.isInPrebattle:
                state = FastOperationButtonState.IN_PLATOON
            elif vehicle.isCrewLocked:
                state = FastOperationButtonState.LOCK_CREW
            elif not any(recruits):
                state = FastOperationButtonState.EMPTY
            fastOperation.setDropInBarrackState(state)
            return

    def __isAnyRecruitNeedTrain(self, vehicle):
        return any((recruit.vehicleNativeDescr.type.compactDescr != vehicle.intCD for recruit in self.recruitPanel.vehicleRecruits if recruit))

    def __isAnyRecruitInBattle(self, recruits):
        recruitVehs = (self.itemsCache.items.getVehicle(recruit.vehicleInvID) for recruit in recruits if recruit)
        return any((recruit.isInBattle or recruit.isAwaitingBattle for recruit in recruitVehs if recruit))

    def __isAnyRecruitInPrebattle(self, recruits):
        recruitVehs = (self.itemsCache.items.getVehicle(recruit.vehicleInvID) for recruit in recruits if recruit)
        return any((tankmanVehicle.isInPrebattle for tankmanVehicle in recruitVehs if tankmanVehicle))

    def __onFlashLayoutUpdate(self, event):
        self.as_updateComponentPositionS(event.get('id'), event.get('posX'), event.get('posY'), event.get('width'), event.get('height'))

    def __onVehicleSelected(self, event):
        if event.ctx and event.ctx.get('vehicleId'):
            vehicle = self.itemsCache.items.getItemByCD(event.ctx['vehicleId'])
            self.as_updateVehicleFilterButtonS(self.__makeVehicleVO(vehicle))
            self.gfInject.selectVehicle(vehicle)
            self.recruitPanel.selectVehicle(vehicle)
            self.__updateVehicleState()
            self.__updateConvertButton()

    @uiLogger.dLog(ACTION.SELECT_BEST_RECRUITS)
    def __onTopClick(self):
        self.recruitPanel.setBestCrew(native=False)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.RETRAIN_CREW_DIALOG)
    def __onRetrainClick(self):
        self.recruitPanel.onRetrainRecruits()

    @uiLogger.dLog(ACTION.RETURN_PREVIOUS_RECRUIT_CONFIGURATION)
    def __onPreviousClick(self):
        self.recruitPanel.onReturnCrew()

    @uiLogger.dLog(ACTION.UNLOAD_ALL_RECRUITS)
    def __onDropInBarrackClick(self):
        self.recruitPanel.onUnloadRecruits()

    @staticmethod
    def __makeVehicleVO(vehicle):
        if vehicle is None:
            return
        else:
            vo = makeVehicleVO(vehicle)
            vo.update({'type': '{}_elite'.format(vehicle.type) if vehicle.isPremium else vehicle.type})
            return vo
