# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/frontline_buy_confirm_view.py
import WWISE
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.FrontlineBuyConfirmViewMeta import FrontlineBuyConfirmViewMeta
from gui.shared import event_dispatcher as shared_event
from gui.shared.gui_items.processors.frontline import FrontlineBuyRewardVehicle
from gui.sounds.filters import STATE_HANGAR_FILTERED
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from helpers import int2roman
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
from gui.impl import backport
from gui.impl.gen import R

class FrontlineBuyConfirmView(FrontlineBuyConfirmViewMeta):

    def __init__(self, ctx=None):
        super(FrontlineBuyConfirmView, self).__init__(ctx)
        self.__vehicle = ctx.get('vehicle')
        self.__blur = WGUIBackgroundBlurSupportImpl()
        self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.WINDOWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER])

    def _populate(self):
        super(FrontlineBuyConfirmView, self)._populate()
        self.setData()
        WWISE.WW_setState(STATE_HANGAR_FILTERED, '{}_on'.format(STATE_HANGAR_FILTERED))

    def destroy(self):
        self.__blur.disable()
        super(FrontlineBuyConfirmView, self).destroy()

    def onClose(self):
        self.destroy()
        WWISE.WW_setState(STATE_HANGAR_FILTERED, '{}_off'.format(STATE_HANGAR_FILTERED))

    def onBack(self):
        self.onClose()

    @process
    def onBuy(self):
        result = yield FrontlineBuyRewardVehicle(self.__vehicle).request()
        if result and result.success:
            ctx = {'congratulationsViewSettings': {'bgSource': R.images.gui.maps.icons.epicBattles.backgrounds.meta_bg(),
                                             'backBtnLabel': R.strings.store.congratulationAnim.showEpicBtnLabel(),
                                             'backBtnEnabled': True}}
            shared_event.showVehicleBuyDialog(vehicle=self.__vehicle, previousAlias=VIEW_ALIAS.FRONTLINE_VEHICLE_PREVIEW_20, showOnlyCongrats=True, ctx=ctx)
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.onClose()

    def setData(self):
        title = _ms(backport.text(R.strings.epic_battle.buyConfirm.title()), level=int2roman(self.__vehicle.level), name=self.__vehicle.shortUserName)
        content = _ms(backport.text(R.strings.epic_battle.buyConfirm.content()), level=text_styles.highlightText(int2roman(self.__vehicle.level)), name=text_styles.highlightText(self.__vehicle.shortUserName))
        self.as_setDataS({'title': text_styles.promoTitle(title),
         'titleBig': text_styles.grandTitle(title),
         'content': text_styles.main(content),
         'contentBig': text_styles.mainBig(content),
         'buyBtnLabel': _ms(backport.text(R.strings.epic_battle.buyConfirm.buyLabel())),
         'backBtnLabel': _ms(backport.text(R.strings.epic_battle.buyConfirm.backLabel()))})
