# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_view.py
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_parameters import IVehCompareView, VehCompareBasketParamsCache
from gui.Scaleform.daapi.view.meta.VehicleCompareViewMeta import VehicleCompareViewMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control import getVehicleComparisonBasketCtrl
from gui.game_control.veh_comparison_basket import MAX_VEHICLES_TO_COMPARE_COUNT
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import selectVehicleInHangar, showVehiclePreview
from gui.shared.formatters import text_styles
from gui.shared.items_parameters.params_helper import getAllParametersTitles
from helpers.i18n import makeString as _ms
_BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORE: 'shop',
 VIEW_ALIAS.LOBBY_RESEARCH: 'researchTree',
 VIEW_ALIAS.LOBBY_TECHTREE: 'researchTree'}

class VehicleCompareView(LobbySubView, VehicleCompareViewMeta):
    __background_alpha__ = 0.0

    def __init__(self, ctx=None):
        super(VehicleCompareView, self).__init__(ctx)
        self.__vehDP = None
        self.__paramsCache = None
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
        return

    def closeView(self):
        self.onBackClick()

    def onSelectModulesClick(self, vehicleID, index):
        g_eventBus.handleEvent(events.LoadViewEvent(VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_WINDOW, ctx={'vehCD': int(vehicleID),
         'index': int(index)}), EVENT_BUS_SCOPE.LOBBY)

    def onRemoveAllVehicles(self):
        getVehicleComparisonBasketCtrl().removeAllVehicles()

    def onRemoveVehicle(self, index):
        getVehicleComparisonBasketCtrl().removeVehicleByIdx(int(index))

    def onCrewLevelChanged(self, index, crewLevelID):
        getVehicleComparisonBasketCtrl().setVehicleCrew(int(index), int(crewLevelID))

    def onGoToPreviewClick(self, vehicleID):
        showVehiclePreview(int(vehicleID), VIEW_ALIAS.VEHICLE_COMPARE)

    def onGoToHangarClick(self, vehicleID):
        selectVehicleInHangar(int(vehicleID))

    def onParamDeltaRequested(self, index, paramID):
        deltas = self.__paramsCache.getParametersDelta(int(index), paramID)
        self.as_setParamsDeltaS({'paramID': paramID,
         'deltas': deltas})

    def onBackClick(self):
        event = g_entitiesFactories.makeLoadEvent(self.__backAlias)
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(VehicleCompareView, self)._populate()
        self.as_setStaticDataS({'header': self.__getHeaderData()})
        self.as_setVehicleParamsDataS(getAllParametersTitles())
        self.__vehDP = VehiclesDataProvider()
        self.__vehDP.setFlashObject(self.as_getVehiclesDPS())
        self.__paramsCache = VehCompareBasketParamsCache(self.__vehDP)
        self.__updateUI()
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange += self.__updateUI
        comparisonBasket.onSwitchChange += self.__onComparingDisabled

    def _dispose(self):
        super(VehicleCompareView, self)._dispose()
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange -= self.__updateUI
        comparisonBasket.onSwitchChange -= self.__onComparingDisabled
        self.__paramsCache.dispose()
        self.__paramsCache = None
        self.__vehDP.fini()
        self.__vehDP = None
        return

    def __updateUI(self, *data):
        self.as_setVehiclesCountTextS(text_styles.main(_ms(VEH_COMPARE.VEHICLECOMPAREVIEW_TOPPANEL_VEHICLESCOUNT, count=text_styles.stats(getVehicleComparisonBasketCtrl().getVehiclesCount()))))

    def __onComparingDisabled(self):
        """
        gui.game_control.VehComparisonBasket.onSwitchChange event handler
        """
        self.destroy()

    def __getHeaderData(self):
        key = _BACK_BTN_LABELS.get(self.__backAlias, 'hangar')
        backBtnDescrLabel = '#veh_compare:header/backBtn/descrLabel/{}'.format(key)
        return {'closeBtnLabel': VEH_COMPARE.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': VEH_COMPARE.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': backBtnDescrLabel,
         'titleText': text_styles.promoTitle(VEH_COMPARE.VEHICLECOMPAREVIEW_HEADER)}


class VehiclesDataProvider(ListDAAPIDataProvider, IVehCompareView):

    def __init__(self):
        super(VehiclesDataProvider, self).__init__()
        self.__list = []

    @property
    def sortedCollection(self):
        return self.collection

    @property
    def collection(self):
        return self.__list

    def emptyItem(self):
        return None

    def buildList(self, *args):
        self.__list = args[0] if args else []
        if len(self.__list) < MAX_VEHICLES_TO_COMPARE_COUNT:
            self.__list.append({'isFirstEmptySlot': True})
        self.refresh()

    def updateItems(self, *args):
        data = args[0]
        self.refreshRandomItems(range(0, len(data)), data)

    def clear(self):
        self.__list = []

    def fini(self):
        self.clear()
        self._dispose()
