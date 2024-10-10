# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleInfoWindow.py
import typing
from debug_utils import LOG_ERROR
from items.vehicles import g_cache
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.meta.VehicleInfoMeta import VehicleInfoMeta
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.formatters import getRoleTextWithLabel
from gui.shared.items_parameters import formatters
from gui.shared.utils import AUTO_RELOAD_PROP_NAME, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_SPEED_MODE_SPEED, TURBOSHAFT_SWITCH_TIME, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION, DUAL_ACCURACY_COOLING_DELAY, SHOT_DISPERSION_ANGLE
from helpers import i18n, dependency
from items import tankmen
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from nation_change_helpers.client_nation_change_helper import getChangeNationTooltip
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict
    from account_helpers.settings_core.ServerSettingsManager import ServerSettingsManager

class _Highlight(object):
    __slots__ = ('__checker', '__highlight')

    def __init__(self, checker):
        super(_Highlight, self).__init__()
        self.__highlight = None
        self.__checker = checker
        return

    def __nonzero__(self):
        if self.__highlight is None:
            self.__highlight = self.__checker()
        return self.__highlight


def _highlightsMap(settings, vehicle=None):
    config = (((AUTO_RELOAD_PROP_NAME,), _Highlight(lambda : settings.checkAutoReloadHighlights(increase=True))),
     ((TURBOSHAFT_ENGINE_POWER,
       TURBOSHAFT_SPEED_MODE_SPEED,
       TURBOSHAFT_SWITCH_TIME,
       TURBOSHAFT_INVISIBILITY_STILL_FACTOR,
       TURBOSHAFT_INVISIBILITY_MOVING_FACTOR), _Highlight(lambda : settings.checkTurboshaftHighlights(increase=True))),
     ((ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION), _Highlight(lambda : settings.checkRocketAccelerationHighlights(increase=True))),
     ((DUAL_ACCURACY_COOLING_DELAY, SHOT_DISPERSION_ANGLE), _Highlight(lambda : vehicle.descriptor.hasDualAccuracy and settings.checkDualAccuracyHighlights(increase=True))))
    mapping = [ zip(params, [highlight] * len(params)) for params, highlight in config ]
    return dict([ item for sub in mapping for item in sub ])


class VehicleInfoWindow(VehicleInfoMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(VehicleInfoWindow, self).__init__()
        self.__vehicleCompactDescr = ctx.get('vehicleCompactDescr', 0)
        serverSettings = self._settingsCore.serverSettings
        vehicle = self._itemsCache.items.getItemByCD(self.__vehicleCompactDescr)
        self.__highlightsMap = _highlightsMap(serverSettings, vehicle)

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
                    lastUserName = tankman.lastUserName if tankman.lastUserName else tankman.firstUserName
                    if tankman.skinID != NO_CREW_SKIN_ID:
                        skinItem = self._itemsCache.items.getCrewSkin(tankman.skinID)
                        lastUserName = i18n.makeString(skinItem.getLastName())
                    tankmanLabel = '%s %s (%d%%)' % (tankman.rankUserName, lastUserName, tankman.roleLevel)
                tankmenParams.append({'tankmanType': i18n.convert(skillsConfig.getSkill(role).userString),
                 'value': tankmanLabel})

            roleStr = getRoleTextWithLabel(vehicle.role, vehicle.roleLabel)
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
             'crewData': tankmenParams,
             'roleStr': roleStr,
             'abilityData': self.__getAbilityData(vehicle.typeDescr.ability)}
            self.as_setVehicleInfoS(info)
            return

    def addToCompare(self):
        self._comparisonBasket.addVehicle(self.__vehicleCompactDescr)

    def changeNation(self):
        vehicle = self._itemsCache.items.getItemByCD(self.__vehicleCompactDescr)
        vehCD = vehicle.intCD if vehicle.activeInNationGroup else iterVehTypeCDsInNationGroup(vehicle.intCD).next()
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, vehCD)
        self.destroy()

    def _populate(self):
        super(VehicleInfoWindow, self)._populate()
        self._comparisonBasket.onChange += self.__onVehCompareBasketChanged
        self._comparisonBasket.onSwitchChange += self.__updateCompareButtonState
        self._itemsCache.onSyncCompleted += self.__updateNationChangeBtn
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__updateNationChangeBtn
        self.__updateCompareButtonState()
        self.__updateChangeNationButtonState()

    def _dispose(self):
        self._comparisonBasket.onSwitchChange -= self.__updateCompareButtonState
        self._comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        self._itemsCache.onSyncCompleted -= self.__updateNationChangeBtn
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateNationChangeBtn
        super(VehicleInfoWindow, self)._dispose()

    def __getAbilityData(self, abilityId):
        if abilityId is not None:
            abilityEquipment = g_cache.getEquipmentByID(abilityId)
            return [{'abilityName': i18n.convert(abilityEquipment.userString),
              'description': i18n.convert(abilityEquipment.description)}]
        else:
            return

    def __packParams(self, paramsList):
        result = []
        for name, value in paramsList:
            paramVO = {'name': name,
             'value': value}
            if self.__highlightsMap.get(name, False):
                paramVO['highlight'] = True
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

    def __onVehCompareBasketChanged(self, changedData, _=None):
        if changedData.isFullChanged:
            self.__updateCompareButtonState()

    def __updateChangeNationButtonState(self):
        vehicle = self._itemsCache.items.getItemByCD(self.__vehicleCompactDescr)
        enabled = vehicle.isNationChangeAvailable
        tooltip = getChangeNationTooltip(vehicle)
        self.as_setChangeNationButtonDataS({'visible': vehicle.hasNationGroup and vehicle.isInInventory,
         'enabled': enabled,
         'label': backport.text(R.strings.menu.vehicleInfo.nationChangeBtn.label()),
         'isNew': not AccountSettings.getSettings(NATION_CHANGE_VIEWED),
         'tooltip': tooltip})

    def __updateNationChangeBtn(self, *args, **kwargs):
        self.__updateChangeNationButtonState()
