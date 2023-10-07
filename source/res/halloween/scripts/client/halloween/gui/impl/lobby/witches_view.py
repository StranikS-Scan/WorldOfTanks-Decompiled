# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/witches_view.py
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer, WindowFlags, WindowStatus
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from halloween.gui.impl.gen.view_models.views.lobby.witches_model import WidgetTypeEnum
from halloween.gui.impl.gen.view_models.views.lobby.witches_view_model import WitchesViewModel
from halloween.gui.impl.lobby.base_event_view import BaseEventView
from halloween.gui.impl.lobby.tooltips.crew_tooltip import CrewTooltip
from halloween.gui.impl.lobby.widgets.witches_widget import WitchesWidget
from halloween.gui.shared.event_dispatcher import showMetaView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
_TOP_LAYERS = (WindowLayer.TOP_SUB_VIEW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.WINDOW,
 WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW)

def predicateTopWindow(window):
    return window.typeFlag != WindowFlags.SERVICE_WINDOW and window.typeFlag != WindowFlags.CONTEXT_MENU and window.layer in _TOP_LAYERS and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and not window.isHidden() and not isinstance(window, WindowImpl)


class WitchesView(BaseEventView):
    __slots__ = ('__witchesWidget',)
    layoutID = R.views.halloween.lobby.WitchesView()
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, flags=ViewFlags.VIEW, model=WitchesViewModel())
        super(WitchesView, self).__init__(settings)
        self.__witchesWidget = WitchesWidget(viewModel=self.viewModel.witchesWidget, parentView=WidgetTypeEnum.HANGAR)

    @property
    def viewModel(self):
        return super(WitchesView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if self.hasTopWindow():
            return
        if contentID == R.views.halloween.lobby.tooltips.CrewTooltip():
            phaseIndex = event.getArgument('id')
            return CrewTooltip(phaseIndex=phaseIndex)

    def hasTopWindow(self):
        windows = self.__gui.windowsManager.findWindows(predicateTopWindow)
        return len(windows) > 0

    def _fillViewModel(self):
        super(WitchesView, self)._fillViewModel()
        self.__witchesWidget.updateAll()

    def _subscribe(self):
        self.viewModel.onClick += self.__handleClick
        super(WitchesView, self)._subscribe()

    def _unsubscribe(self):
        self.viewModel.onClick -= self.__handleClick
        super(WitchesView, self)._unsubscribe()

    def _finalize(self):
        self.__witchesWidget.finalize()
        super(WitchesView, self)._finalize()

    def __handleClick(self, args):
        if self.hasTopWindow():
            return
        selectedPhase = int(args.get('phase', 0))
        showMetaView(selectedPhase)
