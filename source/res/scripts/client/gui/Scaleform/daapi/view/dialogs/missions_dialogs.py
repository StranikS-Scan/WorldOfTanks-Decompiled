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
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -3, 0) if self.meta.isAvailable() else icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON, 16, 16, -4, 0)
        text = text_styles.neutral(self.meta.getInfoText()) if self.meta.isAvailable() else text_styles.alert(self.meta.getWarningText())
        statusText = text_styles.concatStylesWithSpace(icon, text)
        self.as_setDataS({'neededLabel': text_styles.highlightText(self.meta.getNeededText()),
         'neededValue': text_styles.highlightText(self.meta.getPawnCost()),
         'totalLabel': text_styles.main(self.meta.getTotalText()),
         'totalValue': text_styles.main(self.meta.getFreeSheets()),
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
