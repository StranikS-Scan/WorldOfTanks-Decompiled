# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_hangar_widget_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasDesiredSubMode
from fun_random.gui.impl.lobby.common.fun_view_helpers import defineProgressionStatus, packProgressionState, packProgressionActiveStage
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_hangar_widget_view_model import FunRandomHangarWidgetViewModel
from fun_random.gui.impl.lobby.tooltips.fun_random_domain_tooltip_view import FunRandomDomainTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_progression_tooltip_view import FunRandomProgressionTooltipView
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage
    from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState

class FunRandomHangarWidgetView(ViewImpl, FunSubModesWatcher, FunProgressionWatcher):

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.COMPONENT, model=FunRandomHangarWidgetViewModel())
        super(FunRandomHangarWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomHangarWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView():
            modifiersDomain = event.getArgument('modifiersDomain')
            return FunRandomDomainTooltipView(modifiersDomain)
        return FunRandomProgressionTooltipView() if contentID == R.views.fun_random.lobby.tooltips.FunRandomProgressionTooltipView() else super(FunRandomHangarWidgetView, self).createToolTipContent(event, contentID)

    @hasActiveProgression(abortAction='showInfoPage')
    def showActiveProgressionPage(self, *_):
        super(FunRandomHangarWidgetView, self).showActiveProgressionPage()

    @hasDesiredSubMode()
    def showInfoPage(self):
        self.showSubModeInfoPage(self.getDesiredSubMode().getSubModeID())

    def _getEvents(self):
        return ((self.viewModel.onShowInfo, self.showActiveProgressionPage),)

    def _finalize(self):
        self.stopSubSelectionListening(self.__invalidateAll)
        self.stopSubSettingsListening(self.__invalidateAll, desiredOnly=True)
        self.stopProgressionListening(self.__onProgressionUpdate)
        super(FunRandomHangarWidgetView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomHangarWidgetView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__onProgressionUpdate)
        self.startSubSettingsListening(self.__invalidateAll, desiredOnly=True)
        self.startSubSelectionListening(self.__invalidateAll)
        self.__invalidateAll()

    def __onProgressionUpdate(self, *_):
        with self.viewModel.transaction() as model:
            model.progressionState.setStatus(defineProgressionStatus(self.getActiveProgression()))
            self.__invalidateProgression(model.progressionState, model.currentProgressionStage)

    @hasDesiredSubMode()
    def __invalidateAll(self, *_):
        with self.viewModel.transaction() as model:
            model.setActiveModeResName(self.getDesiredSubMode().getAssetsPointer())
            model.progressionState.setStatus(defineProgressionStatus(self.getActiveProgression()))
            self.__invalidateProgression(model.progressionState, model.currentProgressionStage)
            self.__invalidateModifiersDomains(model.getModifiersDomains())

    @hasDesiredSubMode()
    def __invalidateModifiersDomains(self, modifiersDomains):
        modifiersDomains.clear()
        modifiersProvider = self.getDesiredSubMode().getModifiersDataProvider()
        domains = modifiersProvider.getDomains() if modifiersProvider else ()
        for domain in domains:
            modifiersDomains.addString(domain)

        modifiersDomains.invalidate()

    @hasActiveProgression()
    def __invalidateProgression(self, state, currStage):
        progression = self.getActiveProgression()
        packProgressionState(progression, state)
        packProgressionActiveStage(progression, currStage)
