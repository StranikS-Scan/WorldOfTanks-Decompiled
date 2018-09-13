# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/headerTutorial/HeaderTutorialWindow.py
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.headerTutorial.HeaderTutorialDialogMeta import RefuseHeaderTutorialDialogMeta
from gui.Scaleform.daapi.view.meta.HeaderTutorialWindowMeta import HeaderTutorialWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from account_helpers.AccountSettings import AccountSettings, HEADER_TUTORIAL
from helpers import i18n

class HeaderTutorialWindow(View, HeaderTutorialWindowMeta, AbstractWindowView):

    class STEPS_NAMES:
        WELCOME = 'welcome'
        STEP1 = 'step1'
        STEP2 = 'step2'
        STEP3 = 'step3'
        STEP4 = 'step4'
        STEP5 = 'step5'
        STEP6 = 'step6'
        ALL = (WELCOME,
         STEP1,
         STEP2,
         STEP3,
         STEP4,
         STEP5,
         STEP6)

    def __init__(self, ctx):
        super(HeaderTutorialWindow, self).__init__()
        self.__currentStep = ctx.get('currentStep', 0)

    def onWindowClose(self):
        self.__showRefuseDialog()

    def requestToLeave(self):
        self.__showRefuseDialog()

    def setStep(self, step):
        self.__currentStep = step
        self.__applyStep(self.__currentStep)

    def goNextStep(self):
        nextStep = self.__currentStep + 1
        if nextStep >= len(self.STEPS_NAMES.ALL):
            self.__saveFilters(False, True)
            self.destroy()
        else:
            self.__currentStep = nextStep
            self.__applyStep(self.__currentStep)

    def goPrevStep(self):
        prevStep = self.__currentStep - 1
        if prevStep >= 0:
            self.__currentStep = prevStep
            self.__applyStep(self.__currentStep)

    def _populate(self):
        super(HeaderTutorialWindow, self)._populate()
        self.__applyStep(self.__currentStep)

    def _dispose(self):
        self.__resetHighlightControls()
        super(HeaderTutorialWindow, self)._dispose()

    def __dialogCallback(self, isRefused, showNextTime):
        if isRefused:
            self.__saveFilters(isRefused and not showNextTime, False)
            self.destroy()
        else:
            self.__highlightControls()

    def __highlightControls(self):
        currentStep = self.STEPS_NAMES.ALL[self.__currentStep]
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIGHLIGHT_TUTORIAL_CONTROL, ctx={'currentStep': currentStep}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __resetHighlightControls(self):
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.RESET_HIGHLIGHT_TUTORIAL_CONTROL), scope=EVENT_BUS_SCOPE.LOBBY)

    def __showRefuseDialog(self):
        self.__resetHighlightControls()
        DialogsInterface.showDialog(RefuseHeaderTutorialDialogMeta(), self.__dialogCallback)

    def __applyStep(self, step):
        data = self.__getStepData(step)
        self.__highlightControls()
        self.as_setDataS(data)

    def __saveFilters(self, isRefused, isFinished):
        AccountSettings.setFilter(HEADER_TUTORIAL, {'step': self.__currentStep,
         'isRefused': isRefused,
         'isFinished': isFinished})

    def __getStepData(self, currentStep):
        stateStr = self.STEPS_NAMES.ALL[currentStep]
        windowTitle = i18n.makeString(DIALOGS.HEADERTUTORIALWINDOW_WINDOWTITLE_INTUTORIAL)
        if stateStr == self.STEPS_NAMES.WELCOME:
            windowTitle = i18n.makeString(DIALOGS.HEADERTUTORIALWINDOW_WINDOWTITLE_WELCOME)
        return {'windowTitle': windowTitle,
         'title': i18n.makeString(DIALOGS.headertutorialwindow_title(stateStr)),
         'state': stateStr,
         'text': i18n.makeString(DIALOGS.headertutorialwindow_maintext(stateStr))}
