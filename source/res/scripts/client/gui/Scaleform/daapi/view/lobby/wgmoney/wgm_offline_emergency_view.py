# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wgmoney/wgm_offline_emergency_view.py
from gui.Scaleform.daapi.view.meta.WGMoneyWarningViewMeta import WGMoneyWarningViewMeta
from gui.Scaleform.locale.WGM import WGM
from gui.shared.formatters import icons, text_styles
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class WGMoneyWarningView(WGMoneyWarningViewMeta):

    def __init__(self, ctx=None):
        super(WGMoneyWarningView, self).__init__(ctx)

    def closeView(self):
        self.destroy()

    def _populate(self):
        super(WGMoneyWarningView, self)._populate()
        self.__setData()

    def __setData(self):
        self.as_setDataS({'titleText': icons.alertBig(-4) + ' ' + _ms(WGM.WARNINGVIEW_TITLE),
         'subTitleText': text_styles.middleTitle(WGM.WARNINGVIEW_SUBTITLETEXT),
         'compensateData': {'leftIconSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_CREDITS,
                            'rightIconSource': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_DEFAULT,
                            'leftText': text_styles.main(WGM.WARNINGVIEW_COMPENSATEMESSAGE_LEFTTEXT),
                            'rightText': text_styles.main(_ms(WGM.WARNINGVIEW_COMPENSATEMESSAGE_RIGHTTEXT, free=text_styles.middleTitle(WGM.WARNINGVIEW_COMPENSATEMESSAGE_RIGHTTEXT_FREE)))}})
