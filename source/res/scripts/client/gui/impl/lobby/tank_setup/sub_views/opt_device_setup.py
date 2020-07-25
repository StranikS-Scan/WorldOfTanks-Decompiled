# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/opt_device_setup.py
from functools import partial
from BWUtil import AsyncReturn
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async, await
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabsController, OptDeviceSelectedFilters, getOptDeviceTabByItem, OptDeviceIntroductionController, OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from helpers import dependency
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore

class OptDeviceSetupSubView(BaseEquipmentSetupSubView):
    __slots__ = ('__hintController',)

    def __init__(self, *args, **kwargs):
        super(OptDeviceSetupSubView, self).__init__(*args, **kwargs)
        self.__hintController = OptDeviceHintController()

    def onLoading(self, currentSlotID, *args, **kwargs):
        self.__hintController.init(self._viewModel)
        super(OptDeviceSetupSubView, self).onLoading(currentSlotID, *args, **kwargs)

    def updateSlots(self, slotID, fullUpdate=True):
        if fullUpdate:
            self._filter.resetFilters(self._viewModel.filter)
        item = self._interactor.getCurrentLayout()[slotID]
        if item is not None:
            tabName = getOptDeviceTabByItem(item)
            if self._currentTabName != tabName:
                self._setTab(tabName)
                fullUpdate = True
        self.__hintController.updateSlots(self._interactor.getCurrentCategories(slotID))
        super(OptDeviceSetupSubView, self).updateSlots(slotID, fullUpdate)
        return

    def revertItem(self, slotID):
        self._selectItem(slotID, None)
        return

    @async
    def canQuit(self):
        result = yield super(OptDeviceSetupSubView, self).canQuit()
        if result:
            self.__hintController.quit(self._viewModel)
        raise AsyncReturn(result)

    def _createTabsController(self):
        return OptDeviceTabsController()

    def _createFilter(self):
        return OptDeviceSelectedFilters()

    def _addListeners(self):
        super(OptDeviceSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.DEMOUNT_SLOT_ACTION, self.__onDemountItem)
        self._addSlotAction(BaseSetupModel.DESTROY_SLOT_ACTION, partial(self.__onDemountItem, isDestroy=True))
        self._addSlotAction(BaseSetupModel.UPGRADE_SLOT_ACTION, self.__onUpgradeItem)
        self._viewModel.onIntroPassed += self._onIntroPassed

    def _removeListeners(self):
        super(OptDeviceSetupSubView, self)._removeListeners()
        self._viewModel.onIntroPassed -= self._onIntroPassed

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            super(OptDeviceSetupSubView, self)._setTab(tabName)
            self._introductionUpdate(tabName)

    def _onFilterChanged(self, args):
        self.__hintController.filterChanged(self._viewModel, args.get('name'))
        super(OptDeviceSetupSubView, self)._onFilterChanged(args)

    def _updateItemByFilter(self):
        if self._currentTabName == OptDeviceTabs.SIMPLE:
            super(OptDeviceSetupSubView, self)._updateItemByFilter()
        if self._filter is not None:
            self.__hintController.updateItemByFilter(self._viewModel, self._interactor.getCurrentCategories(self._curSlotID), self._currentTabName)
        return

    @async
    def _selectItem(self, slotID, item):
        yield await(self._asyncActionLock.tryAsyncCommand(self._interactor.changeSlotItem, slotID, item))
        self.update()

    def _introductionUpdate(self, tabName):
        introduction = OptDeviceIntroductionController.getIntroduction(tabName)
        self._viewModel.setIntroductionType(introduction or '')
        self._viewModel.setWithIntroduction(introduction is not None)
        if not introduction:
            self._updateTabs()
        return

    def _onIntroPassed(self):
        OptDeviceIntroductionController.setIntroductionValue(self._viewModel.getIntroductionType())
        self._introductionUpdate(self._currentTabName)

    @async
    def __onDemountItem(self, args, isDestroy=False):
        itemIntCD = int(args.get('intCD'))
        yield await(self._asyncActionLock.tryAsyncCommand(self._interactor.demountItem, itemIntCD, isDestroy))
        self.update()

    @async
    def __onUpgradeItem(self, args):
        itemIntCD = int(args['intCD'])
        result = yield await(self._asyncActionLock.tryAsyncCommandWithCallback(self._interactor.upgradeModule, itemIntCD))
        if result:
            self.update(fullUpdate=True)


class OptDeviceHintController(object):
    __slots__ = ('__specHintEnabled',)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__specHintEnabled = False

    def init(self, viewModel):
        self.__specHintEnabled = not self._settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.AMMUNITION_FILTER_HINT, default=False)
        if self.__specHintEnabled:
            viewModel.hints.addHintModel(TutorialHintConsts.AMMUNITION_FILTER_HINT_MC)

    def quit(self, viewModel):
        if viewModel and self.__specHintEnabled:
            viewModel.filter.setSpecializationHintEnabled('')
            self.__hideFilterHint()

    def updateSlots(self, categories):
        if self.__specHintEnabled and categories:
            self._settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.AMMUNITION_PANEL_HINT: True})

    def filterChanged(self, viewModel, filterName):
        if self.__specHintEnabled and viewModel.filter.getSpecializationHintEnabled() == filterName:
            self.__specHintEnabled = False
            self._settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.AMMUNITION_FILTER_HINT: True})
            viewModel.filter.setSpecializationHintEnabled('')
            viewModel.hints.delHintModel(TutorialHintConsts.AMMUNITION_FILTER_HINT_MC)

    def updateItemByFilter(self, viewModel, currentCategories, tabName):
        if not self.__specHintEnabled:
            return
        specHintName = viewModel.filter.getSpecializationHintEnabled()
        if tabName == OptDeviceTabs.SIMPLE:
            newSpecHintName = first(currentCategories, default='')
        else:
            newSpecHintName = ''
        if specHintName and not newSpecHintName:
            self.__hideFilterHint()
        viewModel.filter.setSpecializationHintEnabled(newSpecHintName)

    @staticmethod
    def __hideFilterHint():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.AMMUNITION_FILTER_HINT_MC}), EVENT_BUS_SCOPE.LOBBY)
