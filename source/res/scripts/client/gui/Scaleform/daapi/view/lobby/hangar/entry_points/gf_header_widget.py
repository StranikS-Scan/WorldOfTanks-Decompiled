# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/entry_points/gf_header_widget.py
from collections import namedtuple
from Event import Event, EventManager
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.meta.GFHeaderWidgetMeta import GFHeaderWidgetMeta
from gui.impl.gen.view_models.views.lobby.hangar.header_widget_view_model import HeaderWidgetViewModel
GFWidgetAliases = namedtuple('GFWidgetAliases', ['flashLinkage', 'registerAlias'])

class GFHeaderWidget(GFHeaderWidgetMeta):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(GFHeaderWidget, self).__init__()

    def _makeInjectView(self):
        raise NotImplementedError('The method must return a View inherited from GFHeaderWidgetView')

    def _onPopulate(self):
        super(GFHeaderWidget, self)._onPopulate()
        self._addViewListeners()

    def _dispose(self):
        self._removeViewListeners()
        super(GFHeaderWidget, self)._dispose()

    def _addViewListeners(self):
        view = self.getInjectView()
        if view:
            view.onChangeLayout += self._onChangeLayout

    def _removeViewListeners(self):
        view = self.getInjectView()
        if view:
            view.onChangeLayout -= self._onChangeLayout

    def _onChangeLayout(self, top, right, left):
        self.as_updateMarginsS(top, right, left)


class GFHeaderWidgetView(ViewImpl):
    __slots__ = ('_eManager', 'onChangeLayout')

    def __init__(self, layoutID, model, *args, **kwargs):
        super(GFHeaderWidgetView, self).__init__(ViewSettings(layoutID=layoutID, model=model))
        self._eManager = EventManager()
        self.onChangeLayout = Event(self._eManager)

    def _getEvents(self):
        return ((self.getViewModel().onChangeLayout, self._onChangeLayout),)

    def _finalize(self):
        self._eManager.clear()
        super(GFHeaderWidgetView, self)._finalize()

    def _onChangeLayout(self, args):
        top = args.get(HeaderWidgetViewModel.ARG_TOP, 0)
        right = args.get(HeaderWidgetViewModel.ARG_RIGHT, 0)
        left = args.get(HeaderWidgetViewModel.ARG_LEFT, 0)
        self.onChangeLayout(top, right, left)
