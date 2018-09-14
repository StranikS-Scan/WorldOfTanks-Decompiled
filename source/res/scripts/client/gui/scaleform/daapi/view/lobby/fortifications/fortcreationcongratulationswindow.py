# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortCreationCongratulationsWindow.py
import fortified_regions
from gui.Scaleform.daapi.view.meta.FortCreationCongratulationsWindowMeta import FortCreationCongratulationsWindowMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.formatters import icons, text_styles
from helpers import i18n

class FortCreationCongratulationsWindow(FortCreationCongratulationsWindowMeta):

    def __init__(self, _ = None):
        super(FortCreationCongratulationsWindow, self).__init__()

    def _populate(self):
        super(FortCreationCongratulationsWindow, self)._populate()
        self.__makeData()

    def __makeData(self):
        sourceCount = text_styles.defRes(str(fortified_regions.g_cache.startResource))
        sourceCount += ' ' + icons.nut()
        sourceCount = text_styles.standard(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TEXTBODY, sourceCount=sourceCount))
        self.as_setTextS(sourceCount)
        self.as_setTitleS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TEXTTITLE))
        self.as_setButtonLblS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_BUTTONLBL))
        self.as_setWindowTitleS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TITLELBL))

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(FortCreationCongratulationsWindow, self)._dispose()
