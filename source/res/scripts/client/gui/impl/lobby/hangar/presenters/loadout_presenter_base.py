# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/loadout_presenter_base.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
import SoundGroups
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import CONTROLS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.configurations.base import BaseDealPanel
from gui.impl.lobby.tank_setup.interactors.battle_booster import BattleBoosterInteractor
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from gui.impl.lobby.tank_setup.interactors.opt_device import OptDeviceInteractor
from gui.impl.lobby.tank_setup.interactors.shell import ShellInteractor
from gui.impl.lobby.tank_setup.tank_setup_helper import TankSetupAsyncCommandLock
from gui.impl.lobby.tank_setup.tank_setup_sounds import TankSetupSoundEvents
from gui.impl.pub.view_component import ViewComponent
from gui.impl.pub.view_impl import TViewModel
from gui.shared.event_dispatcher import showModuleInfo, showHangar
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Currency
from gui.veh_post_progression.sounds import playSound
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import ITankSetupCMHandler
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ILoadoutController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await, await_callback
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.array_providers.base import BaseArrayProvider
    from gui.impl.lobby.tank_setup.interactors.base import BaseInteractor
    from gui.shared.gui_items.Vehicle import Vehicle

class LoadoutEntityProvider(object):

    def __init__(self, interactingItem, interactorClazz, dataProviderClazzes):
        self.interactor = interactorClazz(interactingItem)
        self.dataProviders = {key:clazz(self.interactor) for key, clazz in dataProviderClazzes.items()}

    def setInteractingItem(self, interactingItem):
        self.interactor.setItem(interactingItem)

    def updateDataProviderItems(self):
        for _, dataProvider in self.dataProviders.items():
            dataProvider.updateItems()

    def clear(self):
        self.dataProviders = None
        self.interactor.clear()
        self.interactor = None
        return


class LoadoutPresenterBase(ViewComponent[TViewModel], ITankSetupCMHandler):
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __gui = dependency.descriptor(IGuiLoader)
    __loadoutController = dependency.descriptor(ILoadoutController)

    def __init__(self, interactingItem, *args, **kwargs):
        self._vehInteractingItem = interactingItem
        self._provider = None
        self._sectionName = ''
        self._slotActions = {}
        self._guiItemType = None
        self._currentSlotIndex = 0
        self._asyncActionLock = TankSetupAsyncCommandLock()
        super(LoadoutPresenterBase, self).__init__(*args, **kwargs)
        return

    def createSlotActions(self):
        return {BaseSetupModel.SWAP_SLOTS_ACTION: partial(self._onSwapSlots, BaseSetupModel.SWAP_SLOTS_ACTION),
         BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION: partial(self._onDragAndDropSlots, BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION),
         BaseSetupModel.REVERT_SLOT_ACTION: self._onRevertItem,
         BaseSetupModel.RETURN_TO_STORAGE_ACTION: self._onRevertItem,
         BaseSetupModel.SELECT_SLOT_ACTION: self.__onSelectItem,
         BaseSetupModel.SHOW_INFO_SLOT_ACTION: self.__onShowItemInfo}

    def getVehicleItem(self):
        return self._interactor

    def sendSlotAction(self, args):
        self._onSlotAction(args)

    def setLastSlotAction(self, *args, **kwargs):
        _, actionType = args
        if actionType == BaseSetupModel.SWAP_SLOTS_ACTION:
            leftID = kwargs['leftID']
            rightID = kwargs['rightID']
            self._swapSlots(leftID, rightID, actionType)
        else:
            self._updateInteractor()
            self._updateDealPanel()
            self._updateModel()

    def getSelectedSetup(self):
        return self._sectionName

    def _getEvents(self):
        return ((self.__loadoutController.onSlotSelected, self.__onSlotSelected),
         (self.__loadoutController.onUpdateFromItem, self.__onUpdateFromItem),
         (self.__loadoutController.onResetItem, self.__onResetItem),
         (self.__loadoutController.onSpecializationSelect, self.__onSpecializationSelect),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.__settingsCore.onSettingsApplied, self.__onSettingsApplied),
         (self.getViewModel().dealPanel.onDealConfirmed, self.__onDealConfirmed),
         (self.getViewModel().dealPanel.onDealCancelled, self.__onDealCancelled),
         (self.getViewModel().dealPanel.onAutoRenewalChanged, self.__onAutoRenewalChanged),
         (self.getViewModel().onSlotAction, self._onSlotAction))

    def _getCallbacks(self):
        return (('stats.{}'.format(Currency.CRYSTAL), self._onCurrencyUpdate), ('stats.{}'.format(Currency.GOLD), self._onCurrencyUpdate), ('stats.{}'.format(Currency.CREDITS), self._onCurrencyUpdate))

    def _onLoading(self, *args, **kwargs):
        self._slotActions = self.createSlotActions()
        for value in self._slotActions.values():
            if not callable(value):
                _logger.error('Slot action call function  %s is not callable', value)

        if self._vehInteractingItem.getItem() is not None:
            self._createProvider(self._vehInteractingItem)
            self._updateInteractor()
            self._updateDealPanel()
            self._updateModel()
        self._vehInteractingItem.onItemUpdated += self.__onItemUpdated
        self._vehInteractingItem.onRevert += self._onRevert
        self._vehInteractingItem.onAcceptComplete += self.__onAcceptComplete
        super(LoadoutPresenterBase, self)._onLoading(*args, **kwargs)
        return

    def _finalize(self):
        super(LoadoutPresenterBase, self)._finalize()
        self._slotActions = {}
        self.__clearInteractor()

    @property
    def _interactor(self):
        return None if not self._provider else self._provider.interactor

    def _getDealPanel(self):
        return BaseDealPanel

    def _updateDealPanel(self):
        if self.getViewModel() is None:
            return
        else:
            currentItems = self._interactor.getChangedList()
            vehicle = self._interactor.getItem()
            self._getDealPanel().updateDealPanelPrice(vehicle, currentItems, self.getViewModel().dealPanel)
            self._getDealPanel().updateAutoRenewalState(self._interactor, self.getViewModel().dealPanel)
            self.getViewModel().dealPanel.setCanAccept(self._interactor.hasChanged())
            return

    def _selectItem(self, slotID, item):
        self._interactor.changeSlotItem(slotID, item)

    def _swapSlots(self, leftID, rightID, actionType):
        if self.__loadoutController.interactor == self._interactor:
            self._interactor.swapSlots(leftID, rightID, actionType)

    def _onSlotAction(self, args):
        actionType = args.pop('actionType')
        actionMethod = self._slotActions.get(actionType)
        if actionMethod is not None:
            actionMethod(args)
        else:
            _logger.error('__slotActions doesnt exist action type : %s(viewName %s)', actionType, self.__class__.__name__)
        return

    def _updateModel(self, recreate=True):
        raise NotImplementedError

    def _createProvider(self, vehInteractingItem):
        raise NotImplementedError

    def _revertItem(self, slotID):
        self._selectItem(slotID, None)
        return

    def _onSwapSlots(self, actionType, args):
        currentSlotId = int(args.get('currentSlotId'))
        installedSlotId = int(args.get('installedSlotId', -1))
        if installedSlotId == -1:
            installedSlotId = self._currentSlotIndex
        self._swapSlots(currentSlotId, installedSlotId, actionType)
        self._updateModel()

    def _onCurrencyUpdate(self, *_):
        self.__update()

    def __clearInteractor(self):
        if self._vehInteractingItem is not None:
            self._vehInteractingItem.onRevert -= self._onRevert
            self._vehInteractingItem.onAcceptComplete -= self.__onAcceptComplete
            self._vehInteractingItem.onItemUpdated -= self.__onItemUpdated
            self._vehInteractingItem = None
            if self._interactor == self.__loadoutController.interactor:
                self.__loadoutController.clearInteractor()
        if self._provider is not None:
            self._provider.clear()
            self._provider = None
        return

    def _onDragAndDropSlots(self, actionType, args):
        leftID = int(args.get('leftID'))
        rightID = int(args.get('rightID'))
        self._swapSlots(leftID, rightID, actionType)
        self._updateModel()

    def _onRevert(self, *args):
        if self._interactor == self.__loadoutController.interactor:
            if isinstance(self._interactor, OptDeviceInteractor):
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.EQUIPMENT_DEMOUNT)
            elif isinstance(self._interactor, BattleBoosterInteractor):
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.INSTRUCTIONS_DEMOUNT)
            elif isinstance(self._interactor, ConsumableInteractor):
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.CONSUMABLES_DEMOUNT)
            elif isinstance(self._interactor, ShellInteractor):
                SoundGroups.g_instance.playSound2D(TankSetupSoundEvents.EQUIPMENT_DEMOUNT)
        self._updateModel()

    def _onRevertItem(self, args):
        slotID = int(args.get('currentSlotId', args.get('installedSlotId', self._currentSlotIndex)))
        self._revertItem(slotID)
        self._updateModel()

    def _updateInteractor(self, item=None):
        if not g_currentVehicle.isPresent():
            return
        item = item or g_currentVehicle.item
        self._interactor.updateFrom(item, self._interactor == self.__loadoutController.interactor)
        self.__update()

    def __onShowItemInfo(self, args):
        itemIntCD = int(args.get('intCD'))
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)

    def __onSelectItem(self, args):
        itemCD = args.get('intCD')
        currentSlotId = int(args.get('currentSlotId', -1))
        if currentSlotId == -1:
            currentSlotId = self._currentSlotIndex
        isAutoSelect = bool(args.get('isAutoSelect', False))
        if not self.__confirmDialogInShowing() or isAutoSelect:
            self._selectItem(currentSlotId, itemCD)

    def __confirmDialogInShowing(self):
        return self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.tanksetup.dialogs.Confirm()) is not None

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            self._updateModel()

    def __onCacheResync(self, reason, diff):
        if reason not in (CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            return
        if diff.get(self._guiItemType, {}):
            self._provider.updateDataProviderItems()
            self._updateModel()
            self._updateDealPanel()

    def __onApply(self, callback, skipDialog=False):
        self._interactor.confirm(callback, skipDialog=skipDialog)

    def __onItemUpdated(self, *_):
        self.__update(recreate=False)

    def __update(self, recreate=True):
        if self._interactor is not None and self._interactor == self.__loadoutController.interactor:
            self._updateDealPanel()
            self._updateModel(recreate)
        return

    @wg_async
    def __onAcceptComplete(self):
        if self._interactor == self.__loadoutController.interactor:
            playSound(TankSetupSoundEvents.ACCEPT)
            yield await_callback(self._interactor.applyAutoRenewal)()
            self._updateModel()
            self._updateDealPanel()

    @wg_async
    def __onDealConfirmed(self, _=None):
        result = yield wg_await(self._asyncActionLock.tryAsyncCommandWithCallback(self.__onApply))
        if result:
            self._interactor.onAcceptComplete()
            showHangar()

    @wg_async
    def __onDealCancelled(self, _=None):
        self._interactor.revert()
        yield await_callback(self._interactor.applyQuit)(skipApplyAutoRenewal=False)

    def __onAutoRenewalChanged(self, args):
        newValue = args.get('value')
        self._interactor.getAutoRenewal().setLocalValue(newValue)
        self._getDealPanel().updateAutoRenewalState(self._interactor, self.getViewModel().dealPanel)

    def __onSlotSelected(self, slotIndex, sectionName, sectionSwitched):
        if sectionName == self._sectionName:
            self._currentSlotIndex = slotIndex
            if sectionSwitched:
                self.__loadoutController.setInteractor(self._interactor)
                self._provider.updateDataProviderItems()
            self._updateDealPanel()
            self._updateModel()

    def __onUpdateFromItem(self, item):
        self._updateInteractor(item)

    def __onResetItem(self):
        if self._vehInteractingItem.getItem() is None or self._provider is None:
            self._createProvider(self._vehInteractingItem)
        self._interactor.setItem(self._vehInteractingItem)
        return

    def __onSpecializationSelect(self):
        if self._interactor == self.__loadoutController.interactor:
            self._updateModel()
