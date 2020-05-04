# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_subdivision_view.py
import logging
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_subdivision_model import ActionSubdivisionModel
from gui.impl.gen.view_models.views.lobby.secret_event.subdivision_model import SubdivisionModel
from gui.impl.lobby.secret_event import RewardListMixin, VehicleMixin, AbilitiesMixin, ProgressMixin
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.lobby.secret_event.sound_constants import SOUND
_logger = logging.getLogger(__name__)
_MAX_PROGRESS_BAR_VALUE = 100

class ActionSubdivisionView(ActionViewWithMenu, RewardListMixin, VehicleMixin, AbilitiesMixin, ProgressMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    ABILITY_TOOLTIP_EVENTS = (TOOLTIPS_CONSTANTS.COMMANDER_RESPAWN_INFO, TOOLTIPS_CONSTANTS.COMMANDER_ABILITY_INFO)
    __slots__ = ('__isFromPanel',)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ActionSubdivisionModel()
        self.__isFromPanel = ctx.get('isFromPanel') if ctx is not None else False
        super(ActionSubdivisionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if 'rewardTooltip' in tooltipId:
                window = RewardListMixin.createToolTip(self, event)
            elif tooltipId in self.ABILITY_TOOLTIP_EVENTS or tooltipId == TOOLTIPS_CONSTANTS.EVENT_SQUAD_GENERAL_INFO:
                window = self._createSkillToolTip(event)
            if window is None:
                tankId = event.getArgument('tankId', None)
                specialArgs = []
                if tankId:
                    specialArgs = [int(tankId)]
                    tooltipId = TOOLTIPS_CONSTANTS.EVENT_VEHICLE
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
                window.load()
            return window
        else:
            return super(ActionSubdivisionView, self).createToolTip(event)

    def _createSkillToolTip(self, event):
        window = BackportTooltipWindow(createTooltipData(specialAlias=event.getArgument('tooltipId'), isSpecial=True, specialArgs=[event.getArgument('key')]), self.getParentWindow())
        window.load()
        return window

    def _initialize(self):
        super(ActionSubdivisionView, self)._initialize()
        if self.__isFromPanel:
            self.soundManager.playInstantSound(SOUND.SECRET_EVENT_TEAM_HIGHLIGHT_SOUND_EVENT)
        self.__addListeners()

    def _onLoading(self):
        super(ActionSubdivisionView, self)._onLoading()
        self.__fillViewModel(self.viewModel)

    def _finalize(self):
        self.__removeListeners()
        super(ActionSubdivisionView, self)._finalize()

    def __addListeners(self):
        self.viewModel.onBuyClick += self.__onBuyClick
        self.gameEventController.onProgressChanged += self.__onProgressChanged

    def __removeListeners(self):
        self.viewModel.onBuyClick -= self.__onBuyClick
        self.gameEventController.onProgressChanged -= self.__onProgressChanged

    def __onProgressChanged(self):
        self.soundManager.playInstantSound(SOUND.SECRET_EVENT_MISSION_PROGRESS_SOUND_EVENT)
        with self.viewModel.transaction() as vm:
            self.__fillViewModel(vm)

    def __fillViewModel(self, vm):
        vm.setRevision(vm.getRevision() + 1)
        vm.setCurrentView(ActionMenuModel.SUBDIVISION)
        generals = vm.generals.getItems()
        generals.clear()
        for id_ in self.gameEventController.getCommanders():
            commanderProgress = self.gameEventController.getCommander(id_)
            subdivision = SubdivisionModel()
            subdivision.setId(id_)
            subdivision.setLabel(R.strings.event.unit.name.num(id_)())
            if self.__isFromPanel:
                subdivision.setIsSelected(id_ == self.gameEventController.getSelectedCommanderID())
            subdivision.setLogo(R.images.gui.maps.icons.secretEvent.generalIcons.dyn('g_icon{0}'.format(id_))())
            progressionData = self.getCommonProgressionData(commanderProgress)
            subdivision.setIsDone(progressionData.isCompleted)
            progressData = []
            for idx, item in enumerate(commanderProgress.getItems(), 1):
                if item.getMaxProgress() != 0:
                    progressData.append((item.getCurrentProgress(), item.getMaxProgress()))
                levelModel = getattr(subdivision, 'level{}'.format(idx))
                levelModel.setIsComplete(item.isCompleted())
                vehicleData = self.getVehicleDataByLevel(commanderProgress, idx - 1)
                vehicleIconName = vehicleData.vehicle.name.split(':', 1)[-1].replace('-', '_')
                levelModel.setTankIcon(R.images.gui.maps.icons.secretEvent.vehicles.c_48x48.dyn(vehicleIconName)())
                levelModel.setTankId(vehicleData.typeCompDescr)
                level = item.getLevel()
                self.fillAbilitiesList(levelModel.abilities, commanderProgress, level, level)

            subdivision.setCurrentProgress(int(_MAX_PROGRESS_BAR_VALUE * sum((progress[0] / float(progress[1]) for progress in progressData))))
            subdivision.setMaxProgress(_MAX_PROGRESS_BAR_VALUE * len(progressData))
            generals.addViewModel(subdivision)

    def __onBuyClick(self, args=None):
        pass
