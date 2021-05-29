# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_3d_style_choice_view.py
import logging
import AccountCommands
from account_helpers.battle_pass import selectProgressionStyle
from battle_pass_common import BattlePassConsts
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.battle_pass.battle_pass_helpers import getCurrentStyleLevel, getStyleInfo
from gui.battle_pass.state_machine.state_machine_helpers import getStylesToChooseUntilChapter
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass3d_style_choice_view_model import BattlePass3DStyleChoiceViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tank_style_model import TankStyleModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showBattlePass3dStyleChoiceWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import hideVehiclePreview, showProgressionStylesStylePreview
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from gui.impl.lobby.battle_pass.tooltips.battle_pass_style_info_tooltip_view import BattlePassStyleInfoTooltipView
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD

class _BattlePassViewStates(object):

    def __init__(self):
        self.wasOpenChoiceView = False
        self.isGoingToOpenChoiceView = False
        self.currentLevelStyle = 1

    def prepareToOpenPreview(self):
        self.reset()
        self.wasOpenChoiceView = True
        g_eventBus.addListener(events.BattlePassEvent.ON_PREVIEW_PROGRESSION_STYLE_CLOSE, self.__onPreviewProgressionStyleClose, scope=EVENT_BUS_SCOPE.LOBBY)

    def getLevel(self):
        return self.currentLevelStyle if self.wasOpenChoiceView and self.isGoingToOpenChoiceView else 1

    def reset(self):
        self.wasOpenChoiceView = False
        self.isGoingToOpenChoiceView = False
        self.currentLevelStyle = 1

    def __onPreviewProgressionStyleClose(self, event):
        if self.wasOpenChoiceView:
            self.currentLevelStyle = event.ctx.get('level')
        else:
            self.currentLevelStyle = 1
        g_eventBus.removeListener(events.BattlePassEvent.ON_PREVIEW_PROGRESSION_STYLE_CLOSE, self.__onPreviewProgressionStyleClose, scope=EVENT_BUS_SCOPE.LOBBY)


_BPViewStates = _BattlePassViewStates()
_rBattlePass = R.strings.battle_pass
_logger = logging.getLogger(__name__)

class BattlePass3dStyleChoiceView(ViewImpl):
    __slots__ = ('__level', '__previewOpened')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattlePass3DStyleChoiceViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__level = _BPViewStates.getLevel()
        self.__previewOpened = False
        super(BattlePass3dStyleChoiceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePass3dStyleChoiceView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BattlePassStyleInfoTooltipView()

    def _onLoading(self, *args, **kwargs):
        super(BattlePass3dStyleChoiceView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        with self.viewModel.transaction() as tx:
            for styleBonus in self.__battlePassController.getStylesConfig():
                tankStyleModel = TankStyleModel()
                styleInfo = getStyleInfo(styleBonus)
                tankStyleModel.setStyleId(styleInfo.id)
                tankStyleModel.setStyleName(styleInfo.userName)
                vehicleCD = getVehicleCDForStyle(styleInfo)
                vehicle = getVehicleByIntCD(vehicleCD)
                fillVehicleInfo(tankStyleModel.vehicleInfo, vehicle)
                tankStyleModel.setIsInHangar(vehicle.isInInventory)
                tankStyleModel.setIsObtained(bool(styleInfo.fullCount()))
                tx.tankStylesList.addViewModel(tankStyleModel)

            currentChapterLevel = self.__battlePassController.getCurrentChapter()
            chosenItems = self.__itemsCache.items.battlePass.getChosenItems()
            if currentChapterLevel not in chosenItems:
                isChoiceEnabled = True
                if chosenItems:
                    chapterLevel = max(chosenItems.keys()) + 1
                else:
                    chapterLevel = BattlePassConsts.MINIMAL_CHAPTER_NUMBER
            else:
                chapterLevel = currentChapterLevel
                isChoiceEnabled = False
            tx.setIsChoiceEnabled(isChoiceEnabled)
            tx.setChapterNumber(chapterLevel)
            tx.setCurrentLevel(getCurrentStyleLevel(self.__battlePassController.getSeasonID(), chapterLevel))
            tx.setSelectedLevel(self.__level)
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        self.__removeListeners()
        switchHangarOverlaySoundFilter(on=False)
        if not self.__previewOpened:
            _BPViewStates.reset()
            self.__battlePassController.getRewardLogic().postStateEvent()
        self.__previewOpened = False
        super(BattlePass3dStyleChoiceView, self)._finalize()

    def __addListeners(self):
        self.viewModel.onSelectLevel += self.__onSelectLevel
        self.viewModel.onConfirmStyle += self.__onConfirmStyle
        self.viewModel.onPreviewClick += self.__onPreviewClick
        self.viewModel.onCloseOverlay += self.__onCloseOverlay

    def __removeListeners(self):
        self.viewModel.onSelectLevel -= self.__onSelectLevel
        self.viewModel.onConfirmStyle -= self.__onConfirmStyle
        self.viewModel.onPreviewClick -= self.__onPreviewClick
        self.viewModel.onCloseOverlay -= self.__onCloseOverlay

    def __onSelectLevel(self, args):
        level = args.get('level')
        if level is None:
            return
        else:
            self.__level = level
            with self.viewModel.transaction() as tx:
                tx.setSelectedLevel(self.__level)
            return

    def __onPreviewClick(self, args):
        styleID = args.get('styleId')
        styleInfo = None
        for styleBonus in self.__battlePassController.getStylesConfig():
            if first(styleBonus.getValue()).get('id') == styleID:
                styleInfo = getStyleInfo(styleBonus)
                break

        if styleInfo is None:
            _logger.error('Failed to get style for preview! Check server settings are correct.')
            return
        else:
            self.__previewOpened = True
            hideVehiclePreview(back=False)
            vehicleCD = getVehicleCDForStyle(styleInfo)
            self.__battlePassController.getRewardLogic().postPreviewOpen()
            _BPViewStates.prepareToOpenPreview()
            showProgressionStylesStylePreview(vehicleCD, styleInfo, styleInfo.getDescription(), self.__previewCallback, backport.text(_rBattlePass.choose3dStyle.preview.backLabel()), self.__level)
            return

    def __previewCallback(self):
        self.__previewOpened = False
        self.__battlePassController.getRewardLogic().postClosePreview()
        _BPViewStates.isGoingToOpenChoiceView = True
        showBattlePass3dStyleChoiceWindow()

    def __onConfirmStyle(self, args):
        styleID = args.get('styleId')
        styleInfo = None
        for styleBonus in self.__battlePassController.getStylesConfig():
            if first(styleBonus.getValue()).get('id') == styleID:
                styleInfo = getStyleInfo(styleBonus)
                break

        if styleInfo is None:
            _logger.error('Failed to get style for select! Check server settings are correct.')
            return
        else:
            Waiting.show('chooseStyle')
            selectProgressionStyle(styleInfo.intCD, self.__responseSelectStyle)
            return

    def __responseSelectStyle(self, requestID, resultID, errorStr):
        Waiting.hide('chooseStyle')
        if resultID >= AccountCommands.RES_SUCCESS:
            rewardLogic = self.__battlePassController.getRewardLogic()
            rewardLogic.markStyleChosen(self.viewModel.getChapterNumber())
            if not rewardLogic.hasActiveFlow():
                for styleChapter in getStylesToChooseUntilChapter(self.__battlePassController.getCurrentChapter() + 1):
                    rewardLogic.addStyleToChoose(styleChapter)
                    rewardLogic.postStateEvent()

            self.destroyWindow()
        else:
            with self.viewModel.transaction() as tx:
                tx.setIsNeedToCloseOverlay(True)
            SystemMessages.pushI18nMessage(backport.text(_rBattlePass.choose3dStyle.error()), type=SystemMessages.SM_TYPE.Error)

    def __onCloseOverlay(self):
        with self.viewModel.transaction() as tx:
            tx.setIsNeedToCloseOverlay(False)


class BattlePass3dStyleChoiceWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(BattlePass3dStyleChoiceWindow, self).__init__(WindowFlags.WINDOW, content=BattlePass3dStyleChoiceView(R.views.lobby.battle_pass.BattlePass3dStyleChoiceView()), parent=parent)
