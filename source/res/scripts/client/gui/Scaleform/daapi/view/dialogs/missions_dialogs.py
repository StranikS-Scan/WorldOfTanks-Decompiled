# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/missions_dialogs.py
from gui.Scaleform.daapi.view.meta.UseAwardSheetWindowMeta import UseAwardSheetWindowMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.pm_constants import SOUNDS
from gui.shared.formatters import text_styles, icons

class UseAwardSheetWindow(UseAwardSheetWindowMeta):

    def __init__(self, meta, handler):
        super(UseAwardSheetWindow, self).__init__()
        self.meta = meta
        self.handler = handler

    def _populate(self):
        super(UseAwardSheetWindow, self)._populate()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getSubmitButtonLabel(),
         'cancelBtnLabel': self.meta.getCancelButtonLabel()})
        statusText = text_styles.neutral(self.meta.getInfoText()) if self.meta.isAvailable() else text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON, 16, 16, -4, 0), text_styles.alert(self.meta.getWarningText()))
        self.as_setDataS({'descrText': self.meta.getDescrText(),
         'footerText': self.meta.getFooterText(),
         'counterText': self.meta.getCounterText(),
         'statusText': statusText,
         'icon': self.meta.getIcon()})

    def _dispose(self):
        if self.meta is not None:
            self.meta = None
        self.handler = self._data = None
        super(UseAwardSheetWindow, self)._dispose()
        return

    def accept(self):
        self.handler(True)
        self.soundManager.playInstantSound(SOUNDS.FREE_AWARD_LIST_SPENT)
        self.destroy()

    def cancel(self):
        self.handler(False)
        self.destroy()

    def onWindowClose(self):
        self.cancel()
