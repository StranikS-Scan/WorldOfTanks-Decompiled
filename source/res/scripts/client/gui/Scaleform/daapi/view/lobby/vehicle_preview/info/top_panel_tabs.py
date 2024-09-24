# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/top_panel_tabs.py
import logging
import typing
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import Array, ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.VehiclePreviewTopPanelTabsMeta import VehiclePreviewTopPanelTabsMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID, TopPanelTabsModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showStylePreview, showVehiclePreviewWithoutBottomPanel
from shared_utils import first
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Tuple
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)
_TAB_COMMAND = {TabID.VEHICLE: showVehiclePreviewWithoutBottomPanel,
 TabID.STYLE: showStylePreview}
_TAB_CUSTOM_NAME_GETTER = {TabID.STYLE: lambda style: style.userName if style is not None else ''}
PERSONAL_NUMBER_STYLE_TABS = (TabID.PERSONAL_NUMBER_VEHICLE, TabID.BASE_VEHICLE)

class VehiclePreviewTopPanelTabs(VehiclePreviewTopPanelTabsMeta):

    def __init__(self):
        super(VehiclePreviewTopPanelTabs, self).__init__()
        self.__view = None
        return

    def setData(self, **kwargs):
        self.__view.setData(kwargs.get('tabIDs'), kwargs.get('currentTabID'), kwargs.get('style'))

    def setParentCtx(self, **kwargs):
        self.__view.setParentCtx(**kwargs)

    def _makeInjectView(self, *args):
        self.__view = VehiclePreviewTopPanelTabsView()
        return self.__view


class VehiclePreviewTopPanelTabsView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.top_panel.TopPanelTabs())
        settings.flags = ViewFlags.VIEW
        settings.model = TopPanelTabsModel()
        super(VehiclePreviewTopPanelTabsView, self).__init__(settings)
        self.__parentCtx = {}
        self.__tabIDs = tuple()
        self.__currentTabID = None
        self.__style = None
        return

    @property
    def viewModel(self):
        return super(VehiclePreviewTopPanelTabsView, self).getViewModel()

    def setData(self, tabIDs, currentTabID, style):
        self.__tabIDs = tabIDs
        self.__currentTabID = currentTabID
        self.__style = style

    def setParentCtx(self, **kwargs):
        self.__parentCtx = kwargs

    def _getEvents(self):
        return ((self.viewModel.onTabChanged, self.__onTabChanged),)

    def _onLoaded(self, *args, **kwargs):
        self.__updateVMData()

    def __updateVMData(self, *_):
        with self.viewModel.transaction() as tx:
            tabIDs = Array()
            tabNames = Array()
            for tabID in self.__tabIDs:
                tabIDs.addNumber(tabID.value)
                getTabName = _TAB_CUSTOM_NAME_GETTER.get(tabID)
                tabNames.addString(getTabName(self.__style) if callable(getTabName) else '')

            tx.setTabIDs(tabIDs)
            tx.setTabCustomNames(tabNames)
            tx.setCurrentTabID(self.__currentTabID)

    def __onTabChanged(self, *args, **kwargs):
        self.__currentTabID = TabID(first(args).get('selectedTab'))
        self.viewModel.setCurrentTabID(self.__currentTabID)
        command = _TAB_COMMAND.get(self.__currentTabID)
        if callable(command):
            backCallback = self.__parentCtx.get('backCallback') or self.__parentCtx.get('previewBackCb')
            commandCtx = self.__getBackBtnLabel()
            command(self.__parentCtx.get('itemCD'), style=(self.__style if self.__currentTabID == TabID.STYLE else None), topPanelData=self.__makeTopPanelData(), itemsPack=self.__parentCtx.get('itemsPack'), backCallback=backCallback, **commandCtx)
        elif self.__currentTabID in PERSONAL_NUMBER_STYLE_TABS:
            self.__processPersonalNumberStyleTab()
        return

    def __makeTopPanelData(self):
        return {'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
         'tabIDs': self.__tabIDs,
         'currentTabID': self.__currentTabID,
         'style': self.__style}

    def __processPersonalNumberStyleTab(self):
        style = self.__parentCtx.get('numberStyle') if self.__currentTabID == TabID.PERSONAL_NUMBER_VEHICLE else None
        g_currentPreviewVehicle.selectNoVehicle()
        g_currentPreviewVehicle.selectVehicle(self.__parentCtx.get('itemCD'), style=style)
        return

    def __getBackBtnLabel(self):
        backBtnLabel = self.__parentCtx.get('backBtnLabel') or self.__parentCtx.get('backBtnDescrLabel')
        if backBtnLabel is not None and backBtnLabel:
            if self.__currentTabID == TabID.STYLE:
                return {'backBtnDescrLabel': backBtnLabel}
            if self.__currentTabID == TabID.VEHICLE:
                return {'backBtnLabel': backBtnLabel}
        return {}
