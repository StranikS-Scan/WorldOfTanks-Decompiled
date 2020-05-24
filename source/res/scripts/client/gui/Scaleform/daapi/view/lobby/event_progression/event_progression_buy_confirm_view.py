# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_buy_confirm_view.py
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventProgressionBuyConfirmViewMeta import EventProgressionBuyConfirmViewMeta
from gui.shared import event_dispatcher as shared_event
from gui.shared.gui_items.processors.event_progression import EventProgressionBuyRewardVehicle
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.shared.formatters import text_styles, icons
from gui.impl import backport
from gui.impl.gen import R

class EventProgressionBuyConfirmView(EventProgressionBuyConfirmViewMeta):

    def __init__(self, ctx=None):
        super(EventProgressionBuyConfirmView, self).__init__(ctx)
        self.__vehicle = ctx.get('vehicle')
        self.__price = ctx.get('price')
        self.__blur = WGUIBackgroundBlurSupportImpl()
        self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.WINDOWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER])

    def _populate(self):
        super(EventProgressionBuyConfirmView, self)._populate()
        self.setData()
        switchHangarOverlaySoundFilter(on=True)

    def destroy(self):
        self.__blur.disable()
        super(EventProgressionBuyConfirmView, self).destroy()

    def onClose(self):
        self.destroy()
        switchHangarOverlaySoundFilter(on=False)

    def onBack(self):
        self.onClose()

    @process
    def onBuy(self):
        result = yield EventProgressionBuyRewardVehicle(self.__vehicle).request()
        if result and result.success:
            ctx = {'congratulationsViewSettings': {'backBtnLabel': R.strings.store.congratulationAnim.showEpicBtnLabel(),
                                             'backBtnEnabled': True}}
            shared_event.showVehicleBuyDialog(vehicle=self.__vehicle, previousAlias=VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW, showOnlyCongrats=True, ctx=ctx)
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.onClose()

    def setData(self):
        rTokensImage = R.images.gui.maps.icons.epicBattles.rewardPoints
        self.as_setDataS({'title': self.__formatTitle(text_styles.promoTitle, rTokensImage.c_24x24(), iconSize=24, vSpace=-3),
         'titleBig': self.__formatTitle(text_styles.grandTitle, rTokensImage.c_32x32(), iconSize=32, vSpace=-4),
         'content': '',
         'contentBig': '',
         'buyBtnLabel': backport.text(R.strings.event_progression.buyConfirm.buyLabel()),
         'backBtnLabel': backport.text(R.strings.event_progression.buyConfirm.backLabel()),
         'showIcon': False})

    def __formatTitle(self, style, iconResID, iconSize, vSpace):
        return style(backport.text(R.strings.event_progression.buyConfirm.title(), price='{}{}'.format(self.__price, icons.makeImageTag(backport.image(iconResID), width=iconSize, height=iconSize, vSpace=vSpace))))
