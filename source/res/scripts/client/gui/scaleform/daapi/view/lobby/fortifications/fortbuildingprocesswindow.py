# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingProcessWindow.py
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from FortifiedRegionBase import BuildingDescr
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortBuildingProcessWindowMeta import FortBuildingProcessWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.shared.fortifications.context import BuildingCtx
from gui.shared.utils import CONST_CONTAINER
from helpers import i18n

class FortBuildingProcessWindow(AbstractWindowView, View, FortBuildingProcessWindowMeta, FortViewHelper, AppRef):

    class BUILDING_STATUS(CONST_CONTAINER):
        BUILT = 1
        NOT_AVAILABLE = 2
        AVAILABLE = 3

    def __init__(self, ctx = None):
        super(FortBuildingProcessWindow, self).__init__()
        self.__buildingDirection = ctx.get('buildingDirection')
        self.__buildingPosition = ctx.get('buildingPosition')

    def _populate(self):
        super(FortBuildingProcessWindow, self)._populate()
        self.startFortListening()
        self.__makeData()

    def _dispose(self):
        self.stopFortListening()
        super(FortBuildingProcessWindow, self)._dispose()

    def onWindowClose(self):
        self.destroy()

    def onUpdated(self, isFullUpdate):
        self.__makeData()

    def onDirectionClosed(self, dir):
        if self.__buildingDirection == dir:
            self.destroy()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if reason == BUILDING_UPDATE_REASON.ADDED and ctx.get('dir') == self.__buildingDirection and ctx.get('pos') == self.__buildingPosition:
            self.destroy()

    def requestBuildingInfo(self, uid):
        infoData = {}
        id = self.UI_BUILDINGS_BIND.index(uid)
        buildingStatus = self.__getBuildingStatus(id)
        infoData['buildingName'] = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(FORTIFICATIONS.buildings_buildingname(uid)))
        infoData['buildingID'] = uid
        infoData['longDescr'] = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.buildingsprocess_longdescr(uid)))
        buttonLbl = FORTIFICATIONS.BUILDINGSPROCESS_BUTTONLBL
        if buildingStatus == self.BUILDING_STATUS.BUILT:
            buttonLbl = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_BUTTONLBLBUILT))
        infoData['buttonLabel'] = i18n.makeString(buttonLbl)
        infoData['orderInfo'] = self.__makeOrderInfoData(uid)
        statusIcon = ''
        isVisibleBtn = True
        isEnableBtn = True
        statusMsg = ''
        statusIconTooltip = None
        buttonTooltip = None
        if buildingStatus == self.BUILDING_STATUS.BUILT:
            statusMsg = self.app.utilsManager.textManager.concatStyles(((TextIcons.CHECKMARK_ICON,), (TextType.SUCCESS_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_BUILT))))
            statusIcon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK
            isEnableBtn = False
            isVisibleBtn = False
            statusIconTooltip = self.__makeStatusTooltip(True)
            buttonTooltip = self.__makeButtonTooltip(self.BUILDING_STATUS.BUILT, None)
        elif buildingStatus == self.BUILDING_STATUS.NOT_AVAILABLE:
            isEnableBtn = False
            isVisibleBtn = True
            statusMsg = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_BUILDINGINFO_STATUSMESSAGE))
            imageSource = self.app._utilsMgr.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_REDNOTAVAILABLE, 12, 12, 0, 0))
            statusMsg = imageSource + ' ' + statusMsg
            statusIconTooltip = self.__makeStatusTooltip(False)
            buttonTooltip = self.__makeButtonTooltip(self.BUILDING_STATUS.NOT_AVAILABLE, None)
        else:
            buttonTooltip = self.__makeButtonTooltip(self.BUILDING_STATUS.AVAILABLE, i18n.makeString(FORTIFICATIONS.buildings_buildingname(uid)))
        infoData['isVisibleBtn'] = isVisibleBtn
        infoData['isEnableBtn'] = isEnableBtn
        infoData['statusMsg'] = statusMsg
        infoData['statusIconTooltip'] = statusIconTooltip
        infoData['buttonTooltip'] = buttonTooltip
        self.as_responseBuildingInfoS(infoData)
        return

    def __makeButtonTooltip(self, status, buildingName = None):
        result = {}
        header = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNENABLED_HEADER, buildingName=buildingName)
        body = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNENABLED_BODY)
        if status == self.BUILDING_STATUS.BUILT:
            header = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNDISABLEDBUILT_HEADER)
            body = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNDISABLEDBUILT_BODY)
        elif status == self.BUILDING_STATUS.NOT_AVAILABLE:
            header = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNDISABLEDNOTAVAILABLE_HEADER)
            body = i18n.makeString(TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_BTNDISABLEDNOTAVAILABLE_BODY)
        result['header'] = header
        result['body'] = body
        return result

    def __makeStatusTooltip(self, value):
        result = TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_STATUSICONSUCCESS
        if not value:
            result = TOOLTIPS.FORTIFICATION_BUILDINGPROCESS_STATUSICONNOTAVAILABLE
        return result

    def __makeOrderInfoData(self, uid):
        self._buildingID = self.UI_BUILDINGS_BIND.index(uid)
        self._orderID = self.fortCtrl.getFort().getBuildingOrder(self._buildingID)
        orderTitle = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(self.UI_ORDERS_BIND[self._orderID])))
        descrMSG = i18n.makeString(FORTIFICATIONS.buildings_processorderinfo(uid))
        descrMSG = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, descrMSG)
        result = {}
        result['title'] = orderTitle
        result['description'] = descrMSG
        buildingId = self.UI_BUILDINGS_BIND.index(uid)
        buildingDescr = self.fortCtrl.getFort().getBuilding(self.UI_BUILDINGS_BIND.index(uid), BuildingDescr(typeID=buildingId))
        order = self.fortCtrl.getFort().getOrder(buildingDescr.typeRef.orderType)
        result['iconSource'] = order.icon
        result['showAlertIcon'] = self._showOrderAlertIcon(order)
        result['iconLevel'] = None
        return result

    def applyBuildingProcess(self, uid):
        self.__requesToCreate(uid)

    @process
    def __requesToCreate(self, uid):
        buildingTypeID = self.UI_BUILDINGS_BIND.index(uid)
        result = yield self.fortProvider.sendRequest(BuildingCtx(buildingTypeID, self.__buildingDirection, self.__buildingPosition, waitingID='fort/building/add'))
        if result:
            g_fortSoundController.playCreateBuilding()
            building = self.fortCtrl.getFort().getBuilding(buildingTypeID)
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_BUILDINGPROCESS, buildingName=building.userName, type=SystemMessages.SM_TYPE.Warning)
        self.destroy()

    def __makeData(self):
        result = {}
        result['listItems'] = self.__makeListData()
        result['availableCount'] = self.__makeMainLabel()
        result['windowTitle'] = FORTIFICATIONS.BUILDINGSPROCESS_WINDOWTITLE
        result['textInfo'] = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_TEXTINFO))
        self.as_setDataS(result)

    def __makeListData(self):
        result = []
        for id in self.BUILDINGS:
            uid = self.UI_BUILDINGS_BIND[id]
            id, name, shortDescr, statusMsg, status = self.__getStrings(uid, self.__getBuildingStatus(id))
            result.append(self.__listFields(id, name, shortDescr, statusMsg, status))

        return result

    def __getStrings(self, value, status):
        id = value
        name = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.buildings_buildingname(id)))
        shortDescr = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.buildingsprocess_shortdescr(id)))
        statusMsg = ''
        if status == self.BUILDING_STATUS.AVAILABLE:
            return (id,
             name,
             shortDescr,
             statusMsg,
             status)
        iconType = TextIcons.CHECKMARK_ICON
        textColor = TextType.SUCCESS_TEXT
        statusType = FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_BUILT
        if status == self.BUILDING_STATUS.NOT_AVAILABLE:
            iconType = TextIcons.NOT_AVAILABLE
            textColor = TextType.STANDARD_TEXT
            statusType = FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_NOTAVAILABLE
        statusMsg = self.app.utilsManager.textManager.concatStyles(((iconType,), (textColor, i18n.makeString(statusType))))
        return (id,
         name,
         shortDescr,
         statusMsg,
         status)

    def __listFields(self, id, name, shortDescr, status, buildingStatus):
        return {'buildingID': id,
         'buildingName': name,
         'shortDescr': shortDescr,
         'statusLbl': status,
         'buildingStatus': buildingStatus}

    def __makeMainLabel(self):
        buildingCount = len(self.fortCtrl.getFort().buildings) - 1
        countColor = TextType.NEUTRAL_TEXT
        if buildingCount == 0:
            countColor = TextType.STANDARD_TEXT
        currentCount = self.app.utilsManager.textManager.getText(countColor, buildingCount)
        msg = i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_MAINLABEL_ACCESSCOUNT, current=currentCount, total=len(self.BUILDINGS))
        msg = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, msg)
        return msg

    def __getBuildingStatus(self, buildingTypeID):
        if buildingTypeID in self.fortCtrl.getFort().buildings:
            return self.BUILDING_STATUS.BUILT
        elif self.fortCtrl.getLimits().canBuild(buildingTypeID):
            return self.BUILDING_STATUS.AVAILABLE
        else:
            return self.BUILDING_STATUS.NOT_AVAILABLE
