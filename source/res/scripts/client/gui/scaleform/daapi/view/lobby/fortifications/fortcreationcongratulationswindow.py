# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortCreationCongratulationsWindow.py
import fortified_regions
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortCreationCongratulationsWindowMeta import FortCreationCongratulationsWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from helpers import i18n

class FortCreationCongratulationsWindow(AbstractWindowView, View, FortCreationCongratulationsWindowMeta, AppRef):

    def __init__(self, ctx = None):
        super(FortCreationCongratulationsWindow, self).__init__()

    def _populate(self):
        super(FortCreationCongratulationsWindow, self)._populate()
        self.__makeData()

    def __makeData(self):
        sourceCount = self.app.utilsManager.textManager.getText(TextType.DEFRES_TEXT, str(fortified_regions.g_cache.startResource))
        sourceCount += ' ' + self.app.utilsManager.textManager.getIcon(TextIcons.NUT_ICON)
        sourceCount = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TEXTBODY, sourceCount=sourceCount))
        self.as_setTextS(sourceCount)
        self.as_setTitleS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TEXTTITLE))
        self.as_setButtonLblS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_BUTTONLBL))
        self.as_setWindowTitleS(i18n.makeString(FORTIFICATIONS.CONGRATULATIONWINDOW_TITLELBL))

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(FortCreationCongratulationsWindow, self)._dispose()
