# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ReportBug.py
from adisp import process
from gui import makeHtmlString
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.locale.MENU import MENU
from gui import GUI_SETTINGS, DialogsInterface
from gui.Scaleform.daapi.view.meta.ReportBugPanelMeta import ReportBugPanelMeta
from gui import game_control
from debug_utils import LOG_DEBUG
from helpers import i18n
import BigWorld

class ReportBugPanel(ReportBugPanelMeta):

    def reportBug(self):
        reportBugOpenConfirm(self.accountId)

    def _populate(self):
        super(ReportBugPanel, self)._populate()
        links = GUI_SETTINGS.reportBugLinks
        if len(links):
            player = BigWorld.player()
            self.accountId = player.databaseID
            reportBugLink = makeHyperLink('ingameMenu', MENU.INGAME_MENU_LINKS_REPORT_BUG)
            self.as_setHyperLinkS(reportBugLink)


def getForumURL(accountId):
    links = GUI_SETTINGS.reportBugLinks
    url = None
    for region in links:
        min = long(links[region]['min'])
        max = long(links[region]['max'])
        if min <= long(accountId) <= max:
            url = links[region]['url']
            break

    return url


def makeHyperLink(linkType, textId):
    text = i18n.makeString(textId)
    attrs = {'linkType': linkType,
     'text': text}
    linkHtml = makeHtmlString('html_templates:lobby/system_messages', 'link', attrs)
    return linkHtml


@process
def reportBugOpenConfirm(accountId):
    isOk = yield DialogsInterface.showI18nConfirmDialog('reportBug', focusedID=DIALOG_BUTTON_ID.SUBMIT)
    if isOk:
        game_control.g_instance.links.open(getForumURL(accountId))
