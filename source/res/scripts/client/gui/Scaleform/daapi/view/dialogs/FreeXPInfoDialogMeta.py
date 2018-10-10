# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/FreeXPInfoDialogMeta.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.locale.DIALOGS import DIALOGS
from helpers import i18n
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class FreeXPInfoBaseMeta(IDialogMeta):

    def getTitle(self):
        pass

    def getSubmitLbl(self):
        pass

    def getTextInfo(self):
        pass

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT_SCOPE

    def getEventType(self):
        return VIEW_ALIAS.FREE_X_P_INFO_WINDOW


class FreeXPInfoMeta(FreeXPInfoBaseMeta):

    def getTitle(self):
        return i18n.makeString(DIALOGS.FREEXPINFO_TITLE)

    def getSubmitLbl(self):
        return i18n.makeString(DIALOGS.FREEXPINFO_SUBMITBTNLBL)

    def getTextInfo(self):
        text = {}
        msgFormatted = makeHtmlString('html_templates:lobby/dialogs', 'freeXPInfo', {})
        text['body'] = msgFormatted
        return text
