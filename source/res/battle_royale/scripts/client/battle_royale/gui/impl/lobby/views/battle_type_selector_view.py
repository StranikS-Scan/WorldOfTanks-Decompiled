# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/battle_type_selector_view.py
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from battle_royale.gui.constants import BattleRoyaleSubMode
from frameworks.wulf import ViewFlags, ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_type_selector_view_model import BattleTypeSelectorViewModel, BattleType, AnimationState
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from battle_royale.gui.impl.lobby.tooltips.tab_tooltip_view import TabTooltipView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.tutorial import ITutorialLoader
from tutorial.data.hints import HintProps
from tutorial.gui import GUI_EFFECT_NAME
SubModeIdToBattleType = {BattleRoyaleSubMode.SOLO_MODE_ID: BattleType.SOLO,
 BattleRoyaleSubMode.SOLO_DYNAMIC_MODE_ID: BattleType.RANDOMPLATOON,
 BattleRoyaleSubMode.SQUAD_MODE_ID: BattleType.PLATOON}
BattleTypeToSubMode = {v:k for k, v in SubModeIdToBattleType.items()}

class BattleTypeSelectorView(ViewImpl):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    tutorialLoader = dependency.descriptor(ITutorialLoader)
    HINT_ID = OnceOnlyHints.BATTLE_ROYALE_DYNAMIC_PLATOON_SUB_MODE_HINT
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.BattleTypeSelectorView())
        settings.flags = ViewFlags.VIEW
        settings.model = BattleTypeSelectorViewModel()
        super(BattleTypeSelectorView, self).__init__(settings)

    @property
    def _hintsManagerGui(self):
        hintsManager = self.tutorialLoader.hintsManager
        return hintsManager._gui if hintsManager is not None else None

    @property
    def viewModel(self):
        return super(BattleTypeSelectorView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return TabTooltipView(event.getArgument('tabId')) if contentID == R.views.battle_royale.lobby.tooltips.TabTooltipView() else super(BattleTypeSelectorView, self).createToolTipContent(event, contentID)

    def playAnimation(self, isFirstShow):
        self.viewModel.setAnimationState(AnimationState.FIRSTSHOW if isFirstShow else AnimationState.IDLEBLINK)

    def _onLoading(self, *args, **kwargs):
        super(BattleTypeSelectorView, self)._onLoading(args, kwargs)
        self.updateFakeBg()
        self.__onSubModeUpdated()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()

    def __addListeners(self):
        self.viewModel.onSelectTab += self.__onSelectTab
        self.__battleRoyaleController.onSubModeUpdated += self.__onSubModeUpdated
        self.__settingsCore.onOnceOnlyHintsChanged += self.__onOnceOnlyHintsChanged
        if self._hintsManagerGui:
            self._hintsManagerGui.onHintShowing += self._onHintShowing

    def __removeListeners(self):
        self.viewModel.onSelectTab -= self.__onSelectTab
        self.__battleRoyaleController.onSubModeUpdated -= self.__onSubModeUpdated
        self.__settingsCore.onOnceOnlyHintsChanged -= self.__onOnceOnlyHintsChanged
        if self._hintsManagerGui:
            self._hintsManagerGui.onHintShowing -= self._onHintShowing

    def __onSelectTab(self, args):
        tabId = args.get('tabId')
        subModeID = BattleTypeToSubMode.get(BattleType(tabId), BattleRoyaleSubMode.SOLO_MODE_ID)
        self.__battleRoyaleController.selectSubModeBattle(subModeID)

    def __onOnceOnlyHintsChanged(self, diff):
        if self.HINT_ID not in diff.keys():
            return
        hintShown = bool(self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(self.HINT_ID))
        self.viewModel.setIsHintShown(not hintShown)

    def __updateTabId(self, tabId):
        self.viewModel.setSelectedTab(tabId)

    def __onSubModeUpdated(self, *args):
        subModeId = self.__battleRoyaleController.getCurrentSubModeID()
        battleType = SubModeIdToBattleType.get(subModeId, BattleType.SOLO)
        self.__updateTabId(battleType)

    def updateFakeBg(self):
        hintShowing = False
        if self._hintsManagerGui:
            hintShowing = self._hintsManagerGui.isEffectRunning(GUI_EFFECT_NAME.SHOW_HINT, self.HINT_ID)
        self.viewModel.setIsHintShown(hintShowing)

    def _onHintShowing(self, props):
        if props.hintID == self.HINT_ID:
            self.updateFakeBg()
