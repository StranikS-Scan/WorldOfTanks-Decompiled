# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralReferralsIntroWindow.py
import BigWorld
from helpers import i18n
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.ReferralReferralsIntroWindowMeta import ReferralReferralsIntroWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties

class ReferralReferralsIntroWindow(View, AbstractWindowView, ReferralReferralsIntroWindowMeta, AppRef):

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
        referrerNameFmt = self.app.utilsManager.textManager.getText(TextType.STATUS_WARNING_TEXT, self.__referrerName)
        handIcon = self.app._utilsMgr.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALSMALLHAND, 16, 16, -4, 0))
        self.as_setDataS({'titleTF': self.app.utilsManager.textManager.getText(TextType.PROMO_TITLE, i18n.makeString(MENU.REFERRALREFERRALSINTROWINDOW_TEXT_BLOCK_TITLE, userName=BigWorld.player().name)),
         'bodyTF': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.referralreferralsintrowindow_text_block_body(contentKey), referrerName=referrerNameFmt, handIcon=handIcon)),
         'squadTF': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.REFERRALREFERRALSINTROWINDOW_TEXT_BLOCK_SQUAD_TEXT))})
