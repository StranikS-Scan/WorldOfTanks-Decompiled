# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleInfoWindow.py
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from debug_utils import LOG_ERROR
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.VehicleInfoMeta import VehicleInfoMeta
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.items_parameters import formatters
from gui.shared.utils import AUTO_RELOAD_PROP_NAME
from helpers import i18n, dependency
from items import tankmen
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class VehicleInfoWindow(VehicleInfoMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(VehicleInfoWindow, self).__init__()
        self.__vehicleCompactDescr = ctx.get('vehicleCompactDescr', 0)
        self.__highlightPossible = False

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def getVehicleInfo(self):
        vehicle = self._itemsCache.items.getItemByCD(self.__vehicleCompactDescr)
        if vehicle is None:
            LOG_ERROR('There is error while showing vehicle info window: ', self.__vehicleCompactDescr)
            return
        else:
            params = vehicle.getParams()
            tankmenParams = list()
            skillsConfig = tankmen.getSkillsConfig()
            for slotIdx, tankman in vehicle.crew:
                role = vehicle.descriptor.type.crewRoles[slotIdx][0]
                tankmanLabel = ''
                if tankman is not None:
                    lastUserName = tankman.lastUserName
                    if tankman.skinID != NO_CREW_SKIN_ID and self._lobbyContext.getServerSettings().isCrewSkinsEnabled():
                        skinItem = self._itemsCache.items.getCrewSkin(tankman.skinID)
                        lastUserName = i18n.makeString(skinItem.getLastName())
                    tankmanLabel = '%s %s (%d%%)' % (tankman.rankUserName, lastUserName, tankman.roleLevel)
                tankmenParams.append({'tankmanType': i18n.convert(skillsConfig.getSkill(role).userString),
                 'value': tankmanLabel})

            paramsList = formatters.getFormattedParamsList(vehicle.descriptor, params['parameters'], excludeRelative=True)
            info = {'vehicleName': vehicle.longUserName,
             'vehicleDescription': vehicle.fullDescription,
             'vehicleImage': vehicle.icon,
             'vehicleLevel': vehicle.level,
             'vehicleNation': vehicle.nationID,
             'vehicleElite': vehicle.isElite,
             'vehicleType': vehicle.type,
             'propsData': self.__packParams(paramsList),
             'baseData': params['base'],
             'crewData': tankmenParams}
            self.as_setVehicleInfoS(info)
            return

    def addToCompare(self):
        self._comparisonBasket.addVehicle(self.__vehicleCompactDescr)

    def _populate(self):
        self.__highlightPossible = self._settingsCore.serverSettings.checkAutoReloadHighlights()
        super(VehicleInfoWindow, self)._populate()
        self._comparisonBasket.onChange += self.__onVehCompareBasketChanged
        self._comparisonBasket.onSwitchChange += self.__updateCompareButtonState
        self.__updateCompareButtonState()

    def _dispose(self):
        self._comparisonBasket.onSwitchChange -= self.__updateCompareButtonState
        self._comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        super(VehicleInfoWindow, self)._dispose()

    def __packParams(self, paramsList):
        result = []
        for name, value in paramsList:
            paramVO = {'name': name,
             'value': value}
            if name == AUTO_RELOAD_PROP_NAME and self.__highlightPossible:
                paramVO['highlight'] = True
                self._settingsCore.serverSettings.updateUIStorageCounter(UI_STORAGE_KEYS.AUTO_RELOAD_HIGHLIGHTS_COUNTER)
            result.append(paramVO)

        return result

    def __updateCompareButtonState(self):
        if not self._comparisonBasket.isAvailable():
            tooltip = VEH_COMPARE.COMPAREVEHICLEBTN_TOOLTIPS_MINICLIENT
        elif self._comparisonBasket.isFull():
            tooltip = MENU.VEHICLEINFO_COMPAREBTN_TOOLTIP
        else:
            tooltip = ''
        self.as_setCompareButtonDataS({'visible': self._comparisonBasket.isEnabled(),
         'enabled': self._comparisonBasket.isReadyToAdd(self._itemsCache.items.getItemByCD(self.__vehicleCompactDescr)),
         'label': MENU.VEHICLEINFO_COMPAREBTN_LABEL,
         'tooltip': tooltip})

    def __onVehCompareBasketChanged(self, changedData):
        if changedData.isFullChanged:
            self.__updateCompareButtonState()
