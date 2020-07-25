# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/base.py
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import ContextMenu, CMLabel
from gui.Scaleform.framework.managers.context_menu import CM_BUY_COLOR
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
FIRST_SLOT = 0
SECOND_SLOT = 1
THIRD_SLOT = 2

class TankSetupCMLabel(object):
    DEMOUNT = 'demount'
    DESTROY = 'destroy'
    SELECT = 'select'
    PUT_ON_FIRST = 'putOnFirst'
    PUT_ON_SECOND = 'putOnSecond'
    PUT_ON_THIRD = 'putOnThird'
    TAKE_OFF = 'takeOff'
    UNLOAD = 'unload'
    PUT_ON_LIST = (PUT_ON_FIRST, PUT_ON_SECOND, PUT_ON_THIRD)


class BaseTankSetupContextMenu(ContextMenu):
    _gui = dependency.descriptor(IGuiLoader)
    _itemsCache = dependency.descriptor(IItemsCache)

    def _sendSlotAction(self, actionType, **kwargs):
        view = self._getEmitterView()
        if view is None or self._slotType != view.getSelectedSetup():
            return
        else:
            actionArgs = {'actionType': actionType,
             'intCD': kwargs.get('intCD', self._intCD),
             'installedSlotId': kwargs.get('installedSlotId', self._installedSlotId)}
            if 'currentSlotId' in kwargs:
                actionArgs['currentSlotId'] = kwargs['currentSlotId']
            view.sendSlotAction(actionArgs)
            return

    def _sendLastSlotAction(self, setupName, actionType, kwargs):
        view = self._getEmitterView()
        if view is None:
            return
        else:
            view.setLastSlotAction(setupName, actionType, **kwargs)
            return

    def _initFlashValues(self, ctx):
        self.__emitterUID = ctx.emitterUID
        self._intCD = int(ctx.intCD)
        self._slotType = ctx.slotType
        self._installedSlotId = int(ctx.installedSlotId)
        self._isMounted = ctx.isMounted
        self._slotsCount = 1

    def _getEmitterView(self):
        return self._gui.windowsManager.getView(self.__emitterUID)

    def _getVehicle(self):
        return self._getEmitterView().getVehicleItem().getItem()

    def _getCopyVehicle(self):
        return self._itemsCache.items.getVehicleCopy(self._getVehicle())

    def _getItem(self):
        return self._itemsCache.items.getItemByCD(self._intCD)

    def _getOptionCustomData(self, label):
        optionData = super(BaseTankSetupContextMenu, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            money, exchangeRate = self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate
            item = self._itemsCache.items.getItemByCD(self._intCD)
            isEnough = item.mayPurchaseWithExchange(money, exchangeRate)
            optionData.textColor = CM_BUY_COLOR
            optionData.enabled = isEnough
        return optionData

    def _isVisible(self, label):
        if label == TankSetupCMLabel.PUT_ON_FIRST:
            return self._slotsCount > 1 and self._installedSlotId != FIRST_SLOT
        if label == TankSetupCMLabel.PUT_ON_SECOND:
            return self._slotsCount > 1 and self._installedSlotId != SECOND_SLOT
        return self._slotsCount > 2 and self._installedSlotId != THIRD_SLOT if label == TankSetupCMLabel.PUT_ON_THIRD else super(BaseTankSetupContextMenu, self)._isVisible(label)


class BaseItemContextMenu(BaseTankSetupContextMenu):

    def _sendPutOnSlotAction(self, onId):
        self._sendSlotAction(BaseSetupModel.SELECT_SLOT_ACTION, currentSlotId=onId)

    def _initFlashValues(self, ctx):
        super(BaseItemContextMenu, self)._initFlashValues(ctx)
        self._isDisabled = ctx.isDisabled

    def _getOptionCustomData(self, label):
        optionData = super(BaseItemContextMenu, self)._getOptionCustomData(label)
        if label == TankSetupCMLabel.SELECT or label in TankSetupCMLabel.PUT_ON_LIST:
            optionData.enabled = not self._isDisabled
        return optionData

    def _isVisible(self, label):
        return self._slotsCount == 1 and self._installedSlotId == NONE_ID if label == TankSetupCMLabel.SELECT else super(BaseItemContextMenu, self)._isVisible(label)


class BaseSlotContextMenu(BaseTankSetupContextMenu):

    def _sendPutOnSlotAction(self, onId):
        self._sendSlotAction(BaseSetupModel.SWAP_SLOTS_ACTION, currentSlotId=onId)

    def _isItemInInventory(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        return item.isInInventory

    def _isVisible(self, label):
        if label == TankSetupCMLabel.TAKE_OFF:
            return not self._isMounted and not self._isItemInInventory()
        return self._isMounted or self._isItemInInventory() if label == TankSetupCMLabel.UNLOAD else super(BaseSlotContextMenu, self)._isVisible(label)
