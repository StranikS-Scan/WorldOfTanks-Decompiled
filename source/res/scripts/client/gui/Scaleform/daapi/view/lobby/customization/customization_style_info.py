# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_style_info.py
from collections import namedtuple
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.customization.shared import getPurchaseMoneyState, isTransactionValid
from gui.Scaleform.daapi.view.meta.CustomizationStyleInfoMeta import CustomizationStyleInfoMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.gui_items.customization.c11n_items import STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
StyleInfoVO = namedtuple('StyleInfoVO', ('styleType', 'styleName', 'styleInfoText'))
BuyBtnVO = namedtuple('BuyBtnVO', ('enabled', 'label', 'disabledTooltip'))
StylePriceVO = namedtuple('StylePriceVO', ('isEnoughMoney', 'rentalInfo', 'buyBtnVO', 'itemPriceVO'))

class CustomizationStyleInfo(CustomizationStyleInfoMeta):
    service = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(CustomizationStyleInfo, self).__init__()
        self.__ctx = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()

    def _dispose(self):
        self.__ctx = None
        return

    def show(self):
        style = self.__ctx.modifiedStyle
        if style is None:
            return
        else:
            styleInfoVO = self.__makeStyleInfoVO(style)
            self.as_setStyleInfoS(styleInfoVO)
            stylePriceVO = self.__makeStylePriceVO(style)
            self.as_setStylePriceS(stylePriceVO)
            self.as_showS()
            return

    def onClose(self):
        self.__ctx.onStyleInfoHidden(resumeHighlighter=True)

    def onApply(self):
        self.__ctx.onStyleInfoHidden(resumeHighlighter=False)

    def hide(self):
        self.as_hideS()

    def __makeStyleInfoVO(self, style):
        styleType = text_styles.promoSubTitle(_ms(STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP[style.groupID]))
        styleName = text_styles.epicTitleYellow(style.userName)
        styleInfoText = self.__ctx.getItemFromSelectedRegion().textInfo
        styleInfoText = text_styles.mainBig(styleInfoText)
        return StyleInfoVO(styleType=styleType, styleName=styleName, styleInfoText=styleInfoText)._asdict()

    def __makeStylePriceVO(self, style):
        validTransaction = False
        rentalInfoText = ''
        buyBtnVO = itemPriceVO = None
        stylePrice = style.getBuyPrice()
        outfitsModified = self.__ctx.isOutfitsModified()
        if outfitsModified:
            isFromInventory = self.__ctx.getPurchaseItems()[0].isFromInventory
            moneyState = getPurchaseMoneyState(stylePrice.price)
            validTransaction = isTransactionValid(moneyState, stylePrice.price)
            if style.isRentable:
                rentalInfoText = text_styles.main(_ms(VEHICLE_CUSTOMIZATION.CAROUSEL_RENTALBATTLES, battlesNum=style.rentCount))
            buyBtnVO = self.__makeBuyBtnVO(validTransaction, isFromInventory)
            if not isFromInventory:
                itemPriceVO = getItemPricesVO(stylePrice)[0]
        return StylePriceVO(isEnoughMoney=validTransaction, rentalInfo=rentalInfoText, buyBtnVO=buyBtnVO, itemPriceVO=itemPriceVO)._asdict()

    def __makeBuyBtnVO(self, validTransaction, isFromInventory):
        if isFromInventory:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_APPLY)
        else:
            label = _ms(VEHICLE_CUSTOMIZATION.COMMIT_BUY)
        disabledTooltip = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_BUYDISABLED_BODY
        return BuyBtnVO(enabled=validTransaction, label=label, disabledTooltip=disabledTooltip)._asdict()
