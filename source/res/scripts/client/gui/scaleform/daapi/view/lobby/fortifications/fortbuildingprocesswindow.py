# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingProcessWindow.py
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from FortifiedRegionBase import BuildingDescr
from adisp import process
from account_helpers.AccountSettings import AccountSettings, DEFAULT_VALUES
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortBuildingProcessWindowMeta import FortBuildingProcessWindowMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.fortifications.context import BuildingCtx
from gui.shared.formatters import icons, text_styles
from shared_utils import CONST_CONTAINER
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from helpers import i18n

class FortBuildingProcessWindow(FortBuildingProcessWindowMeta, FortViewHelper):

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
        id = self.getBuildingIDbyUID(uid)
        self.__markAsVisited(id)
        buildingStatus = self.__getBuildingStatus(id)
        infoData['buildingName'] = text_styles.highTitle(i18n.makeString(FORTIFICATIONS.buildings_buildingname(uid)))
        infoData['buildingID'] = uid
        infoData['longDescr'] = text_styles.standard(i18n.makeString(FORTIFICATIONS.buildingsprocess_longdescr(uid)))
        buttonLbl = FORTIFICATIONS.BUILDINGSPROCESS_BUTTONLBL
        if buildingStatus == self.BUILDING_STATUS.BUILT:
            buttonLbl = text_styles.standard(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_BUTTONLBLBUILT))
        infoData['buttonLabel'] = i18n.makeString(buttonLbl)
        infoData['orderInfo'] = self.__makeOrderInfoData(uid)
        isVisibleBtn = True
        isEnableBtn = True
        statusMsg = ''
        statusIconTooltip = None
        if buildingStatus == self.BUILDING_STATUS.BUILT:
            statusMsg = ''.join((icons.checkmark(), text_styles.success(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_BUILT))))
            isEnableBtn = False
            isVisibleBtn = False
            statusIconTooltip = self.__makeStatusTooltip(True)
            buttonTooltip = self.__makeButtonTooltip(self.BUILDING_STATUS.BUILT, None)
        elif buildingStatus == self.BUILDING_STATUS.NOT_AVAILABLE:
            isEnableBtn = False
            isVisibleBtn = True
            statusMsg = text_styles.error(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_BUILDINGINFO_STATUSMESSAGE))
            imageSource = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_REDNOTAVAILABLE, 12, 12, 0, 0)
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
        buildingIcon = FortViewHelper.getPopoverIconSource(uid, FORT_BATTLE_DIVISIONS.ABSOLUTE.maxFortLevel)
        infoData['buildingIcon'] = buildingIcon
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
        self._buildingID = self.getBuildingIDbyUID(uid)
        self._orderID = self.fortCtrl.getFort().getBuildingOrder(self._buildingID)
        orderTitle = text_styles.middleTitle(i18n.makeString(FORTIFICATIONS.orders_orderpopover_ordertype(self.getOrderUIDbyID(self._orderID))))
        descrMSG = i18n.makeString(FORTIFICATIONS.buildings_processorderinfo(uid))
        descrMSG = text_styles.main(descrMSG)
        result = {}
        result['title'] = orderTitle
        result['description'] = descrMSG
        buildingId = self.getBuildingIDbyUID(uid)
        buildingDescr = self.fortCtrl.getFort().getBuilding(self.getBuildingIDbyUID(uid), BuildingDescr(typeID=buildingId))
        order = self.fortCtrl.getFort().getOrder(buildingDescr.typeRef.orderType)
        result['iconSource'] = order.icon
        showAlertIcon, alertIconTooltip = self._showOrderAlertIcon(order)
        result['showAlertIcon'] = showAlertIcon
        result['alertIconTooltip'] = alertIconTooltip
        result['iconLevel'] = None
        return result

    def applyBuildingProcess(self, uid):
        self.__requesToCreate(uid)

    @process
    def __requesToCreate(self, uid):
        buildingTypeID = self.getBuildingIDbyUID(uid)
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
        result['textInfo'] = text_styles.highTitle(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_TEXTINFO))
        self.as_setDataS(result)

    def __makeListData(self):
        result = []
        for buildTypeID in self.BUILDINGS:
            uid = self.getBuildingUIDbyID(buildTypeID)
            wtfID, name, shortDescr, statusMsg, status = self.__getStrings(uid, self.__getBuildingStatus(buildTypeID))
            result.append(self.__listFields(wtfID, name, shortDescr, statusMsg, status, self.__isNewBuilding(buildTypeID)))

        return result

    def __getStrings(self, value, status):
        id = value
        name = text_styles.middleTitle(i18n.makeString(FORTIFICATIONS.buildings_buildingname(id)))
        shortDescr = text_styles.standard(i18n.makeString(FORTIFICATIONS.buildingsprocess_shortdescr(id)))
        statusMsg = ''
        if status == self.BUILDING_STATUS.AVAILABLE:
            return (id,
             name,
             shortDescr,
             statusMsg,
             status)
        if status == self.BUILDING_STATUS.NOT_AVAILABLE:
            icon = icons.notAvailable()
            statusMsg = text_styles.standard(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_NOTAVAILABLE))
        else:
            icon = icons.checkmark()
            statusMsg = text_styles.success(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_STATUSMSG_BUILT))
        statusMsg = ''.join((icon, statusMsg))
        return (id,
         name,
         shortDescr,
         statusMsg,
         status)

    def __listFields(self, id, name, shortDescr, status, buildingStatus, isNewItem):
        return {'buildingID': id,
         'buildingName': name,
         'shortDescr': shortDescr,
         'statusLbl': status,
         'buildingStatus': buildingStatus,
         'isNewItem': isNewItem,
         'buildingIcon': FortViewHelper.getSmallIconSource(id, FORT_BATTLE_DIVISIONS.ABSOLUTE.maxFortLevel)}

    def __makeMainLabel(self):
        buildingCount = len(self.fortCtrl.getFort().buildings) - 1
        formatter = text_styles.neutral
        if buildingCount == 0:
            formatter = text_styles.standard
        return text_styles.standard(i18n.makeString(FORTIFICATIONS.BUILDINGSPROCESS_MAINLABEL_ACCESSCOUNT, current=formatter(buildingCount), total=len(self.BUILDINGS)))

    def __getBuildingStatus(self, buildingTypeID):
        if buildingTypeID in self.fortCtrl.getFort().buildings:
            return self.BUILDING_STATUS.BUILT
        elif self.fortCtrl.getLimits().canBuild(buildingTypeID):
            return self.BUILDING_STATUS.AVAILABLE
        else:
            return self.BUILDING_STATUS.NOT_AVAILABLE

    @classmethod
    def __isNewBuilding(cls, buildTypeID):
        fortSettings = dict(AccountSettings.getSettings('fortSettings'))
        if 'visitedBuildings' not in fortSettings:
            fortSettings['visitedBuildings'] = DEFAULT_VALUES['settings']['fortSettings']['visitedBuildings']
        return buildTypeID not in fortSettings['visitedBuildings']

    @classmethod
    def __markAsVisited(cls, buildTypeID):
        fortSettings = dict(AccountSettings.getSettings('fortSettings'))
        if 'visitedBuildings' not in fortSettings:
            fortSettings['visitedBuildings'] = DEFAULT_VALUES['settings']['fortSettings']['visitedBuildings']
        fortSettings['visitedBuildings'].add(buildTypeID)
        AccountSettings.setSettings('fortSettings', fortSettings)
