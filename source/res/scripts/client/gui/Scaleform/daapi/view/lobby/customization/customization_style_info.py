# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_style_info.py
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
import GUI
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.customization.shared import C11nId, getPurchaseMoneyState, isTransactionValid, SEASON_TYPE_TO_IDX
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
from gui.Scaleform.daapi.view.meta.CustomizationStyleInfoMeta import CustomizationStyleInfoMeta
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from shared_utils import first
StyleInfoVO = namedtuple('StyleInfoVO', ('styleName', 'styleInfo', 'styleInfoBig', 'suitableBlock', 'styleParams'))
ButtonVO = namedtuple('ButtonVO', ('enabled', 'label', 'disabledTooltip', 'visible'))
ParamVO = namedtuple('ParamVO', ('iconSrc', 'paramText'))
STYLE_INFO_BLUR_DELAY = 0.2
_STYLE_INFO_BLUR_MASK = 'system/maps/mask.dds'
_INSERTION_OPEN_TAG = "<font size='16' face='$FieldFont' color='#E9E2BF'>"
_INSERTION_OPEN_TAG_BIG = "<font size='18' face='$TitleFont' color='#E9E2BF'>"
_INSERTION_CLOSE_TAG = '</font>'

class CustomizationStyleInfo(CustomizationStyleInfoMeta, CallbackDelayer):
    service = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    @property
    def visible(self):
        return self.__visible

    def __init__(self):
        CustomizationStyleInfoMeta.__init__(self)
        CallbackDelayer.__init__(self)
        self.__ctx = None
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__visible = False
        self.__prevStyle = None
        self.__selectedStyle = None
        self.__paramsDOF = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()
        g_clientUpdateManager.addMoneyCallback(self.updateButton)
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        self.__ctx.onLocateToStyleInfo += self.__onLocateToStyleInfo
        self.service.onCustomizationHelperRecreated += self.__onCustomizationHelperRecreated

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        self.__ctx.onLocateToStyleInfo -= self.__onLocateToStyleInfo
        self.service.onCustomizationHelperRecreated -= self.__onCustomizationHelperRecreated
        self.__ctx = None
        return

    def show(self, style=None):
        self.__prevStyle = self.__ctx.modifiedStyle
        self.__selectedStyle = style or self.__ctx.modifiedStyle
        if self.__selectedStyle is None:
            return
        else:
            if self.__prevStyle is None or self.__selectedStyle != self.__prevStyle:
                self.__installStyle(self.__selectedStyle)
            styleInfoVO = self.__makeVO(self.__selectedStyle)
            self.as_setDataS(styleInfoVO)
            self.updateButton()
            self.as_showS()
            self.__visible = True
            self.delayCallback(STYLE_INFO_BLUR_DELAY, self.__enableBlur)
            self.__ctx.onClearItem()
            return

    def updateButton(self, *_):
        if self.__selectedStyle:
            buttonVO = self.__makeButtonVO(self.__selectedStyle)
            self.as_buttonUpdateS(buttonVO)

    def onClose(self):
        self.__ctx.onStyleInfoHidden()
        self.disableBlur()
        self.__visible = False
        self.__selectedStyle = None
        if self.__prevStyle is None:
            self.__ctx.removeStyle(self.__ctx.modifiedStyle.intCD)
        elif self.__prevStyle != self.__ctx.modifiedStyle:
            self.__installStyle(self.__prevStyle)
        self.__prevStyle = None
        self.__ctx.onClearItem()
        return

    def onApply(self):
        self.__ctx.onStyleInfoHidden(toBuyWindow=True)
        self.__blur.blendMask = ''
        self.service.setDOFenabled(False)
        self.__visible = False

    def hide(self):
        self.stopCallback(self.__enableBlur)
        self.stopCallback(self.service.setDOFenabled)
        self.as_hideS()
        self.__paramsDOF = None
        return

    def disableBlur(self):
        self.__blur.blendMask = ''
        self.__blur.enable = False
        self.__paramsDOF = None
        self.service.setDOFenabled(False)
        return

    def __makeVO(self, style):
        styleParams = self.__makeParamsVO(style)
        styleName = style.userName
        styleInfoText = style.longDescriptionSpecial
        styleInfo = text_styles.mainBig(styleInfoText % {'insertion_open': _INSERTION_OPEN_TAG,
         'insertion_close': _INSERTION_CLOSE_TAG})
        styleInfoBig = text_styles.mainBig(styleInfoText % {'insertion_open': _INSERTION_OPEN_TAG_BIG,
         'insertion_close': _INSERTION_CLOSE_TAG})
        suitableText = getSuitableText(style, g_currentVehicle.item)
        if suitableText:
            suitableBlock = text_styles.mainBig(backport.text(R.strings.vehicle_customization.styleInfo.suitable()))
            suitableBlock += suitableText
        else:
            suitableBlock = text_styles.mainBig(backport.text(R.strings.vehicle_customization.styleInfo.suitableAll()))
        return StyleInfoVO(styleName=styleName, styleInfo=styleInfo, styleInfoBig=styleInfoBig, suitableBlock=suitableBlock, styleParams=styleParams)._asdict()

    def __makeButtonVO(self, style):
        buttonVO = None
        if self.__ctx.isOutfitsModified():
            stylePrice = style.getBuyPrice().price
            moneyState = getPurchaseMoneyState(stylePrice)
            purchaseItem = first(self.__ctx.getPurchaseItems())
            if purchaseItem is not None and purchaseItem.isFromInventory:
                label = backport.text(R.strings.vehicle_customization.commit.apply())
                enabled = True
            else:
                label = backport.text(R.strings.vehicle_customization.commit.buy())
                enabled = isTransactionValid(moneyState, stylePrice)
            buttonVO = ButtonVO(enabled=enabled, label=label, disabledTooltip=backport.text(R.strings.vehicle_customization.customization.buyDisabled.body()), visible=True)._asdict()
        return buttonVO

    def __makeParamsVO(self, style):
        params = []
        for season in SeasonType.COMMON_SEASONS:
            outfit = style.getOutfit(season)
            if outfit:
                container = outfit.hull
                camo = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItem()
                if camo and camo.bonus:
                    bonus = camo.bonus.getFormattedValue(g_currentVehicle.item)
                    bonusIcon = backport.image(R.images.gui.maps.icons.customization.style_info.bonus())
                    formattedBonus = makeHtmlString('html_templates:lobby/customization', 'style_info_bonus', ctx={'bonus': bonus})
                    bonusParam = ParamVO(bonusIcon, formattedBonus)
                    params.append(bonusParam._asdict())
                    break

        if style.isHistorical():
            historicIcon = backport.image(R.images.gui.maps.icons.customization.style_info.historical())
            historicString = backport.text(R.strings.vehicle_customization.styleInfo.historical())
        else:
            historicIcon = backport.image(R.images.gui.maps.icons.customization.style_info.nonhistorical())
            historicString = backport.text(R.strings.vehicle_customization.styleInfo.nonhistorical())
        historicParam = ParamVO(historicIcon, text_styles.main(historicString))
        params.append(historicParam._asdict())
        if style.isRentable:
            rentIcon = backport.image(R.images.gui.maps.icons.customization.style_info.rentable())
            rentString = backport.text(R.strings.vehicle_customization.styleInfo.rentable())
            rentParam = ParamVO(rentIcon, text_styles.main(rentString))
            params.append(rentParam._asdict())
        elif style.specialEventTag is not None:
            eventIcon = style.specialEventIcon
            eventName = style.specialEventName
            eventParam = ParamVO(eventIcon, text_styles.main(eventName))
            params.append(eventParam._asdict())
        return params

    def __enableBlur(self):
        self.__blur.blendMask = _STYLE_INFO_BLUR_MASK
        self.__blur.enable = True

    def __installStyle(self, style):
        season = SEASON_TYPE_TO_IDX[self.__ctx.currentSeason]
        styleSlot = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        self.__ctx.installItem(style.intCD, styleSlot, season)
        self.__ctx.onClearItem()

    def __onLocateToStyleInfo(self, paramsDOF):
        self.__paramsDOF = paramsDOF
        if self.__paramsDOF is not None:
            self.service.setDOFparams(self.__paramsDOF)
            self.delayCallback(STYLE_INFO_BLUR_DELAY, self.service.setDOFenabled, enable=True)
        return

    def __onCustomizationHelperRecreated(self):
        if self.visible and self.__paramsDOF is not None:
            self.service.setDOFparams(self.__paramsDOF)
            self.service.setDOFenabled(True)
            self.service.suspendHighlighter()
        else:
            self.service.setDOFenabled(False)
        return

    def __onVehicleChangeStarted(self):
        self.__paramsDOF = None
        if self.visible:
            self.service.setDOFenabled(False)
        return
