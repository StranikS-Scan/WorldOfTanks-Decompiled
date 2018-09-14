# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralReferrerIntroWindow.py
from gui import makeHtmlString, game_control
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.ReferralReferrerIntroWindowMeta import ReferralReferrerIntroWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import i18n

class ReferralReferrerIntroWindow(View, AbstractWindowView, ReferralReferrerIntroWindowMeta, AppRef):

    def __init__(self, ctx = None):
        super(ReferralReferrerIntroWindow, self).__init__(ctx)
        self.__invitesCount = ctx.get('invitesCount', 0)

    def onWindowClose(self):
        self.destroy()

    def onClickApplyButton(self):
        self.onWindowClose()

    def onClickHrefLink(self):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.INVIETES_MANAGEMENT))

    def _populate(self):
        super(ReferralReferrerIntroWindow, self)._populate()
        blocks = [self.__packContentBlock('invite_block', RES_ICONS.MAPS_ICONS_LIBRARY_REFERRALINVITEICON_1, ctx={'inviteCount': self.__invitesCount,
          'link': self.__makeHyperLink(OpenLinkEvent.INVIETES_MANAGEMENT, MENU.REFERRALREFERRERINTROWINDOW_TEXTBLOCK_LINK)}, showLinkBtn=True), self.__packContentBlock('squad_block', RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_SQUAD), self.__packContentBlock('referrals_block', RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALHAND, ctx={'icon': self.app._utilsMgr.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALSMALLHAND, 16, 16, -4, 0))})]
        self.as_setDataS({'titleMsg': self.app.utilsManager.textManager.getText(TextType.PROMO_TITLE, i18n.makeString(MENU.REFERRALREFERRERINTROWINDOW_TITLEMESSAGE)),
         'blocksVOs': blocks})

    def __packContentBlock(self, localeKey, iconSource, ctx = None, showLinkBtn = False):
        return {'iconSource': iconSource,
         'titleTF': self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.referralreferrerintrowindow_textblock_title(localeKey))),
         'bodyTF': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.referralreferrerintrowindow_textblock_body(localeKey), **(ctx or {}))),
         'showLinkBtn': showLinkBtn}

    @classmethod
    def __makeHyperLink(cls, linkType, textId):
        return makeHtmlString('html_templates:lobby/fortifications', 'link', {'linkType': linkType,
         'text': i18n.makeString(textId)})
