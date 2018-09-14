# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ResearchPanel.py
from CurrentVehicle import g_currentVehicle
from constants import IGR_TYPE
from debug_utils import LOG_ERROR
from gui import game_control, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control import getVehicleComparisonBasketCtrl
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache, event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getTimeLeftStr
from gui.shared.gui_items.Vehicle import getLobbyDescription
from helpers import i18n

class ResearchPanel(ResearchPanelMeta):

    def _populate(self):
        super(ResearchPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.vehTypeXP': self.onVehicleTypeXPChanged,
         'stats.eliteVehicles': self.onVehicleBecomeElite})
        self.onCurrentVehicleChanged()
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange += self.__onCompareBasketChanged
        comparisonBasket.onSwitchChange += self.onCurrentVehicleChanged

    def _dispose(self):
        super(ResearchPanel, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange -= self.__onCompareBasketChanged
        comparisonBasket.onSwitchChange -= self.onCurrentVehicleChanged

    def goToResearch(self):
        if g_currentVehicle.isPresent():
            shared_events.showResearchView(g_currentVehicle.item.intCD)
        else:
            LOG_ERROR('Current vehicle is not preset')

    def addVehToCompare(self):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            getVehicleComparisonBasketCtrl().addVehicle(vehCD)

    def onCurrentVehicleChanged(self):
        if g_currentVehicle.isPresent():
            xps = g_itemsCache.items.stats.vehiclesXPs
            vehicle = g_currentVehicle.item
            xp = xps.get(vehicle.intCD, 0)
            self.as_updateCurrentVehicleS({'earnedXP': xp,
             'isElite': vehicle.isElite,
             'vehCompareData': self.__getVehCompareData(vehicle)})
        else:
            self.as_updateCurrentVehicleS({'earnedXP': 0})
        self.__onIgrTypeChanged()

    def __onIgrTypeChanged(self, *args):
        type = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if type == IGR_TYPE.PREMIUM else 'basic', {})
        label = text_styles.main(i18n.makeString(MENU.IGR_INFO, igrIcon=icon))
        self.as_setIGRLabelS(type != IGR_TYPE.NONE, label)
        self.__updateVehIGRStatus()

    def __updateVehIGRStatus(self):
        vehicleIgrTimeLeft = None
        igrType = game_control.g_instance.igr.getRoomType()
        if g_currentVehicle.isPresent() and g_currentVehicle.isPremiumIGR() and igrType == IGR_TYPE.PREMIUM:
            igrActionIcon = makeHtmlString('html_templates:igr/iconSmall', 'premium', {})
            localization = '#menu:vehicleIgr/%s'
            rentInfo = g_currentVehicle.item.rentInfo
            vehicleIgrTimeLeft = getTimeLeftStr(localization, rentInfo.getTimeLeft(), timeStyle=text_styles.stats, ctx={'igrIcon': igrActionIcon})
        self.as_actionIGRDaysLeftS(vehicleIgrTimeLeft is not None, text_styles.main(vehicleIgrTimeLeft))
        return

    def onVehicleTypeXPChanged(self, xps):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            if vehCD in xps:
                self.as_setEarnedXPS(xps[vehCD])

    def onVehicleBecomeElite(self, elite):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            if vehCD in elite:
                self.as_setEliteS(True)

    def __onCompareBasketChanged(self, changedData):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param changedData: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        if changedData.isFullChanged:
            self.onCurrentVehicleChanged()

    @staticmethod
    def __getVehCompareData(vehicle):
        comparisonBasket = getVehicleComparisonBasketCtrl()
        state, tooltip = resolveStateTooltip(comparisonBasket, vehicle, enabledTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, fullTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        return {'modeAvailable': comparisonBasket.isEnabled(),
         'btnEnabled': state,
         'btnTooltip': tooltip}
