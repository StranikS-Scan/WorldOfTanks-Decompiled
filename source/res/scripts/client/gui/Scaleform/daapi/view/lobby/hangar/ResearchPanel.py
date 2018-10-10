# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ResearchPanel.py
from CurrentVehicle import g_currentVehicle
from constants import IGR_TYPE
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getTimeLeftStr
from helpers import i18n, dependency
from skeletons.gui.game_control import IVehicleComparisonBasket, IIGRController
from skeletons.gui.shared import IItemsCache

class ResearchPanel(ResearchPanelMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self):
        super(ResearchPanel, self).__init__()
        self.__isNavigationEnabled = True

    def _populate(self):
        super(ResearchPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.vehTypeXP': self.onVehicleTypeXPChanged,
         'stats.eliteVehicles': self.onVehicleBecomeElite})
        self.onCurrentVehicleChanged()
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.onCurrentVehicleChanged

    def _dispose(self):
        super(ResearchPanel, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.comparisonBasket.onChange -= self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self.onCurrentVehicleChanged

    def setNavigationEnabled(self, isEnabled):
        if self.__isNavigationEnabled != isEnabled:
            self.as_setNavigationEnabledS(isEnabled)
            self.__isNavigationEnabled = isEnabled

    def goToResearch(self):
        if g_currentVehicle.isPresent() and self.__isNavigationEnabled:
            shared_events.showResearchView(g_currentVehicle.item.intCD)
        else:
            LOG_ERROR('Current vehicle is not preset or navigation is disabled')

    def addVehToCompare(self):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            self.comparisonBasket.addVehicle(vehCD)

    def onCurrentVehicleChanged(self):
        if g_currentVehicle.isPresent():
            xps = self.itemsCache.items.stats.vehiclesXPs
            vehicle = g_currentVehicle.item
            xp = xps.get(vehicle.intCD, 0)
            self.as_updateCurrentVehicleS({'earnedXP': xp,
             'isElite': vehicle.isElite,
             'vehCompareData': self.__getVehCompareData(vehicle)})
        else:
            self.as_updateCurrentVehicleS({'earnedXP': 0})
        self.__onIgrTypeChanged()

    def __onIgrTypeChanged(self, *args):
        igrType = self.igrCtrl.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == IGR_TYPE.PREMIUM else 'basic', {})
        label = text_styles.main(i18n.makeString(MENU.IGR_INFO, igrIcon=icon))
        self.as_setIGRLabelS(igrType != IGR_TYPE.NONE, label)
        self.__updateVehIGRStatus()

    def __updateVehIGRStatus(self):
        vehicleIgrTimeLeft = None
        igrType = self.igrCtrl.getRoomType()
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
        if changedData.isFullChanged:
            self.onCurrentVehicleChanged()

    def __getVehCompareData(self, vehicle):
        state, tooltip = resolveStateTooltip(self.comparisonBasket, vehicle, enabledTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, fullTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        return {'modeAvailable': self.comparisonBasket.isEnabled(),
         'btnEnabled': state,
         'btnTooltip': tooltip}
