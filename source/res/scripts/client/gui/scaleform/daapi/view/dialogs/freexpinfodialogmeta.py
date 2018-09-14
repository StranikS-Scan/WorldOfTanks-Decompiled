# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/FreeXPInfoDialogMeta.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared import events
from helpers import i18n
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
__author__ = 'd_savitski'

class FreeXPInfoBaseMeta(IDialogMeta):

    def __init__(self):
        super(FreeXPInfoBaseMeta, self).__init__()

    def getTitle(self):
        return ''

    def getSubmitLbl(self):
        return ''

    def getTextInfo(self):
        return ''

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT

    def getEventType(self):
        return VIEW_ALIAS.FREE_X_P_INFO_WINDOW


class FreeXPInfoMeta(FreeXPInfoBaseMeta):

    def __init__(self):
        super(FreeXPInfoMeta, self).__init__()

    def getTitle(self):
        return i18n.makeString(DIALOGS.FREEXPINFO_TITLE)

    def getSubmitLbl(self):
        return i18n.makeString(DIALOGS.FREEXPINFO_SUBMITBTNLBL)

    def getTextInfo(self):
        text = {}
        msgFormatted = makeHtmlString('html_templates:lobby/dialogs', 'freeXPInfo', {})
        text['body'] = msgFormatted
        return text
