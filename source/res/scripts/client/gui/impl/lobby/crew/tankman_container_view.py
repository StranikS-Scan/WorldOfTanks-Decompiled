# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tankman_container_view.py
import typing
from collections import OrderedDict
import Event
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from account_helpers import AccountSettings
from base_crew_view import BaseCrewView, IS_FROM_ESCAPE_PARAM
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tankman_container_tab_model import TankmanContainerTabModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_container_view_model import TankmanContainerViewModel
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from gui.impl.lobby.crew.personal_case.personal_data_view import PersonalDataView
from gui.impl.lobby.crew.container_vews.personal_file.personal_file_view import PersonalFileView
from gui.impl.lobby.crew.container_vews.service_record.service_record_view import ServiceRecordView
from gui.impl.lobby.crew.widget.crew_widget import NO_TANKMAN
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import VehicleSkillPreviewParamsView
from gui.shared.event_dispatcher import showChangeCrewMember
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from nations import NAMES
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewMetricsLoggerWithParent
from uilogging.crew.logging_constants import CrewViewKeys, LAYOUT_ID_TO_ITEM, CrewNavigationButtons, TABS_LOGGING_KEYS
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class TabsId(object):
    PERSONAL_FILE = R.views.lobby.crew.personal_case.PersonalFileView()
    PERSONAL_DATA = R.views.lobby.crew.personal_case.PersonalDataView()
    SERVICE_RECORD = R.views.lobby.crew.personal_case.ServiceRecordView()
    ALL = [PERSONAL_FILE, PERSONAL_DATA, SERVICE_RECORD]
    DEFAULT = PERSONAL_FILE


TABS = OrderedDict([(TabsId.PERSONAL_FILE, PersonalFileView), (TabsId.PERSONAL_DATA, PersonalDataView), (TabsId.SERVICE_RECORD, ServiceRecordView)])

class TankmanContainerView(BaseCrewView):
    __slots__ = ('_tankmanInvID', 'vehicleID', '_activeTab', '_createdTabs', '_isAnimationEnabled', 'paramsView', 'onTabChanged', '_isContentHidden')
    itemsCache = dependency.descriptor(IItemsCache)
    gui = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=TankmanContainerViewModel(), kwargs=kwargs)
        super(TankmanContainerView, self).__init__(settings)
        tankmanInvID = kwargs.get('tankmanInvID', NO_TANKMAN)
        currentViewID = kwargs.get('currentViewID', None)
        self._activeTab = currentViewID if currentViewID in TabsId.ALL else TabsId.DEFAULT
        self._tankmanInvID = tankmanInvID
        self.vehicleID = self.itemsCache.items.getTankman(tankmanInvID).vehicleInvID
        self.onTabChanged = Event.Event()
        self._createdTabs = []
        self._isAnimationEnabled = False
        self.paramsView = None
        self._uiLogger = CrewMetricsLoggerWithParent()
        self._isContentVisible = True
        return

    def updateTankmanId(self, tankmanInvID):
        self.__selectTankman(tankmanInvID)

    def updateTabId(self, tabID):
        self.__changeTab(tabID)

    def updateTTCWithSkillName(self, skillName):
        self.paramsView.updateForSkill([skillName] if skillName is not None else [])
        return

    @property
    def viewModel(self):
        return super(TankmanContainerView, self).getViewModel()

    @property
    def currentTabId(self):
        return self._activeTab

    def onBringToFront(self, otherWindow):
        tab = self.getChildView(self._activeTab)
        if isinstance(tab, BasePersonalCaseView):
            tab.uiLogger.onBringToFront(otherWindow)

    def toggleContentVisibility(self, isVisible):
        self._isContentVisible = isVisible
        self.viewModel.setIsContentVisible(isVisible)

    def setAnimationInProgress(self, isEnabled):
        self._isAnimationEnabled = isEnabled

    def _onEmptySlotAutoSelect(self, _):
        self.destroyWindow()

    def _setWidgets(self, **kwargs):
        super(TankmanContainerView, self)._setWidgets(**kwargs)
        self.paramsView = VehicleSkillPreviewParamsView()
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self.paramsView)

    def _onLoading(self, *args, **kwargs):
        super(TankmanContainerView, self)._onLoading(*args, **kwargs)
        self.__createTab(self._activeTab, LAYOUT_ID_TO_ITEM.get(self._previousViewID))
        self._uiLogger.setParentViewKey(LAYOUT_ID_TO_ITEM.get(self._activeTab))

    def _fillViewModel(self, vm):
        super(TankmanContainerView, self)._fillViewModel(vm)
        tankman = self.itemsCache.items.getTankman(self._tankmanInvID)
        nation = NAMES[tankman.nationID]
        tabs = vm.getTabs()
        vm.setCurrentTabId(self._activeTab)
        vm.setNation(nation)
        for resId, viewCls in TABS.iteritems():
            tabModel = TankmanContainerTabModel()
            tabModel.setId(resId)
            tabModel.setTitle(viewCls.TITLE)
            if resId == TabsId.PERSONAL_DATA:
                tabModel.setCounter(self.__getNewSkinsAmount())
            tabs.addViewModel(tabModel)

        tabs.invalidate()
        if tankman.isInTank:
            vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
            fillVehicleInfo(vm.vehicleInfo, vehicle, separateIGRTag=True)

    def _setBackButtonLabel(self, vm):
        vm.setBackButtonLabel(R.strings.crew.common.navigation.toBarracks() if not self._isHangar else R.invalid())

    def _getEvents(self):
        eventsTuple = super(TankmanContainerView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onTabChange, self._onTabChange), (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging))

    def _getCallbacks(self):
        return (('inventory.13', self._onSkinsUpdate),)

    def _finalize(self):
        super(TankmanContainerView, self)._finalize()
        self.paramsView = None
        return

    def _onClose(self, params=None):
        if not self._isContentVisible:
            return
        if self._isAnimationEnabled and isinstance(params, dict) and params.get(IS_FROM_ESCAPE_PARAM, False):
            self.__stopAnimations()
            return
        self._logClose(params)
        self._destroySubViews()

    def _onBack(self, logClick=True):
        self._destroySubViews()
        if logClick:
            self._uiLogger.logNavigationButtonClick(CrewNavigationButtons.TO_BARRACKS)

    def _onFocus(self, focused):
        tab = self.getChildView(self._activeTab)
        tab._onFocus(focused)

    def _onTabChange(self, args):
        self.__changeTab(int(args.get('tabId', TabsId.DEFAULT)))

    def _onTankmanSlotAutoSelect(self, tankmanInvID, slotIdx):
        self.__selectTankman(tankmanInvID)

    def _onTankmanSlotClick(self, tankmanInvID, _):
        self.__selectTankman(tankmanInvID)

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        showChangeCrewMember(slotIdx, self.vehicleID, self._activeTab)

    def _onSkinsUpdate(self, _):
        self.__updateNewSkinsCounter()

    def __onAccountSettingsChanging(self, key, _):
        if key == CREW_SKINS_VIEWED:
            self.__updateNewSkinsCounter()

    def __updateNewSkinsCounter(self):
        with self.viewModel.transaction() as vm:
            tabs = vm.getTabs()
            for tab in tabs:
                if tab.getId() == TabsId.PERSONAL_DATA:
                    tab.setCounter(self.__getNewSkinsAmount())
                    tabs.invalidate()
                    break

    def __getNewSkinsAmount(self):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        amount = 0
        for item in items.itervalues():
            amount += item.getNewCount()

        return amount

    def __selectTankman(self, tankmanInvID):
        self._tankmanInvID = tankmanInvID
        vehicle = self.itemsCache.items.getTankman(tankmanInvID)
        if not vehicle:
            return
        self.vehicleID = vehicle.vehicleInvID
        self.__updateTabs(tankmanInvID)
        self._crewWidget.updateTankmanId(tankmanInvID)

    def __changeTab(self, tabID):
        if tabID == self._activeTab:
            return
        self._uiLogger.setParentViewKey(LAYOUT_ID_TO_ITEM.get(tabID))
        self._uiLogger.logClick(TABS_LOGGING_KEYS.get(tabID, CrewViewKeys.HANGAR), CrewViewKeys.PERSONAL_FILE)
        self.__stopAnimations()
        self.__createTab(tabID, LAYOUT_ID_TO_ITEM.get(self._activeTab))
        with self.viewModel.transaction() as vm:
            vm.setCurrentTabId(tabID)
        self.onTabChanged(tabID, prevTabKey=LAYOUT_ID_TO_ITEM.get(self._activeTab))
        self._activeTab = tabID
        self._crewWidget.setCurrentViewID(tabID)

    def __updateTabs(self, tankmanInvID):
        for tabId in TabsId.ALL:
            tab = self.getChildView(tabId)
            if isinstance(tab, IPersonalTab):
                tab.onChangeTankman(tankmanInvID)

    def __stopAnimations(self):
        self._isAnimationEnabled = False
        tab = self.getChildView(self._activeTab)
        if isinstance(tab, IPersonalTab):
            tab.onStopAnimations()

    def __createTab(self, tabId, parentViewKey=None):
        if tabId in self._createdTabs:
            return
        viewCls = TABS[tabId]
        self.setChildView(tabId, viewCls(parentView=self, tankmanID=self._tankmanInvID, parentViewKey=parentViewKey))
        self._createdTabs.append(tabId)
