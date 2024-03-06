# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/ConfirmOrderDialogMeta.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.dialogs import IDialogMeta, I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from gui.shared.formatters import text_styles, icons
from web_stubs import i18n

class ConfirmOrderDialogMeta(IDialogMeta):

    def __init__(self, orderID, title, submitBtn, cancelBtn):
        self.__orderID = orderID
        self.__title = title
        self.__submitLabel = submitBtn
        self.__cancelLabel = cancelBtn

    def submit(self, count):
        pass

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG

    def getTitle(self):
        return i18n.makeString(self.__title)

    def getSubmitButtonLabel(self):
        return i18n.makeString(self.__submitLabel)

    def getCancelButtonLabel(self):
        return i18n.makeString(self.__cancelLabel)

    def getOrderID(self):
        return self.__orderID

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT_SCOPE

    def destroy(self):
        pass


class BuyOrderDialogMeta(ConfirmOrderDialogMeta):

    def __init__(self, orderID):
        super(BuyOrderDialogMeta, self).__init__(orderID, DIALOGS.CREATEORDERCONFIRMATION_TITLE, DIALOGS.CREATEORDERCONFIRMATION_SUBMIT, DIALOGS.CREATEORDERCONFIRMATION_CANCEL)


class UnfreezeVehicleDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, playerName, vehicleName, price, balance):
        self.__playerName = playerName
        self.__vehicleName = vehicleName
        self.__price = price
        self.__balance = balance
        super(UnfreezeVehicleDialogMeta, self).__init__('wgshEventUnfreezeVehicle', focusedID=DIALOG_BUTTON_ID.SUBMIT)

    def getMessage(self):
        priceStyle = text_styles.discountSmallText if self.__price <= self.__balance else text_styles.failedStatusText
        return makeHtmlString('html_templates:lobby/dialogs', 'wgshEventUnreezeVehicle', {'first_part': text_styles.leadingText(text_styles.alert(backport.text(R.strings.dialogs.wgshEventUnfreezeVehicle.messagePart.first())), 8),
         'second_part': backport.text(R.strings.dialogs.wgshEventUnfreezeVehicle.messagePart.second(), player_name=text_styles.discountSmallText(self.__playerName)),
         'third_part': text_styles.leadingText(backport.text(R.strings.dialogs.wgshEventUnfreezeVehicle.messagePart.third(), vehicle_name=text_styles.discountSmallText(self.__vehicleName)), 8),
         'fourth_part': backport.text(R.strings.dialogs.wgshEventUnfreezeVehicle.messagePart.fourth(), price=priceStyle(self.__price), balance=text_styles.discountSmallText(self.__balance), icon=icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.wgshSpareParts())))})
