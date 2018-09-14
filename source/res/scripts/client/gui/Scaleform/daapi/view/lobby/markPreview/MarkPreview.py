# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/markPreview/MarkPreview.py
from collections import namedtuple
import BigWorld
import ResMgr
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui.Scaleform.daapi.view.meta.MarkPreviewMeta import MarkPreviewMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.Scaleform.genConsts.MARKPREVIEW_CONSTANTS import MARKPREVIEW_CONSTANTS
from gui.shared import event_dispatcher, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi import LobbySubView
from gui.shared.tooltips import ToolTipBaseData
from gui.shared.utils.functions import makeTooltip
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.shared.events import LobbySimpleEvent
from gui.shared.utils.HangarSpace import g_hangarSpace
from HangarVehicle import HangarVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
TAB_ORDER = [FACT_SHEET_TAB_ID, CREW_INFO_TAB_ID]
TAB_DATA_MAP = {FACT_SHEET_TAB_ID: (MARKPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, MENU.HANGAR_MARKPREVIEW_INFOBUTTON),
 CREW_INFO_TAB_ID: (MARKPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, MENU.HANGAR_MARKPREVIEW_CREWBUTTON)}
_ButtonState = namedtuple('_ButtonState', 'enabled, price, label, isAction, currencyIcon, actionType, action')

class MarkPreview(LobbySubView, MarkPreviewMeta):
    __background_alpha__ = 0.0

    def __init__(self, ctx=None):
        super(MarkPreview, self).__init__(ctx)
        self.__selected3DEntityFromHangar = ctx['entity3d']
        self.__selected3dEntityWhileClicked = None
        self.__selected3DEntity = None
        self.__isCursorOver3dScene = False
        self.__isObjectClicked = False
        return

    def _populate(self):
        super(MarkPreview, self)._populate()
        self.as_setStaticDataS(self.__getStaticData())
        self.__fullUpdate()
        self.fireEvent(events.Mark1PreviewEvent(events.Mark1PreviewEvent.MARK1_WINDOW_OPENED), EVENT_BUS_SCOPE.LOBBY)
        if self.__selected3DEntityFromHangar is not None:
            self.__selected3DEntityFromHangar.onReleased()
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntityFromHangar)
            self.__selected3DEntityFromHangar = None
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        g_hangarSpace.onObjectReleased += self.__on3DObjectReleased
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        return

    def _dispose(self):
        self.fireEvent(events.Mark1PreviewEvent(events.Mark1PreviewEvent.MARK1_WINDOW_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        ClientSelectableCameraObject.switchCamera()
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        g_hangarSpace.onObjectReleased -= self.__on3DObjectReleased
        self.__selected3dEntityWhileClicked = None
        if self.__selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        super(MarkPreview, self)._dispose()
        return

    def closeView(self):
        self.onBackClick()

    def onBackClick(self):
        event_dispatcher.showHangar()

    def onOpenInfoTab(self, index):
        AccountSettings.setSettings(PREVIEW_INFO_PANEL_IDX, index)

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self.__selected3DEntity is not None:
            if self.__isCursorOver3dScene:
                self.__highlight3DEntityAndShowTT(self.__selected3DEntity)
            else:
                self.__fade3DEntityAndHideTT(self.__selected3DEntity)
        return

    def __on3DObjectSelected(self, entity):
        if not self.__isObjectClicked:
            self.__selected3DEntity = entity
            if self.__isCursorOver3dScene:
                self.__highlight3DEntityAndShowTT(entity)
        else:
            self.__selected3dEntityWhileClicked = entity

    def __on3DObjectUnSelected(self, entity):
        self.__selected3DEntity = None
        self.__selected3dEntityWhileClicked = None
        if self.__isCursorOver3dScene:
            self.__fade3DEntityAndHideTT(entity)
        return

    def __on3DObjectClicked(self):
        self.__isObjectClicked = True
        if self.__isCursorOver3dScene:
            if self.__selected3DEntity is not None:
                self.__selected3DEntity.onClicked()
        return

    def __on3DObjectReleased(self):
        self.__isObjectClicked = False
        if self.__isCursorOver3dScene:
            if self.__selected3DEntity is not None:
                if isinstance(self.__selected3DEntity, HangarVehicle):
                    self.closeView()
                else:
                    self.__selected3DEntity.onReleased()
        if self.__selected3dEntityWhileClicked is not None:
            self.__on3DObjectSelected(self.__selected3dEntityWhileClicked)
            self.__selected3dEntityWhileClicked = None
        return

    def __highlight3DEntityAndShowTT(self, entity):
        entity.highlight(True)
        itemId = entity.selectionId
        if len(itemId) > 0:
            self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])

    def __fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)
        self.as_hide3DSceneTooltipS()

    def __fullUpdate(self):
        selectedTabInd = AccountSettings.getSettings(PREVIEW_INFO_PANEL_IDX)
        self.as_updateInfoDataS(self.__getInfoData(selectedTabInd))

    def __getStaticData(self):
        return {'header': self.__getHeaderData(),
         'bottomPanel': self.__getBottomPanelData(),
         'tabButtonsData': self.__packTabButtonsData(),
         'vehicleInfo': {}}

    def __getHeaderData(self):
        return {'closeBtnLabel': VEHICLE_PREVIEW.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': '',
         'backBtnDescrLabel': makeTooltip(TOOLTIPS.HANGAR_MARKPREVIEW_CLOSEBUTTON_HEADER, TOOLTIPS.HANGAR_MARKPREVIEW_CLOSEBUTTON_DESCRIPTION),
         'titleText': text_styles.promoTitle(MENU.HANGAR_MARKPREVIEW_HEADERTITLE)}

    def __getBottomPanelData(self):
        return {'buyingLabel': '',
         'modulesLabel': text_styles.middleTitle(MENU.HANGAR_MARKPREVIEW_MODULES),
         'isBuyingAvailable': False}

    def __getInfoData(self, selectedTabInd):
        return {'selectedTab': selectedTabInd,
         'tabData': self.__packTabData(),
         'nation': 'uk'}

    def __packTabButtonsData(self):
        data = []
        for id in TAB_ORDER:
            linkage, label = TAB_DATA_MAP[id]
            data.append({'label': label,
             'linkage': linkage})

        return data

    def __packTabData(self):
        return [self.__packDataItem(MARKPREVIEW_CONSTANTS.FACT_SHEET_DATA_CLASS_NAME, self.__packFactSheetData()), self.__packDataItem(MARKPREVIEW_CONSTANTS.FACT_SHEET_DATA_CLASS_NAME, self.__packCrewInfoData())]

    def __packCrewInfoData(self):
        return {'historicReferenceTxt': text_styles.stats(MENU.HANGAR_MARKPREVIEW_CREWINFO),
         'showNationFlag': True}

    def __packFactSheetData(self):
        return {'historicReferenceTxt': text_styles.stats(MENU.HANGAR_MARKPREVIEW_VEHICLEINFO),
         'showNationFlag': True}

    def __packDataItem(self, className, data):
        return {'voClassName': className,
         'voData': data}


_ENV_TOOLTIPS_PATH = '#tooltips:%s'
_ENV_IMAGES_PATH = '../maps/icons/markTooltips/%s.png'
_ENV_IMAGES_PATH_FOR_CHECK = 'gui/maps/icons/markTooltips/%s.png'

class MarkPreviewTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(MarkPreviewTooltipData, self).__init__(context, None)
        return

    def getDisplayableData(self, tooltipId):
        title = _ENV_TOOLTIPS_PATH % ('mark1/%s/header' % tooltipId)
        desc = _ENV_TOOLTIPS_PATH % ('mark1/%s/description' % tooltipId)
        icon = None
        if ResMgr.isFile(_ENV_IMAGES_PATH_FOR_CHECK % tooltipId):
            icon = _ENV_IMAGES_PATH % tooltipId
        return {'title': title,
         'text': desc,
         'icon': icon}
