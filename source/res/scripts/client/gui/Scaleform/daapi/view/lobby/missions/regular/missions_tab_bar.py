# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_tab_bar.py
import logging
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.side_bar_tab_model import SideBarTabModel
from gui.impl.gen.view_models.views.missions.missions_tab_bar_view_model import MissionsTabBarViewModel
from gui.impl.pub import ViewImpl
from helpers.i18n import makeString as _ms
_logger = logging.getLogger(__name__)

class MissionsTabBarComponent(InjectComponentAdaptor):

    def setTabs(self, tabs):
        if self._injectView:
            self._injectView.setTabs(tabs)

    def setOnTabSelectionChangedCallback(self, callback):
        if self._injectView:
            self._injectView.setOnTabSelectionChangedCallback(callback)

    def _makeInjectView(self):
        return MissionsTabBarView()


class MissionsTabBarView(ViewImpl):
    __slots__ = ('__tabsData', '__onTabSelectionChangedCallback')

    def __init__(self, *args, **kwargs):
        super(MissionsTabBarView, self).__init__(R.views.lobby.missions.missions_tab_bar_view.MissionsTabBarView(), ViewFlags.VIEW, MissionsTabBarViewModel, *args, **kwargs)
        self.__tabsData = []
        self.__onTabSelectionChangedCallback = None
        return

    @property
    def viewModel(self):
        return super(MissionsTabBarView, self).getViewModel()

    def setTabs(self, tabs):
        self.__tabsData = tabs
        i = 0
        with self.viewModel.transaction() as model:
            views = model.getViews()
            views.clear()
            for tabData in tabs:
                viewModel = SideBarTabModel()
                viewModel.setAlias(tabData['alias'])
                viewModel.setIcon(tabData['icon'])
                viewModel.setLinkage(tabData['linkage'])
                viewModel.setTooltipHeader(_ms(tabData['tooltip'] + '/header'))
                viewModel.setTooltipBody(_ms(tabData['tooltip'] + '/body'))
                viewModel.setUnseenCount(tabData['unseenCount'])
                viewModel.setEnabled(tabData['enabled'])
                if tabData['selected']:
                    model.setStartIndex(i)
                views.addViewModel(viewModel)
                i += 1

            views.invalidate()

    def setOnTabSelectionChangedCallback(self, callback):
        self.__onTabSelectionChangedCallback = callback

    def _initialize(self):
        super(MissionsTabBarView, self)._initialize()
        self.viewModel.onTabSelectionChanged += self.__onTabSelectionChanged

    def _finalize(self):
        super(MissionsTabBarView, self)._finalize()
        self.viewModel.onTabSelectionChanged -= self.__onTabSelectionChanged
        self.__onTabSelectionChangedCallback = None
        return

    def __onTabSelectionChanged(self, args=None):
        index = int(args['index'])
        if index <= len(self.__tabsData):
            tabData = self.__tabsData[index]
            if tabData is not None:
                if self.__onTabSelectionChangedCallback:
                    self.__onTabSelectionChangedCallback(tabData['alias'], tabData['linkage'], tabData['prefix'])
        else:
            _logger.error('Invalid tab index selected %d', index)
        return
