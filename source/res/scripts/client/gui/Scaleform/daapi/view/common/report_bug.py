# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/report_bug.py
from adisp import adisp_process
from gui import GUI_SETTINGS, DialogsInterface, makeHtmlString
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.ReportBugPanelMeta import ReportBugPanelMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController

class ReportBugPanel(ReportBugPanelMeta):

    def reportBug(self):
        self.reportBugOpenConfirm()

    def _populate(self):
        super(ReportBugPanel, self)._populate()
        if GUI_SETTINGS.reportBugLink:
            text = backport.text(R.strings.menu.ingame_menu.links.report_bug())
            reportBugLink = self.makeHyperLink('ingameMenu', text)
            self.as_setHyperLinkS(reportBugLink)

    @staticmethod
    def makeHyperLink(linkType, text):
        ctx = {'linkType': linkType,
         'text': text}
        linkHtml = makeHtmlString('html_templates:lobby/system_messages', 'link', ctx)
        return linkHtml

    @staticmethod
    @adisp_process
    def reportBugOpenConfirm():
        isOk = yield DialogsInterface.showI18nConfirmDialog('reportBug', focusedID=DIALOG_BUTTON_ID.SUBMIT)
        if isOk:
            links = dependency.instance(IExternalLinksController)
            links.open(GUI_SETTINGS.reportBugLink)
