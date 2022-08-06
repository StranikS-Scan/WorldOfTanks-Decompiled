# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_style_info.py
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
from gui.Scaleform.daapi.view.meta.CustomizationStyleInfoMeta import CustomizationStyleInfoMeta
from gui.shared.utils.graphics import isRendererPipelineDeferred
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.customization.shared import C11nId, getPurchaseMoneyState, isTransactionValid
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from vehicle_outfit.outfit import Area
StyleInfoVO = namedtuple('StyleInfoVO', ('styleName', 'styleInfo', 'styleInfoBig', 'suitableBlock', 'styleParams'))
ButtonVO = namedtuple('ButtonVO', ('enabled', 'label', 'disabledTooltip', 'visible'))
ParamVO = namedtuple('ParamVO', ('iconSrc', 'paramText'))
STYLE_INFO_BLUR_DELAY = 0.2
BACKGROUND_ALPHA_FORWARD = 1.0
BACKGROUND_ALPHA_DEFERRED = 0.5
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
        self.__blur = None
        self.__blurRectId = None
        self.__visible = False
        self.__prevStyle = None
        self.__selectedStyle = None
        self.__paramsDOF = None
        self.__blurParams = None
        return

    def _populate(self):
        self.__ctx = self.service.getCtx()
        self.__blur = CachedBlur()
        g_clientUpdateManager.addMoneyCallback(self.updateButton)
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        self.__ctx.events.onUpdateStyleInfoDOF += self.__onUpdateStyleInfoDOF
        self.service.onCustomizationHelperRecreated += self.__onCustomizationHelperRecreated
        self.__setBackgroundAlpha()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        self.__ctx.events.onUpdateStyleInfoDOF -= self.__onUpdateStyleInfoDOF
        self.service.onCustomizationHelperRecreated -= self.__onCustomizationHelperRecreated
        self.__ctx = None
        if self.__blur is not None:
            self.__blur.fini()
        return

    def show(self, style=None):
        self.__prevStyle = self.__ctx.mode.modifiedStyle
        self.__selectedStyle = style or self.__ctx.mode.modifiedStyle
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
            self.__ctx.mode.unselectSlot()
            return

    def updateButton(self, *_):
        if self.__selectedStyle:
            buttonVO = self.__makeButtonVO(self.__selectedStyle)
            self.as_buttonUpdateS(buttonVO)

    def onClose(self):
        self.__ctx.events.onHideStyleInfo()
        self.disableBlur()
        self.__visible = False
        self.__selectedStyle = None
        if self.__prevStyle is None:
            slotId = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            self.__ctx.mode.removeItem(slotId)
        elif self.__prevStyle != self.__ctx.mode.modifiedStyle:
            self.__installStyle(self.__prevStyle)
        self.__prevStyle = None
        return

    def onApply(self):
        self.__ctx.events.onHideStyleInfo(toBuyWindow=True)
        if self.__blurRectId:
            self.__blur.removeRect(self.__blurRectId)
            self.__blurRectId = None
        self.service.setDOFenabled(False)
        self.__visible = False
        return

    def hide(self):
        self.stopCallback(self.__enableBlur)
        self.stopCallback(self.service.setDOFenabled)
        self.disableBlur()
        self.as_hideS()
        self.__paramsDOF = None
        return

    def disableBlur(self):
        if self.__blurRectId:
            self.__blur.removeRect(self.__blurRectId)
            self.__blurRectId = None
        self.__blur.disable()
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
            purchaseItem = first(self.__ctx.mode.getPurchaseItems())
            tooltip = backport.text(R.strings.vehicle_customization.customization.buyDisabled.body())
            if purchaseItem is not None and purchaseItem.isFromInventory:
                label = backport.text(R.strings.vehicle_customization.commit.apply())
                if self.__ctx.mode.isOutfitsHasLockedItems():
                    enabled = False
                    tooltip = backport.text(R.strings.vehicle_customization.customization.lockedItemsApply())
                else:
                    enabled = True
            else:
                label = backport.text(R.strings.vehicle_customization.commit.buy())
                enabled = isTransactionValid(moneyState, stylePrice)
            buttonVO = ButtonVO(enabled=enabled, label=label, disabledTooltip=tooltip, visible=True)._asdict()
        return buttonVO

    def __makeParamsVO(self, style):
        params = []
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        for season in SeasonType.COMMON_SEASONS:
            outfit = style.getOutfit(season, vehicleCD=vehicleCD)
            if outfit:
                container = outfit.hull
                intCD = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
                if not intCD:
                    continue
                camo = self.service.getItemByCD(intCD)
                if camo and camo.bonus:
                    bonus = camo.bonus.getFormattedValue(g_currentVehicle.item)
                    bonusIcon = backport.image(R.images.gui.maps.icons.customization.style_info.bonus())
                    formattedBonus = makeHtmlString('html_templates:lobby/customization', 'style_info_bonus', ctx={'bonus': bonus})
                    bonusParam = ParamVO(bonusIcon, formattedBonus)
                    params.append(bonusParam._asdict())
                    break

        displayType = style.customizationDisplayType()
        if displayType == 0:
            historicIcon = backport.image(R.images.gui.maps.icons.customization.style_info.historical())
            historicString = backport.text(R.strings.vehicle_customization.styleInfo.historical())
        elif displayType == 1:
            historicIcon = backport.image(R.images.gui.maps.icons.customization.style_info.nonhistorical())
            historicString = backport.text(R.strings.vehicle_customization.styleInfo.nonhistorical())
        else:
            historicIcon = backport.image(R.images.gui.maps.icons.customization.style_info.fantastical())
            historicString = backport.text(R.strings.vehicle_customization.styleInfo.fantastical())
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
        self.__blur.enable()

    def __installStyle(self, style):
        slotId = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        self.__ctx.mode.installItem(style.intCD, slotId)

    def __onUpdateStyleInfoDOF(self, paramsDOF):
        self.__paramsDOF = paramsDOF
        if self.__paramsDOF is not None and self.visible:
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

    def onWidthUpdated(self, x, width, height):
        if not self.visible:
            return
        blurRect = (round(x),
         0,
         round(x + width),
         round(height))
        if self.__blurRectId:
            self.__blur.changeRect(self.__blurRectId, blurRect)
        else:
            self.__blurRectId = self.__blur.addRect(blurRect)

    def __setBackgroundAlpha(self):
        alpha = BACKGROUND_ALPHA_DEFERRED if isRendererPipelineDeferred() else BACKGROUND_ALPHA_FORWARD
        self.as_setBackgroundAlphaS(alpha)
