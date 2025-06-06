# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_video_rewards_view.py
import itertools
import logging
import BigWorld
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_video_rewards_view_model import PersonalMissionsVideoRewardsViewModel, OperationState
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.personal_missions.personal_mission_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.finders import BRANCH_TO_OPERATION_IDS
from items.vehicles import getVehicleClassFromVehicleType
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.game_control import IPersonalMissionsController
from gui.shared.event_dispatcher import showHangar
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
from gui.impl.lobby.personal_missions.video_sound_control.video_sound_control import PM3VideoSoundControl
from gui.shared.events import PersonalMissionsEvent
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
_logger = logging.getLogger(__name__)

class PersonalMissionsVideoRewardsView(ViewImpl):
    __slots__ = ('__vehicle', '__operation', '__soundControl', '__tooltipData')
    __itemsCache = dependency.descriptor(IItemsCache)
    __personalMissionsController = dependency.descriptor(IPersonalMissionsController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __LOW_QUALITY_PRESETS = ('LOW', 'MIN')

    def __init__(self, layoutID, operationId):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsVideoRewardsViewModel()
        super(PersonalMissionsVideoRewardsView, self).__init__(settings)
        self.__operation = self.__personalMissionsController.getOperationById(operationId)
        if self.__operation is not None:
            self.__vehicle = self.__operation.getVehicleBonus()
        BigWorld.worldDrawEnabled(False)
        self.__soundControl = PM3VideoSoundControl(operationId)
        self.__tooltipData = {}
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsVideoRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PersonalMissionsVideoRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        index = event.getArgument('tooltipId')
        return self.__tooltipData.get(index, None)

    def getOperationState(self):
        if self.__operation.isFullCompleted():
            return OperationState.COMPLETEWITHHONOR
        return OperationState.COMPLETE if self.__operation.isCompleted() else OperationState.COMPLETE

    def _finalize(self):
        BigWorld.worldDrawEnabled(True)
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.__soundControl.stop()
        super(PersonalMissionsVideoRewardsView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onError, self.__onError),
         (self.viewModel.onShowVehicle, self.__onShowVehicle),
         (self.viewModel.onVideoStarted, self.__onVideoStarted))

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsVideoRewardsView, self)._onLoading(*args, **kwargs)
        if self.__vehicle is None:
            return
        else:
            with self.viewModel.transaction() as vm:
                vm.setVehicleName(self.__vehicle.userName)
                vm.setVehicleLvl(self.__vehicle.level)
                vm.setVehicleType(getVehicleClassFromVehicleType(self.__vehicle.descriptor.type))
                vm.setIsElite(self.__vehicle.isElite)
                vm.setIsWindowAccessible(Windowing.isWindowAccessible())
                vm.setVideoName(self.__getVideoNameByPreset(self.__operation.getID()))
                bonusList = []
                pm3ctrl = self.__personalMissionsController
                for bonus in itertools.chain(*self.__operation.getBonuses().itervalues()):
                    if bonus.getName() not in ('vehicles', 'slots'):
                        bonusList.append(bonus)

                if self.__operation.isFullCompleted():
                    bonusList.extend(pm3ctrl.getAddBonusesForOperation(self.__operation))
                lastPM3Operation = BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_3][-1]
                if self.__operation.getID() == lastPM3Operation and all((pm3ctrl.getOperationById(operationId).isFullCompleted() for operationId in BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_3])):
                    bonusList.extend(pm3ctrl.getBadgesForChampionQuestPM3())
                packBonusModelAndTooltipData(bonusList, vm.getRewards(), self.__tooltipData)
                vm.setState(OperationState.COMPLETEWITHHONOR if self.__operation.isFullCompleted() else OperationState.COMPLETE)
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
            return

    def __getVideoNameByPreset(self, operationId):
        presetIndx = BigWorld.detectGraphicsPresetFromSystemSettings()
        lowPresets = [ BigWorld.getSystemPerformancePresetIdFromName(pName) for pName in self.__LOW_QUALITY_PRESETS ]
        videoName = 'operation_{}'.format(operationId)
        return '{}_min'.format(videoName) if presetIndx in lowPresets else videoName

    def __onClose(self):
        self.destroyWindow()
        g_eventBus.handleEvent(PersonalMissionsEvent(PersonalMissionsEvent.ON_AWARD_PM_SCREEN_CLOSE, ctx={'operationID': self.__operation.getID()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('Reward video error: %s', errorFilePath)
        self.destroyWindow()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundControl.unpause()
        else:
            self.__soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __onShowVehicle(self):
        vehicle = self.__itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if vehicle.isInInventory:
            showHangar()
            g_currentVehicle.selectVehicle(vehicle.invID)
            self.destroyWindow()

    def __onVideoStarted(self):
        self.__soundControl.start()
        if not Windowing.isWindowAccessible():
            self.__soundControl.pause()


class PersonalMissionsVideoRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, operationId=None, parent=None):
        super(PersonalMissionsVideoRewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalMissionsVideoRewardsView(R.views.lobby.personal_missions.PersonalMissionsVideoRewardsView(), operationId=operationId), parent=parent, layer=WindowLayer.OVERLAY)
