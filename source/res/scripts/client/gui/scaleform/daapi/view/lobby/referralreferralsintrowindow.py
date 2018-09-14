# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralReferralsIntroWindow.py
import BigWorld
from gui.shared.formatters import text_styles, icons
from helpers import i18n
from gui.Scaleform.daapi.view.meta.ReferralReferralsIntroWindowMeta import ReferralReferralsIntroWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class ReferralReferralsIntroWindow(ReferralReferralsIntroWindowMeta):

    def __init__(self, ctx):
        super(ReferralReferralsIntroWindow, self).__init__()
        self.__referrerName = ctx.get('referrerName', '')
        self.__isNewbie = ctx.get('newbie', False)

    def onWindowClose(self):
        self.destroy()

    def onClickApplyBtn(self):
        self.onWindowClose()

    def _populate(self):
        super(ReferralReferralsIntroWindow, self)._populate()
        contentKey = 'referrals' if self.__isNewbie else 'phenix'
        referrerNameFmt = text_styles.warning(self.__referrerName)
        handIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALSMALLHAND, 16, 16, -4, 0)
        self.as_setDataS({'titleTF': text_styles.promoTitle(i18n.makeString(MENU.REFERRALREFERRALSINTROWINDOW_TEXT_BLOCK_TITLE, userName=getattr(BigWorld.player(), 'name', 'Unknown'))),
         'bodyTF': text_styles.main(i18n.makeString(MENU.referralreferralsintrowindow_text_block_body(contentKey), referrerName=referrerNameFmt, handIcon=handIcon)),
         'squadTF': text_styles.main(i18n.makeString(MENU.REFERRALREFERRALSINTROWINDOW_TEXT_BLOCK_SQUAD_TEXT))})
