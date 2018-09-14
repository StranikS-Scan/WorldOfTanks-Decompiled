# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortDisableDefencePeriodWindow.py
import BigWorld
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortDisableDefencePeriodWindowMeta import FortDisableDefencePeriodWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as ALIAS, FORTIFICATIONS
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.fortifications.context import DefencePeriodCtx
from helpers import i18n

class FortDisableDefencePeriodWindow(AbstractWindowView, View, FortDisableDefencePeriodWindowMeta, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortDisableDefencePeriodWindow, self).__init__()
        self.__inputChecker = None
        self.__controlNumber = self.fortCtrl.getFort().getTotalDefRes()
        return

    def initInputChecker(self):
        self.__inputChecker.errorMsg = self.__makeInputCheckerError()
        self.__inputChecker.questionTitle = self.__makeInputCheckerTitle()
        self.__inputChecker.questionBody = self.__makeInputCheckerBody()
        self.__inputChecker.setControlNumbers(self.__controlNumber, BigWorld.wg_getIntegralFormat)

    def onWindowClose(self):
        self.destroy()

    def onClickApplyButton(self):
        self.__setup()

    def onDefenceHourShutdown(self):
        if self.fortCtrl.getFort().isDefenceHourShutDown():
            self.destroy()

    def onShutdownDowngrade(self):
        self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__inputChecker = viewPy
        self.initInputChecker()

    def _populate(self):
        super(FortDisableDefencePeriodWindow, self)._populate()
        self.startFortListening()
        if self.fortCtrl.getFort().isDefenceHourShutDown():
            return self.destroy()
        self.__makeMainData()

    def _dispose(self):
        self.__inputChecker = None
        self.stopFortListening()
        super(FortDisableDefencePeriodWindow, self)._dispose()
        return

    def __makeInputCheckerError(self):
        return self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(ALIAS.DEMOUNTBUILDING_ERRORMESSAGE))

    def __makeInputCheckerTitle(self):
        return self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(ALIAS.DISABLEDEFENCEPERIODWINDOW_INPUTCHECKER_TITLE))

    def __makeInputCheckerBody(self):
        controlNumber = BigWorld.wg_getIntegralFormat(self.__controlNumber)
        controlNumber = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, str(controlNumber))
        questionBody = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(ALIAS.DISABLEDEFENCEPERIODWINDOW_INPUTCHECKER_BODY, controlNumber=controlNumber))
        return questionBody

    def __makeMainData(self):
        titleText = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.DISABLEDEFENCEPERIODWINDOW_MAINTEXT_TITLE))
        redText = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.DISABLEDEFENCEPERIODWINDOW_MAINTEXT_BODYREDTEXT))
        bodyText = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.DISABLEDEFENCEPERIODWINDOW_MAINTEXT_BODY, redText=redText))
        self.as_setDataS({'titleText': titleText,
         'bodyText': bodyText})

    @process
    def __setup(self):
        result = yield self.fortProvider.sendRequest(DefencePeriodCtx(waitingID='fort/settings'))
        if result:
            g_fortSoundController.playDefencePeriodDeactivated()
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DEFENCEHOURDEACTIVATED, type=SystemMessages.SM_TYPE.Warning)
        self.destroy()
