# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/confirm_customization_item_dialog.py
from debug_utils import LOG_ERROR
from PlayerEvents import g_playerEvents
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.ConfirmItemWindowMeta import ConfirmItemWindowMeta
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import Types
from gui.Scaleform.genConsts.CUSTOMIZATION_DIALOGS import CUSTOMIZATION_DIALOGS
from gui.shared.formatters import getMoneyVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION

class CustomizationItemIconWidth(object):
    SMALL = 59
    MEDIUM = 118
    BIG = 161


class ConfirmCustomizationItemDialog(ConfirmItemWindowMeta):

    def __init__(self, meta, handler):
        super(ConfirmCustomizationItemDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def _populate(self):
        super(ConfirmCustomizationItemDialog, self)._populate()
        g_playerEvents.onShopResync += self.__onUpdate
        g_clientUpdateManager.addCallbacks({'stats': self.__onUpdate})
        self._prepareAndSendData()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getSubmitButtonLabel(),
         'cancelBtnLabel': self.meta.getCancelButtonLabel()})

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.meta is not None:
            self.meta.destroy()
            self.meta = None
        self.handler = None
        super(ConfirmCustomizationItemDialog, self)._dispose()
        return

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    def submit(self, count, currency):
        item = self.meta.getItem()
        if self.meta.type == Types.BUY and item.isVehicleBound and not item.isRentable:

            def callback(isOk):
                if isOk:
                    self.proceedSubmit(count, currency)

            DialogsInterface.showI18nConfirmDialog(CUSTOMIZATION_DIALOGS.CUSTOMIZATION_INSTALL_BOUND_RIGHTCLICK_NOTIFICATION, callback)
        else:
            self.proceedSubmit(count, currency)

    def proceedSubmit(self, count, currency):
        item = self.meta.getItem()
        stepFactor = self.meta.getStepFactor(item)
        count = count / stepFactor
        self.meta.submit(item, count, currency)
        self._callHandler(True, item, count, currency)
        self.destroy()

    def _callHandler(self, success, *kargs):
        if self.handler is not None:
            self.handler((success, kargs))
        return

    def _prepareAndSendData(self):
        item = self.meta.getItem()
        if item is not None:
            actualPrices = self.meta.getActualPrices(item)
            defaultPrices = self.meta.getDefaultPrices(item)
            currency = self.meta.getCurrency(item)
            setCurrencies = actualPrices.toSignDict()
            hasAlternativePrice = len(setCurrencies) > 1
            action = None
            if actualPrices != defaultPrices:
                action = self.meta.getActionVO(item)
            iconWidth = iconHeight = CustomizationItemIconWidth.SMALL
            if item.isWide() and item.itemTypeID != GUI_ITEM_TYPE.PROJECTION_DECAL:
                iconWidth = CustomizationItemIconWidth.MEDIUM if item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION or item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER else CustomizationItemIconWidth.BIG
            countLabel = ''
            if item.isRentable and item.rentCount:
                countLabel = VEHICLE_CUSTOMIZATION.CONFIRMITEMDIALOG_COUNTLABEL
            smallSlotVO = {'itemIcon': item.icon,
             'isBgVisible': False,
             'isFrameVisible': True,
             'iconWidth': iconWidth,
             'iconHeight': iconHeight}
            stepFactor = self.meta.getStepFactor(item)
            resultData = {'id': item.intCD,
             'price': getMoneyVO(actualPrices),
             'actionPriceData': action,
             'name': item.userName,
             'description': item.userType,
             'currency': currency,
             'defaultValue': self.meta.getDefaultValue(item) * stepFactor,
             'maxAvailableCount': self.meta.getMaxAvailableItemsCount(item),
             'hasSeveralPrices': hasAlternativePrice,
             'smallSlotVO': smallSlotVO,
             'countLabel': countLabel,
             'stepSize': stepFactor}
            self.as_setDataS(resultData)
        else:
            LOG_ERROR("Couldn't find given customization item: ", self.meta.getItem())
            self.onWindowClose()
        return

    def __onUpdate(self, *_):
        self._prepareAndSendData()
