# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/fun_random/fun_random_hangar_widget_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.FunRandomHangarWidgetMeta import FunRandomHangarWidgetMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.fun_random.fun_random_hangar_widget_view_model import FunRandomHangarWidgetViewModel
from gui.impl.lobby.fun_random.tooltips.fun_random_modifiers_domain_tooltip_view import FunRandomModifiersDomainTooltipView
from gui.impl.lobby.fun_random.tooltips.fun_random_widget_tooltip_view import FunRandomWidgetTooltipView
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showFunRandomInfoPage
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
_logger = logging.getLogger(__name__)

class FunRandomHangarWidgetComponent(FunRandomHangarWidgetMeta):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def _makeInjectView(self):
        return FunRandomHangarWidgetView()

    def _populate(self):
        super(FunRandomHangarWidgetComponent, self)._populate()
        self.__funRandomCtrl.onGameModeStatusUpdated += self.__update
        self.__update()

    def _dispose(self):
        self.__funRandomCtrl.onGameModeStatusUpdated -= self.__update
        super(FunRandomHangarWidgetComponent, self)._dispose()

    def __update(self, *_):
        self.as_setModifiersCountS(len(self.__funRandomCtrl.getModifiersDataProvider().getDomains()))


class FunRandomHangarWidgetView(ViewImpl):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.fun_random.FunRandomHangarWidgetView(), flags=ViewFlags.COMPONENT, model=FunRandomHangarWidgetViewModel())
        super(FunRandomHangarWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomHangarWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.fun_random.tooltips.FunRandomModifiersDomainTooltipView():
            modifiersDomain = event.getArgument('modifiersDomain')
            return FunRandomModifiersDomainTooltipView(modifiersDomain)
        return FunRandomWidgetTooltipView() if contentID == R.views.lobby.fun_random.tooltips.FunRandomWidgetTooltipView() else super(FunRandomHangarWidgetView, self).createToolTipContent(event, contentID)

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
        return ((self.__funRandomCtrl.onUpdated, self.__invalidateAll),)

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
        for domain in self.__funRandomCtrl.getModifiersDataProvider().getDomains():
            modifiersDomains.addString(domain)

        modifiersDomains.invalidate()

    def __onShowInfo(self):
        showFunRandomInfoPage()
