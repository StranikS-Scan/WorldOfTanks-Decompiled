# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/ConfirmBoosterDialog.py
from PlayerEvents import g_playerEvents
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.ConfirmItemWindowMeta import ConfirmItemWindowMeta
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CONFIRM_DIALOG_ALIASES import CONFIRM_DIALOG_ALIASES
from gui.shared.formatters import text_styles, getMoneyVO
DEFAULT_VALUE = 1

class ConfirmBoosterDialog(ConfirmItemWindowMeta):

    def __init__(self, meta, handler):
        super(ConfirmBoosterDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    def submit(self, count, currency):
        self.meta.submit(count, currency)
        self._callHandler(True, self.meta.getBoosterID(), count, currency)
        self.destroy()

    def _populate(self):
        super(ConfirmBoosterDialog, self)._populate()
        g_playerEvents.onShopResync += self.__onShopResync
        self.meta.onInvalidate += self.__makeBoosterData
        self.__makeBoosterData()
        submitBtn, cancelBtn = self.meta.getButtonLabels()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': submitBtn['label'],
         'cancelBtnLabel': cancelBtn['label']})

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onShopResync
        if self.meta is not None:
            self.meta.onInvalidate -= self.__makeBoosterData
            self.meta.destroy()
            self.meta = None
        self.handler = None
        super(ConfirmBoosterDialog, self)._dispose()
        return

    def _callHandler(self, success, *kargs):
        if self.handler is not None:
            self.handler((success, kargs))
        return

    def __onShopResync(self):
        self.__makeBoosterData()

    def __makeBoosterData(self):
        booster = self.meta.getBooster()
        if booster is not None:
            action = self.meta.getActionVO()
            itemPrices = self.meta.getPrices()
            price = itemPrices.getMaxValuesAsMoney()
            self.as_setDataS({'id': self.meta.getBoosterID(),
             'price': getMoneyVO(price),
             'actionPriceData': action,
             'name': booster.userName,
             'description': text_styles.concatStylesToMultiLine(booster.description, booster.getExpiryDateStr()),
             'currency': self.meta.getCurrency(),
             'defaultValue': DEFAULT_VALUE,
             'maxAvailableCount': self.meta.getMaxAvailableItemsCount(),
             'isActionNow': itemPrices.hasAltPrice(),
             'boosterData': self.__makeBoosterVO(booster),
             'linkage': CONFIRM_DIALOG_ALIASES.BOOSTER_ICON})
        else:
            LOG_ERROR("Couldn't find booster with given ID:", self.meta.getBoosterID())
            self.onWindowClose()
        return

    @staticmethod
    def __makeBoosterVO(booster):
        return {'boosterId': booster.boosterID,
         'icon': booster.icon,
         'inCooldown': booster.inCooldown,
         'cooldownPercent': booster.getCooldownAsPercent(),
         'leftTime': booster.getUsageLeftTime(),
         'leftTimeText': booster.getShortLeftTimeStr(),
         'showLeftTime': False,
         'isDischarging': True,
         'isEmpty': False,
         'qualityIconSrc': booster.getQualityIcon(),
         'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
         'isInactive': True}
