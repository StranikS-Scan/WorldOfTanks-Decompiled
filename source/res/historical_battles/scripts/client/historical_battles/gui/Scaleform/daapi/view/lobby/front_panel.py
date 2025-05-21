# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/front_panel.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.hangar_selectable_view import HangarSelectableView
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.gui.impl.gen.view_models.views.lobby.front_panel_model import FrontPanelModel
from historical_battles.gui.impl.gen.view_models.views.lobby.front_model import FrontModel, FrontStateType
from historical_battles.gui.prb_control import prb_config
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.shared.event_dispatcher import showInfoPage
_logger = logging.getLogger(__name__)

class FrontPanel(InjectComponentAdaptor):

    def _makeInjectView(self):
        return FrontPanelView(R.views.historical_battles.lobby.FrontPanel())


class FrontPanelView(HangarSelectableView):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = FrontPanelModel()
        super(FrontPanelView, self).__init__(settings)
        self.__callbackDelayer = CallbackDelayer()
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        self.frontName = currentFront.getName()

    @property
    def viewModel(self):
        return super(FrontPanelView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        return super(FrontPanelView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(FrontPanelView, self)._onLoading(*args, **kwargs)
        self.viewModel.onFrontClick += self.__onFrontClick
        self.viewModel.onClose += self.__onClose
        self.viewModel.onAboutClick += self.__onAboutClick
        self.__gameEventController.frontDataUpdated += self.__updateSelectedFront
        self.__gameEventController.onFrontTimeStatusUpdated += self.__onFrontTimeStatusUpdated
        self.__gameEventController.onDisableFrontsWidget += self.__onDisableFrontsWidget
        self.__fillViewModel()

    def __onFrontClick(self, args):
        newFrontName = args.get('frontName')
        if newFrontName == self.frontName:
            return
        self.frontName = newFrontName
        frontID = self.__gameEventController.frontController.getFrontIdByName(self.frontName)
        self.__gameEventController.updateFrontData(frontId=frontID)

    def _onLoaded(self, *args, **kwargs):
        super(FrontPanelView, self)._onLoaded(*args, **kwargs)
        SelectorBattleTypesUtils.setBattleTypeAsKnown(prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES)

    def _finalize(self):
        self.__callbackDelayer.clearCallbacks()
        self.viewModel.onFrontClick -= self.__onFrontClick
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onAboutClick -= self.__onAboutClick
        self.__gameEventController.onDisableFrontsWidget -= self.__onDisableFrontsWidget
        self.__gameEventController.onFrontTimeStatusUpdated -= self.__onFrontTimeStatusUpdated
        self.__gameEventController.frontDataUpdated -= self.__updateSelectedFront
        super(FrontPanelView, self)._finalize()

    def __fillViewModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillFronts(tx)
            tx.setIsDisabled(self.__gameEventController.frontsWidgetDisabled)

    def __fillFronts(self, tx):
        fronts = tx.getFronts()
        fronts.clear()
        currentSelectedFront = self.__gameEventController.frontController.getSelectedFront()
        for front in self.__gameEventController.frontController.getOrderedFrontsList():
            fronts.addViewModel(self.__createFront(front))

        fronts.invalidate()
        tx.setSelectedFront(self.frontName)
        if currentSelectedFront is None:
            return
        else:
            self.__updateSelectedFront(currentSelectedFront.getID(), None)
            return

    def __onDisableFrontsWidget(self, isDisabled):
        with self.viewModel.transaction() as tx:
            tx.setIsDisabled(isDisabled)

    def __onSettingsChanged(self, diff):
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self.__updateFronts()

    def __updateFronts(self, *_):
        with self.viewModel.transaction() as tx:
            self.__updateFrontStates(tx)

    def __createFront(self, front):
        frontModel = FrontModel()
        frontModel.setFrontName(front.getName())
        frontModel.setFrontState(FrontStateType.AVAILABLE)
        self.__updateFrontState(frontModel)
        return frontModel

    def __updateFrontStates(self, tx):
        fronts = tx.getFronts()
        for front in fronts:
            self.__updateFrontState(front)

        fronts.invalidate()

    def __updateFrontState(self, front):
        frontProgress = self.__gameEventController.frontController.getFrontByName(front.getFrontName())
        if frontProgress is None:
            return
        else:
            enabled = frontProgress.isEnabled()
            delta = self.__gameEventController.getTimeLeftToStartFront(frontProgress.getID())
            front.setCountDownSeconds(delta)
            front.setFrontState((FrontStateType.AVAILABLE if delta <= 0 else FrontStateType.COUNTDOWN) if enabled else FrontStateType.SOON)
            return

    def __updateSelectedFront(self, frontId, _):
        if frontId is None:
            return
        else:
            front = self.__gameEventController.frontController.getFrontByID(frontId)
            self.frontName = front.getName()
            with self.viewModel.transaction() as tx:
                tx.setSelectedFront(self.frontName)
                self.__updateFrontStates(tx)
            return

    def __onFrontTimeStatusUpdated(self, frontId):
        self.__updateFronts()

    def __onClose(self):
        self.__gameEventController.selectRandomMode()

    def __onAboutClick(self):
        showInfoPage()
