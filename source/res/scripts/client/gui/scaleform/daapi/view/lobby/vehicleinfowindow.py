# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleInfoWindow.py
from debug_utils import LOG_ERROR
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.VehicleInfoMeta import VehicleInfoMeta
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared import g_itemsCache
from gui.shared.items_parameters import formatters
from helpers import i18n, dependency
from items import tankmen
from skeletons.gui.game_control import IVehicleComparisonBasket

class VehicleInfoWindow(VehicleInfoMeta):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, ctx=None):
        super(VehicleInfoWindow, self).__init__()
        vehicleCompactDescr = ctx.get('vehicleCompactDescr', 0)
        self.vehicleCompactDescr = vehicleCompactDescr

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def getVehicleInfo(self):
        vehicle = g_itemsCache.items.getItemByCD(self.vehicleCompactDescr)
        if vehicle is None:
            LOG_ERROR('There is error while showing vehicle info window: ', self.vehicleCompactDescr)
            return
        else:
            params = vehicle.getParams()
            tankmenParams = list()
            for slotIdx, tankman in vehicle.crew:
                role = vehicle.descriptor.type.crewRoles[slotIdx][0]
                tankmanLabel = ''
                if tankman is not None:
                    tankmanLabel = '%s %s (%d%%)' % (tankman.rankUserName, tankman.lastUserName, tankman.roleLevel)
                tankmenParams.append({'tankmanType': i18n.convert(tankmen.getSkillsConfig()[role].get('userString', '')),
                 'value': tankmanLabel})

            paramsList = formatters.getFormattedParamsList(vehicle.descriptor, params['parameters'], excludeRelative=True)
            info = {'vehicleName': vehicle.longUserName,
             'vehicleDescription': vehicle.fullDescription,
             'vehicleImage': vehicle.icon,
             'vehicleLevel': vehicle.level,
             'vehicleNation': vehicle.nationID,
             'vehicleElite': vehicle.isElite,
             'vehicleType': vehicle.type,
             'propsData': [ {'name': n,
                           'value': v} for n, v in paramsList ],
             'baseData': params['base'],
             'crewData': tankmenParams}
            self.as_setVehicleInfoS(info)
            return

    def addToCompare(self):
        self.comparisonBasket.addVehicle(self.vehicleCompactDescr)

    def _populate(self):
        super(VehicleInfoWindow, self)._populate()
        self.comparisonBasket.onChange += self.__onVehCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__updateCompareButtonState
        self.__updateCompareButtonState()

    def _dispose(self):
        self.comparisonBasket.onSwitchChange -= self.__updateCompareButtonState
        self.comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        super(VehicleInfoWindow, self)._dispose()

    def __updateCompareButtonState(self):
        if not self.comparisonBasket.isAvailable():
            tooltip = VEH_COMPARE.COMPAREVEHICLEBTN_TOOLTIPS_MINICLIENT
        elif self.comparisonBasket.isFull():
            tooltip = MENU.VEHICLEINFO_COMPAREBTN_TOOLTIP
        else:
            tooltip = ''
        self.as_setCompareButtonDataS({'visible': self.comparisonBasket.isEnabled(),
         'enabled': self.comparisonBasket.isReadyToAdd(g_itemsCache.items.getItemByCD(self.vehicleCompactDescr)),
         'label': MENU.VEHICLEINFO_COMPAREBTN_LABEL,
         'tooltip': tooltip})

    def __onVehCompareBasketChanged(self, changedData):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param changedData: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        if changedData.isFullChanged:
            self.__updateCompareButtonState()
