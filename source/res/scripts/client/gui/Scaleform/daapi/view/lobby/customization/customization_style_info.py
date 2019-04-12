# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_style_info.py
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentVehicle
import GUI
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.shared import getPurchaseMoneyState, isTransactionValid, getSuitableText
from gui.Scaleform.daapi.view.meta.CustomizationStyleInfoMeta import CustomizationStyleInfoMeta
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
StyleInfoVO = namedtuple('StyleInfoVO', ('styleName', 'styleInfo', 'styleInfoBig', 'buttonVO', 'suitableBlock', 'styleParams'))
ButtonVO = namedtuple('ButtonVO', ('enabled', 'label', 'disabledTooltip'))
ParamVO = namedtuple('ParamVO', ('iconSrc', 'paramText'))
STYLE_INFO_BLUR_DELAY = 0.2
_STYLE_INFO_BLUR_MASK = 'system/maps/mask.dds'
_INSERTION_OPEN_TAG = "<font size='16' face='$FieldFont' color='#E9E2BF'>"
_INSERTION_OPEN_TAG_BIG = "<font size='18' face='$TitleFont' color='#E9E2BF'>"
_INSERTION_CLOSE_TAG = '</font>'

class Events(object):
    NY18 = 'NY18'
    NY19 = 'NY19'
    FOOTBALL18 = 'FOOTBALL18'
    WINTER_HUNT = 'WINTER_HUNT'
    KURSK_BATTLE = 'KURSK_BATTLE'
    ALL = (NY18,
     NY19,
     FOOTBALL18,
     WINTER_HUNT,
     KURSK_BATTLE)
    ICONS = {NY18: R.images.gui.maps.icons.customization.style_info.newYear(),
     NY19: R.images.gui.maps.icons.customization.style_info.newYear(),
     FOOTBALL18: R.images.gui.maps.icons.customization.style_info.football(),
     WINTER_HUNT: R.images.gui.maps.icons.customization.style_info.marathon(),
     KURSK_BATTLE: R.images.gui.maps.icons.customization.style_info.marathon()}
    TEXTS = {NY18: R.strings.vehicle_customization.styleInfo.event.ny18(),
     NY19: R.strings.vehicle_customization.styleInfo.event.ny19(),
     FOOTBALL18: R.strings.vehicle_customization.styleInfo.event.football18(),
     WINTER_HUNT: R.strings.vehicle_customization.styleInfo.event.winter_hunt(),
     KURSK_BATTLE: R.strings.vehicle_customization.styleInfo.event.kursk_battle()}


class CustomizationStyleInfo(CustomizationStyleInfoMeta):
    service = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    @property
    def visible(self):
        return self.__visible

    def __init__(self):
        super(CustomizationStyleInfo, self).__init__()
        self.__ctx = None
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__visible = False
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
            styleInfoVO = self.__makeVO(style)
            self.as_setDataS(styleInfoVO)
            self.as_showS()
            BigWorld.callback(STYLE_INFO_BLUR_DELAY, self.__enableBlur)
            self.__visible = True
            return

    def onClose(self):
        self.__ctx.onStyleInfoHidden()
        self.__blur.blendMask = ''
        self.__blur.enable = False
        self.service.setDOFenabled(False)
        self.__visible = False

    def onApply(self):
        self.__ctx.onStyleInfoHidden(toBuyWindow=True)
        self.__blur.blendMask = ''
        self.service.setDOFenabled(False)
        self.__visible = False

    def hide(self):
        self.as_hideS()

    def disableBlur(self):
        self.__blur.blendMask = ''
        self.__blur.enable = False

    def __makeVO(self, style):
        styleParams = self.__makeParamsVO(style)
        styleName = style.userName
        styleInfoText = self.__ctx.getItemFromSelectedRegion().textInfo
        styleInfo = text_styles.mainBig(styleInfoText % {'insertion_open': _INSERTION_OPEN_TAG,
         'insertion_close': _INSERTION_CLOSE_TAG})
        styleInfoBig = text_styles.mainBig(styleInfoText % {'insertion_open': _INSERTION_OPEN_TAG_BIG,
         'insertion_close': _INSERTION_CLOSE_TAG})
        buttonVO = self.__makeButtonVO(style)
        suitableBlock = text_styles.mainBig(backport.text(R.strings.vehicle_customization.styleInfo.suitable()))
        suitableBlock += getSuitableText(style, g_currentVehicle.item)
        return StyleInfoVO(styleName=styleName, styleInfo=styleInfo, styleInfoBig=styleInfoBig, buttonVO=buttonVO, suitableBlock=suitableBlock, styleParams=styleParams)._asdict()

    def __makeButtonVO(self, style):
        buttonVO = None
        if self.__ctx.isOutfitsModified():
            stylePrice = style.getBuyPrice().price
            moneyState = getPurchaseMoneyState(stylePrice)
            enabled = isTransactionValid(moneyState, stylePrice)
            if self.__ctx.getPurchaseItems()[0].isFromInventory:
                label = backport.text(R.strings.vehicle_customization.commit.apply())
            else:
                label = backport.text(R.strings.vehicle_customization.styleInfo.btn.install())
            buttonVO = ButtonVO(enabled=enabled, label=label, disabledTooltip=backport.text(R.strings.vehicle_customization.customization.buyDisabled.body()))._asdict()
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
        else:
            import random
            event = random.choice(Events.ALL)
            eventIcon = backport.image(Events.ICONS[event])
            eventString = backport.text(Events.TEXTS[event])
            eventParam = ParamVO(eventIcon, text_styles.main(eventString))
            params.append(eventParam._asdict())
        return params

    def __enableBlur(self):
        self.__blur.blendMask = _STYLE_INFO_BLUR_MASK
        self.__blur.enable = True
