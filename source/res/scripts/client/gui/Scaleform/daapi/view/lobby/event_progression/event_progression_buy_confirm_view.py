# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_buy_confirm_view.py
from adisp import process
from constants import IS_CHINA
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventProgressionBuyConfirmViewMeta import EventProgressionBuyConfirmViewMeta
from gui.impl.lobby.common.congrats.congrats_ctx import EventProgressionStyleCongratsCtx
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared import event_dispatcher as shared_event
from gui.shared.gui_items.processors.event_progression import getEventProgressionRewardRequester
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.shared.formatters import text_styles, icons
from gui.impl import backport
from gui.impl.gen import R

class EventProgressionBuyConfirmView(EventProgressionBuyConfirmViewMeta):

    def __init__(self, ctx=None):
        super(EventProgressionBuyConfirmView, self).__init__(ctx)
        self.__vehicle = ctx['vehicle']
        self.__reward = ctx['reward']
        self.__price = ctx.get('price')
        self.__blur = CachedBlur(enabled=True, ownLayer=APP_CONTAINERS_NAMES.DIALOGS, layers=(APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.WINDOWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER))

    def _populate(self):
        super(EventProgressionBuyConfirmView, self)._populate()
        self.setData()
        switchHangarOverlaySoundFilter(on=True)

    def destroy(self):
        self.__blur.fini()
        super(EventProgressionBuyConfirmView, self).destroy()

    def onClose(self):
        self.destroy()
        switchHangarOverlaySoundFilter(on=False)

    def onBack(self):
        self.onClose()

    @process
    def onBuy(self):
        result = yield getEventProgressionRewardRequester(self.__reward).request()
        if result and result.success:
            if self.__reward.itemTypeID == GUI_ITEM_TYPE.STYLE:
                shared_event.showCongrats(EventProgressionStyleCongratsCtx(self.__reward))
            else:
                shared_event.showVehicleBuyDialog(vehicle=self.__vehicle, previousAlias=VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW, showOnlyCongrats=True, ctx={'congratulationsViewSettings': {'backBtnLabel': R.strings.store.congratulationAnim.backToEpicLabel(),
                                                 'backBtnEnabled': True}})
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.onClose()

    def setData(self):
        rTokensImage = R.images.gui.maps.icons.epicBattles.prestigePoints if IS_CHINA else R.images.gui.maps.icons.epicBattles.rewardPoints
        self.as_setDataS({'title': self.__formatTitle(text_styles.promoTitle, rTokensImage.c_24x24(), iconSize=24, vSpace=-3),
         'titleBig': self.__formatTitle(text_styles.grandTitle, rTokensImage.c_32x32(), iconSize=32, vSpace=-4),
         'content': '',
         'contentBig': '',
         'buyBtnLabel': backport.text(R.strings.event_progression.buyConfirm.buyLabel()),
         'backBtnLabel': backport.text(R.strings.event_progression.buyConfirm.backLabel()),
         'showIcon': False})

    def __formatTitle(self, style, iconResID, iconSize, vSpace):
        return style(backport.text(R.strings.event_progression.buyConfirm.style_title() if self.__reward.itemTypeID == GUI_ITEM_TYPE.STYLE else R.strings.event_progression.buyConfirm.title(), price='{}{}'.format(self.__price, icons.makeImageTag(backport.image(iconResID), width=iconSize, height=iconSize, vSpace=vSpace))))
