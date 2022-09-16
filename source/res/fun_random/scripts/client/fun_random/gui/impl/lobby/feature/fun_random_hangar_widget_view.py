# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_hangar_widget_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_hangar_widget_view_model import FunRandomHangarWidgetViewModel
from fun_random.gui.impl.lobby.tooltips.fun_random_widget_tooltip_view import FunRandomWidgetTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_domain_tooltip_view import FunRandomDomainTooltipView
from fun_random.gui.shared.event_dispatcher import showFunRandomInfoPage
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
_logger = logging.getLogger(__name__)

class FunRandomHangarWidgetView(ViewImpl):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.feature.FunRandomHangarWidgetView(), flags=ViewFlags.COMPONENT, model=FunRandomHangarWidgetViewModel())
        super(FunRandomHangarWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomHangarWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView():
            modifiersDomain = event.getArgument('modifiersDomain')
            return FunRandomDomainTooltipView(modifiersDomain)
        return FunRandomWidgetTooltipView() if contentID == R.views.fun_random.lobby.tooltips.FunRandomWidgetTooltipView() else super(FunRandomHangarWidgetView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(FunRandomHangarWidgetView, self)._initialize()
        self.viewModel.onShowInfo += self.__onShowInfo

    def _finalize(self):
        self.viewModel.onShowInfo -= self.__onShowInfo
        super(FunRandomHangarWidgetView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomHangarWidgetView, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    def _getEvents(self):
        return ((self.__funRandomCtrl.onGameModeStatusUpdated, self.__invalidateAll),)

    def __invalidateAll(self, *_):
        currentSeason = self.__funRandomCtrl.getCurrentSeason()
        if currentSeason is None:
            _logger.error('Invalid active season of Fun Random mode is found')
            return
        else:
            with self.viewModel.transaction() as model:
                model.setActiveModeName(currentSeason.getUserName())
                self.__invalidateModifiersDomains(model.getModifiersDomains())
            return

    def __invalidateModifiersDomains(self, modifiersDomains):
        modifiersDomains.clear()
        modifiersProvider = self.__funRandomCtrl.getModifiersDataProvider()
        domains = modifiersProvider.getDomains() if modifiersProvider else ()
        for domain in domains:
            modifiersDomains.addString(domain)

        modifiersDomains.invalidate()

    def __onShowInfo(self):
        showFunRandomInfoPage()
