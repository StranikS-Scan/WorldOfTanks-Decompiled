# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_select/module_extenders.py
import typing
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS, ServerSettingsManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import TURBOSHAFT_ENGINE_POWER
from gui.shared.gui_items.vehicle_modules import VehicleEngine, VehicleGun
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
    from gui.shared.gui_items.vehicle_modules import VehicleModule
_ModuleParamExtendInfo = typing.NamedTuple('_ModuleParamsExtenderData', (('param', str), ('replaceParam', str)))

class ModuleParamsExtender(object):
    __slots__ = ('__settingsKey', '__settingsUpdated')

    def __init__(self, settingsKey):
        super(ModuleParamsExtender, self).__init__()
        self.__settingsUpdated = False
        self.__settingsKey = settingsKey

    def check(self, vehicleModule, vehicleDescriptor):
        pass

    def highlightCheck(self, settings):
        return False

    def updatedHighlightSettings(self, settings):
        if not self.__settingsUpdated:
            settings.updateUIStorageCounter(self.__settingsKey)
            self.__settingsUpdated = True

    def extendParamList(self, paramList):
        return (paramList, None)


class ReplaceModuleParamsExtender(ModuleParamsExtender):
    __slots__ = ('__replaceInfo',)

    def __init__(self, settingsKey, replaceInfo):
        super(ReplaceModuleParamsExtender, self).__init__(settingsKey)
        self.__replaceInfo = replaceInfo

    def extendParamList(self, paramList):
        replaceMap = {paramList.index(info.param):info.replaceParam for info in self.__replaceInfo if info.param in paramList}
        if replaceMap:
            params = list(paramList)
            for ind, replace in replaceMap.items():
                params[ind] = replace

            return (params, replaceMap.keys())
        else:
            return (paramList, None)


class AutoReloadParamsExtender(ReplaceModuleParamsExtender):

    def __init__(self):
        super(AutoReloadParamsExtender, self).__init__(UI_STORAGE_KEYS.AUTO_RELOAD_HIGHLIGHTS_COUNTER, (_ModuleParamExtendInfo('reloadTime', 'autoReloadTime'),))

    def check(self, vehicleModule, vehicleDescriptor):
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.GUN:
            gun = typing.cast(VehicleGun, vehicleModule)
            return gun.isAutoReloadable(vehicleDescriptor)
        return False

    def highlightCheck(self, settings):
        return settings.checkAutoReloadHighlights()


class DualGunParamsExtender(ReplaceModuleParamsExtender):

    def __init__(self):
        super(DualGunParamsExtender, self).__init__(UI_STORAGE_KEYS.DUAL_GUN_HIGHLIGHTS_COUNTER, (_ModuleParamExtendInfo('reloadTime', 'reloadTimeSecs'),))

    def check(self, vehicleModule, vehicleDescriptor):
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.GUN:
            gun = typing.cast(VehicleGun, vehicleModule)
            return gun.isDualGun(vehicleDescriptor)
        return False

    def highlightCheck(self, settings):
        return settings.checkDualGunHighlights()


class TurboshaftParamsExtender(ModuleParamsExtender):

    def __init__(self):
        super(TurboshaftParamsExtender, self).__init__(UI_STORAGE_KEYS.TURBOSHAFT_HIGHLIGHTS_COUNTER)

    def highlightCheck(self, settings):
        return settings.checkTurboshaftHighlights()

    def check(self, vehicleModule, vehicleDescriptor):
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.ENGINE:
            engine = typing.cast(VehicleEngine, vehicleModule)
            return engine.hasTurboshaftEngine()
        return False

    def extendParamList(self, paramList):
        ind = paramList.index('enginePower') + 1 if 'enginePower' in paramList else 0
        params = list(paramList)
        params.insert(ind, TURBOSHAFT_ENGINE_POWER)
        return (params, [ind])


def fittingSelectModuleExtenders():
    return (AutoReloadParamsExtender(), DualGunParamsExtender(), TurboshaftParamsExtender())
