# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_buy_confirm_view.py
from gui.Scaleform.daapi.view.meta.EventProgressionBuyConfirmViewMeta import EventProgressionBuyConfirmViewMeta
from gui.impl.pub.dialog_window import DialogButtons, DialogViewMixin
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.shared.formatters import text_styles, icons
from gui.impl import backport
from gui.impl.gen import R

class EventProgressionBuyConfirmView(DialogViewMixin, EventProgressionBuyConfirmViewMeta):

    def __init__(self, ctx=None):
        super(EventProgressionBuyConfirmView, self).__init__(ctx)
        self.__price = ctx.get('price')
        self.__blur = None
        return

    def setParentWindow(self, window):
        super(EventProgressionBuyConfirmView, self).setParentWindow(window)
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer)

    def onClose(self):
        self._sendDialogResult(DialogButtons.CANCEL)

    def onBack(self):
        self._sendDialogResult(DialogButtons.CANCEL)

    def onBuy(self):
        self._sendDialogResult(DialogButtons.SUBMIT)

    def _populate(self):
        super(EventProgressionBuyConfirmView, self)._populate()
        self.__setData()
        switchHangarOverlaySoundFilter(on=True)

    def _dispose(self):
        switchHangarOverlaySoundFilter(on=False)
        if self.__blur is not None:
            self.__blur.fini()
        super(EventProgressionBuyConfirmView, self)._dispose()
        return

    def __setData(self):
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
