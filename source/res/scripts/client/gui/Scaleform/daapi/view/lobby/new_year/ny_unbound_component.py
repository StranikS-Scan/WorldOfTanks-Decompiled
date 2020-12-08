# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/ny_unbound_component.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.new_year import InjectWithContext
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_main_view_model import NewYearMainViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewTypes
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.new_year_collections_tooltip_content import NewYearCollectionsTooltipContent
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYViewCtx

class NYMainViewUBComponent(NewYearHistoryNavigation):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_main_view.NewYearMainView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = NewYearMainViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NYMainViewUBComponent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NYMainViewUBComponent, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        return NewYearCollectionsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_collections_tooltip_content.NYCollectionsTooltipContent() else None

    def _onLoading(self, ctx=None, *args, **kwargs):
        super(NYMainViewUBComponent, self)._onLoading(*args, **kwargs)
        g_eventBus.addListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        if ctx is not None:
            self.__updateView(ctx)
        return

    def _finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        super(NYMainViewUBComponent, self)._finalize()

    def __onSwitchViewEvent(self, event):
        ctx = event.ctx
        self.__updateView(ctx)

    def __updateView(self, ctx):
        viewParams = ctx.viewParams
        if viewParams.type != ViewTypes.UNBOUND:
            self.setChildView(R.dynamic_ids.newYearMainView(), None)
            return
        else:
            view = viewParams.clazz(ctx.tabName, *ctx.args, **ctx.kwargs)
            self.setChildView(R.dynamic_ids.newYearMainView(), view)
            with self.viewModel.transaction() as model:
                model.setCurrentView(viewParams.menuName)
            return


class NYMainViewUBInject(InjectWithContext):
    __slots__ = ()

    def _getInjectViewClass(self):
        return NYMainViewUBComponent
