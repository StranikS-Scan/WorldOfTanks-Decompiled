# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/ny_gameface_component.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.new_year import InjectWithContext
from gui.impl.backport.backport_pop_over import createPopOverData, BackportPopOverContent
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel as Discount
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_view_model import NyMainViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewTypes, NewYearNavigation
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYViewCtx

@loggerTarget(logKey=NY_LOG_KEYS.NY_CELEBRITY_CHALLENGE, loggerCls=NYLogger)
class NYMainViewGFContent(NewYearHistoryNavigation):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.NYMainViewContent())
        settings.model = NyMainViewModel()
        settings.flags = ViewFlags.COMPONENT
        settings.args = args
        settings.kwargs = kwargs
        super(NYMainViewGFContent, self).__init__(settings)
        self.__currentView = None
        return

    @property
    def viewModel(self):
        return super(NYMainViewGFContent, self).getViewModel()

    @loggerEntry
    def _onLoading(self, ctx=None, *args, **kwargs):
        super(NYMainViewGFContent, self)._onLoading(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        g_eventBus.addListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        if ctx is not None:
            self.__updateView(ctx)
        return

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        g_eventBus.removeListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        super(NYMainViewGFContent, self)._finalize()

    @simpleLog(argsIndex=0, argMap={True: NY_LOG_ACTIONS.NY_DISCOUNT_FROM_SCREEN}, preProcessAction=lambda x: x.getArgument('popoverId') == Discount.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID)
    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == Discount.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID})
                return BackportPopOverContent(popOverData=data)
        return super(NYMainViewGFContent, self).createPopOverContent(event)

    def __onSwitchViewEvent(self, event):
        ctx = event.ctx
        self.__updateView(ctx)

    def __updateView(self, ctx):
        viewParams = ctx.viewParams
        if self.__currentView is not None:
            self.viewModel.setCurrentViewResId(R.invalid())
            self.setChildView(self.__currentView.layoutID, view=None)
            self.__currentView = None
        if viewParams.type != ViewTypes.GAMEFACE:
            return
        else:
            self.__currentView = viewParams.clazz(*ctx.args, **ctx.kwargs)
            self.setChildView(self.__currentView.layoutID, self.__currentView)
            with self.viewModel.transaction() as model:
                model.setCurrentViewResId(self.__currentView.layoutID)
            return

    def __onClose(self):
        NewYearNavigation.closeMainView()


class NYMainViewGFInject(InjectWithContext):
    __slots__ = ()

    def _getInjectViewClass(self):
        return NYMainViewGFContent
