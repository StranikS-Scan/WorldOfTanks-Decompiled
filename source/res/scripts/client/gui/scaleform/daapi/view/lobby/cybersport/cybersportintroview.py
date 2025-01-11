# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportIntroView.py
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from helpers.i18n import makeString as _ms
from account_helpers.AccountSettings import SELECTED_INTRO_VEHICLES_FIELD
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME as _VCN
from gui.shared.events import CSVehicleSelectEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeIntroVehicleVO
from gui.Scaleform.daapi.view.meta.CyberSportIntroMeta import CyberSportIntroMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from nation_change_helpers.client_nation_change_helper import getValidVehicleCDForNationChange
from skeletons.gui.shared import IItemsCache
_ACCEPTED_VEH_TYPES = (_VCN.LIGHT_TANK, _VCN.MEDIUM_TANK, _VCN.HEAVY_TANK)

class _IntroViewVO(object):

    def __init__(self):
        self.__data = {'teamDescriptionText': '',
         'isTeamDescriptionTooltip': False,
         'teamDescriptionTooltip': '',
         'createBtnLabel': '',
         'createBtnTooltip': '',
         'isCreateBtnEnabled': False,
         'isCreateBtnVisible': False,
         'isCanCreateBattle': False,
         'isCanJoinBattle': False,
         'isNeedAddPlayers': False,
         'isHaveTeamToShow': False}

    def getData(self):
        return self.__data

    def showCreateButton(self, label, tooltip, enabled=True):
        self.__data['isCreateBtnVisible'] = True
        self.__data['isCreateBtnEnabled'] = enabled
        self.__data['createBtnLabel'] = label
        self.__data['createBtnTooltip'] = tooltip

    def moveToTheUnitByCreateButton(self):
        self.__data['isCanCreateBattle'] = self.__data['isCanJoinBattle'] = True

    def needAddPlayers(self):
        self.__data['isNeedAddPlayers'] = True

    def fillDefault(self):
        self.showCreateButton(_ms(CYBERSPORT.INTROVIEW_RIGHTBLOCK_BTNLABEL), '', enabled=True)


class CyberSportIntroView(CyberSportIntroMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def showSelectorPopup(self):
        rosterSettings = self.prbEntity.getRosterSettings()
        self._currentVehCD = -1
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY), ctx={'isMultiSelect': False,
         'infoText': CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_INTRO,
         'titleText': CYBERSPORT.WINDOW_VEHICLESELECTOR_TITLE,
         'selectButton': CYBERSPORT.WINDOW_VEHICLESELECTOR_BUTTONS_SELECT,
         'cancelButton': CYBERSPORT.WINDOW_VEHICLESELECTOR_BUTTONS_CANCEL,
         'compatibleOnlyLabel': CYBERSPORT.WINDOW_VEHICLESELECTOR_FILTERS_MATCHES,
         'componentsOffset': 45,
         'selectedVehicles': self.__getSelectedVehicles(),
         'section': 'cs_intro_view_vehicle',
         'levelsRange': rosterSettings.getLevelsRange(),
         'vehicleTypes': _ACCEPTED_VEH_TYPES}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(CyberSportIntroView, self)._populate()
        self.addListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        data = {'titleLblText': text_styles.promoTitle(CYBERSPORT.WINDOW_INTRO_TITLE),
         'descrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_DESCRIPTION),
         'listRoomTitleLblText': text_styles.promoSubTitle(CYBERSPORT.WINDOW_INTRO_SEARCH_TITLE),
         'listRoomDescrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_SEARCH_DESCRIPTION),
         'listRoomBtnLabel': _ms(CYBERSPORT.WINDOW_INTRO_SEARCH_BTN),
         'autoTitleLblText': text_styles.middleTitle(CYBERSPORT.WINDOW_INTRO_AUTO_TITLE),
         'autoDescrLblText': text_styles.main(CYBERSPORT.WINDOW_INTRO_AUTO_DESCRIPTION),
         'vehicleBtnTitleTfText': text_styles.standard(CYBERSPORT.BUTTON_CHOOSEVEHICLES_SELECTED),
         'rightBlockHeader': text_styles.promoSubTitle(CYBERSPORT.INTROVIEW_RIGHTBLOCK_HEADER),
         'rightBlockDescr': text_styles.main(CYBERSPORT.INTROVIEW_RIGHTBLOCK_DESCR),
         'rightBlockBtnLbl': _ms(CYBERSPORT.INTROVIEW_RIGHTBLOCK_BTNLABEL)}
        self.as_setTextsS(data)
        self.__checkSelectedVehicles()
        self.__updateAutoSearchVehicle(self.__getSelectedVehicles())

    def _dispose(self):
        self.removeListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(CyberSportIntroView, self)._dispose()

    def __checkSelectedVehicles(self):
        vehsIntCD = self.__getSelectedVehicles()
        if vehsIntCD:
            vehIntCD = vehsIntCD[0]
            vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
            if not vehicle.activeInNationGroup:
                vehIntCD = getValidVehicleCDForNationChange(vehIntCD)
                self.prbEntity.setSelectedVehicles(SELECTED_INTRO_VEHICLES_FIELD, [vehIntCD])

    def __onCacheResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                for vehIntCD in vehDiff:
                    vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
                    if not vehicle.activeInNationGroup and self._currentVehCD == vehIntCD:
                        itemCD = iterVehTypeCDsInNationGroup(vehicle.intCD).next()
                        self.__setSelectedVehicle(itemCD)

            return

    def __updateSelectedVehicles(self, event):
        if event.ctx:
            vehIntCD = int(event.ctx[0])
            self.__setSelectedVehicle(vehIntCD)

    def __setSelectedVehicle(self, vehIntCD):
        self.prbEntity.setSelectedVehicles(SELECTED_INTRO_VEHICLES_FIELD, [vehIntCD])
        self.__updateAutoSearchVehicle([vehIntCD])

    def __updateAutoSearchVehicle(self, vehsIntCD):
        if vehsIntCD:
            vehIntCD = vehsIntCD[0]
            vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
            levelsRange = self.prbEntity.getRosterSettings().getLevelsRange()
            if vehicle.level not in levelsRange:
                isReadyVehicle = False
                warnTooltip = TOOLTIPS.CYBERSPORT_INTRO_SELECTEDVEHICLEWARN_INCOMPATIBLELEVEL
            elif vehicle.type not in _ACCEPTED_VEH_TYPES:
                isReadyVehicle = False
                warnTooltip = TOOLTIPS.CYBERSPORT_INTRO_SELECTEDVEHICLEWARN_INCOMPATIBLETYPE
            elif vehicle.isOnlyForEpicBattles or vehicle.isOnlyForBob:
                isReadyVehicle = False
                warnTooltip = TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_EVENTVEHICLEWRONGMODE
            else:
                warnTooltip, isReadyVehicle = '', vehicle.isReadyToPrebattle()
            self._currentVehCD = vehIntCD
            self.as_setSelectedVehicleS(makeIntroVehicleVO(vehicle, isReadyVehicle, warnTooltip))
        else:
            self.as_setNoVehiclesS(TOOLTIPS.CYBERSPORT_NOVEHICLESINHANGAR)

    def __getSelectedVehicles(self):
        return self.prbEntity.getSelectedVehicles(SELECTED_INTRO_VEHICLES_FIELD)
