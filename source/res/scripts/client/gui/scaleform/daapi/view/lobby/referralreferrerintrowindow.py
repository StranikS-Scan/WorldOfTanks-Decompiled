# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReferralReferrerIntroWindow.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.ReferralReferrerIntroWindowMeta import ReferralReferrerIntroWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from gui.shared.formatters import text_styles, icons
from helpers import i18n

class ReferralReferrerIntroWindow(ReferralReferrerIntroWindowMeta):

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
          'link': self.__makeHyperLink(OpenLinkEvent.INVIETES_MANAGEMENT, MENU.REFERRALREFERRERINTROWINDOW_TEXTBLOCK_LINK)}, showLinkBtn=True), self.__packContentBlock('squad_block', RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_SQUAD), self.__packContentBlock('referrals_block', RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALHAND, ctx={'icon': icons.makeImageTag(RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALSMALLHAND, 16, 16, -4, 0)})]
        self.as_setDataS({'titleMsg': text_styles.promoTitle(i18n.makeString(MENU.REFERRALREFERRERINTROWINDOW_TITLEMESSAGE)),
         'blocksVOs': blocks})

    def __packContentBlock(self, localeKey, iconSource, ctx = None, showLinkBtn = False):
        return {'iconSource': iconSource,
         'titleTF': text_styles.highTitle(i18n.makeString(MENU.referralreferrerintrowindow_textblock_title(localeKey))),
         'bodyTF': text_styles.main(i18n.makeString(MENU.referralreferrerintrowindow_textblock_body(localeKey), **(ctx or {}))),
         'showLinkBtn': showLinkBtn}

    @classmethod
    def __makeHyperLink(cls, linkType, textId):
        return makeHtmlString('html_templates:lobby/fortifications', 'link', {'linkType': linkType,
         'text': i18n.makeString(textId)})
