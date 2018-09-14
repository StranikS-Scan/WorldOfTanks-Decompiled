# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/DemountBuildingWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from gui import SystemMessages
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.DemountBuildingWindowMeta import DemountBuildingWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as ALIAS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.fortifications.context import BuildingCtx
from helpers import i18n

class DemountBuildingWindow(AbstractWindowView, View, DemountBuildingWindowMeta, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(DemountBuildingWindow, self).__init__()
        self.__buildingID = ctx.get('data', None)
        self.__formattedBuildingName = i18n.makeString(ALIAS.buildings_buildingname(self.__buildingID))
        buildingDescr = self.fortCtrl.getFort().getBuilding(self.UI_BUILDINGS_BIND.index(self.__buildingID))
        self.__buildingLevel = buildingDescr.level
        self.__currHpVal = buildingDescr.hp
        self.__buildingIntID = buildingDescr.typeID
        self.__inputChecker = None
        return

    def _populate(self):
        super(DemountBuildingWindow, self)._populate()
        self.startFortListening()
        self.update()

    def update(self):
        self.as_setDataS(self.__makeData())

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.stopFortListening()
        self.__buildingIntID = None
        self.__buildingID = None
        self.__formattedBuildingName = None
        self.__buildingLevel = None
        self.__currHpVal = None
        self.__inputChecker = None
        super(DemountBuildingWindow, self)._dispose()
        return

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if self.__buildingIntID == buildingTypeID and reason == BUILDING_UPDATE_REASON.DELETED:
            self.destroy()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__inputChecker = viewPy
        self.initInputChecker()

    def onUpdated(self, isFullUpdate):
        if isFullUpdate and self.fortCtrl.getFort().getBuilding(self.__buildingIntID) is None:
            self.destroy()
        else:
            self.update()
        return

    def initInputChecker(self):
        self.__inputChecker.errorMsg = self.__makeInputCheckerError()
        self.__inputChecker.questionTitle = self.__makeInputCheckerTitle()
        self.__inputChecker.questionBody = self.__makeInputCheckerBody()
        self.__inputChecker.setControlNumbers(self.__currHpVal, BigWorld.wg_getIntegralFormat)

    def __makeData(self):
        return {'windowTitle': self.__makeWindowTitle(),
         'headerQuestion': self.__makeTitle(),
         'bodyText': self.__makeBody(),
         'applyButtonLbl': ALIAS.DEMOUNTBUILDING_APPLYBUTTON_LABEL,
         'cancelButtonLbl': ALIAS.DEMOUNTBUILDING_CANCELBUTTON_LABEL}

    def __makeWindowTitle(self):
        return i18n.makeString(ALIAS.DEMOUNTBUILDING_WINDOWTITLE, buildingName=self.__formattedBuildingName)

    def __makeTitle(self):
        text = i18n.makeString(ALIAS.DEMOUNTBUILDING_GENERALTEXT_TITLE, buildingName=self.__formattedBuildingName, buildingLevel=fort_formatters.getTextLevel(self.__buildingLevel))
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, text)

    def __makeBody(self):
        text = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(ALIAS.DEMOUNTBUILDING_GENERALTEXT_BODYINNERTEXT))
        concatTexts = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(ALIAS.DEMOUNTBUILDING_GENERALTEXT_BODY, bodyInnerText=text))
        return concatTexts

    def __makeInputCheckerTitle(self):
        return self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(ALIAS.DEMOUNTBUILDING_QUESTION_TITLE))

    def __makeInputCheckerBody(self):
        controlNumber = BigWorld.wg_getIntegralFormat(self.__currHpVal)
        controlNumber = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, str(controlNumber))
        questionBody = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(ALIAS.DEMOUNTBUILDING_QUESTION_BODY, controlNumber=controlNumber))
        return questionBody

    def __makeInputCheckerError(self):
        return self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(ALIAS.DEMOUNTBUILDING_ERRORMESSAGE))

    def applyDemount(self):
        self.__requestToDelete()

    @process
    def __requestToDelete(self):
        buildingTypeID = self.UI_BUILDINGS_BIND.index(self.__buildingID)
        building = self.fortCtrl.getFort().getBuilding(buildingTypeID)
        result = yield self.fortProvider.sendRequest(BuildingCtx(buildingTypeID, isAdd=False, waitingID='fort/building/delete'))
        if result:
            g_fortSoundController.playDeleteBuilding()
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DEMOUNTBUILDING, buildingName=building.userName, type=SystemMessages.SM_TYPE.Warning)
        self.destroy()

    def __updateInputChecker(self):
        self.__inputChecker.questionBody = self.__makeInputCheckerBody()
        self.__inputChecker.setControlNumbers(self.__currHpVal, BigWorld.wg_getIntegralFormat)
