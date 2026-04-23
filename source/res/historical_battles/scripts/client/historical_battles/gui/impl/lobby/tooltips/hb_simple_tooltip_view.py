# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_simple_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.hb_meta_view_model import TabId

class HbSimpleTooltipView(ViewImpl):
    __slots__ = ('__tab',)
    _RES_ROOT = R.strings.hb_lobby.hbMetaView
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, id):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.HbSimpleTooltipView())
        settings.model = SimpleTooltipContentModel()
        self.__tab = self.__getTabByTabID(id)
        super(HbSimpleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HbSimpleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HbSimpleTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setHeader(self.__getHeader())
            tx.setBody(self.__getBody())

    def __getHeader(self):
        return backport.text(self._RES_ROOT.dyn(self.__tab).tooltip.title())

    def __getBody(self):
        if not self.__gameEventController.isEnabled():
            return ''
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        frontName = backport.text(R.strings.hb_lobby.front.name.capital.dyn(currentFront.getName())())
        return backport.text(self._RES_ROOT.dyn(self.__tab).tooltip.body(), frontName=frontName)

    def __getTabByTabID(self, id):
        if id == TabId.DIVISION:
            return 'division'
        if id == TabId.QUESTS:
            return 'quests'
        return 'order' if id == TabId.ORDER else 'progress'
