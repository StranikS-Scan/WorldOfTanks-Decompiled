# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortIntelligenceWindow.py
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortIntelligenceWindowMeta import FortIntelligenceWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from helpers import i18n
TEXTS = (FORTIFICATIONS.FORTINTELLIGENCE_HEADERBLOCK,
 FORTIFICATIONS.FORTINTELLIGENCE_TOPBLOCK,
 FORTIFICATIONS.FORTINTELLIGENCE_MIDDLEBLOCK,
 FORTIFICATIONS.FORTINTELLIGENCE_BOTTOMBLOCK)

class FortIntelligenceWindow(AbstractWindowView, View, FortIntelligenceWindowMeta, AppRef):

    def __init__(self):
        super(FortIntelligenceWindow, self).__init__()

    def _populate(self):
        super(FortIntelligenceWindow, self)._populate()
        self.__makeData()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(FortIntelligenceWindow, self)._dispose()

    def __makeData(self):
        data = []
        countIteration = 0
        for item in TEXTS:
            data.extend(self.__getLocalize(item, countIteration))
            countIteration += 1

        data.append(fort_text.getText(fort_text.NEUTRAL_TEXT, self.__getText(FORTIFICATIONS.FORTINTELLIGENCE_ADDITIONALTEXT_COMINGSOON)))
        self.as_setDataS(data)

    def __getLocalize(self, value, countIteration):
        headerText = fort_text.PROMO_SUB_TITLE
        if countIteration == 0:
            headerText = fort_text.PROMO_TITLE
        valueHeader = fort_text.getText(headerText, self.__getText(value + '/header'))
        valueBody = fort_text.getText(fort_text.MAIN_TEXT, self.__getText(value + '/body'))
        return [valueHeader, valueBody]

    def __getText(self, value):
        return i18n.makeString(value)
