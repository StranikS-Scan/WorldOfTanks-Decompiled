# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/modules_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from gui.Scaleform.daapi.view.lobby.shared.fitting_slot_vo import FittingSlotVO
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.ModulesPanelMeta import ModulesPanelMeta
from gui.Scaleform.daapi.view.meta.VehiclePreviewModulesTabMeta import VehiclePreviewModulesTabMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE_INDICES
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.vehicle_collector_helper import wasModulesAnimationShown
from helpers import dependency
from items import ITEM_TYPES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
_MODULE_SLOTS = (GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleChassis],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleTurret],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleGun],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleEngine],
 GUI_ITEM_TYPE_NAMES[ITEM_TYPES.vehicleRadio])

class VehiclePreviewModulesTab(VehiclePreviewModulesTabMeta):

    def _populate(self):
        super(VehiclePreviewModulesTab, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        super(VehiclePreviewModulesTab, self)._dispose()

    def setActiveState(self, isActive):
        pass

    def update(self):
        self.as_setStatusInfoS(*self.__makeStatusInfo())

    @classmethod
    def __makeStatusInfo(cls):
        textRes = R.strings.vehicle_preview.modulesPanel
        iconRes = R.images.gui.maps.icons.library
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                makeTextData = (textRes.status.text, iconRes.info_yellow, text_styles.neutral)
            else:
                makeTextData = (textRes.Label, iconRes.info, text_styles.stats)
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULS
        else:
            makeTextData = (textRes.noModulesOptions, iconRes.info, text_styles.stats)
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULSNOMODULES
        return (_makeStatusText(*makeTextData),
         tooltip,
         g_currentPreviewVehicle.getVehiclePreviewType(),
         cls.__needToShowAnim())

    @staticmethod
    def __needToShowAnim():
        vehicle = g_currentPreviewVehicle.item
        return not wasModulesAnimationShown() if vehicle is not None and vehicle.isCollectible and vehicle.hasModulesToSelect else False


class ModulesPanel(ModulesPanelMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ModulesPanel, self).__init__()
        self.__hasCounter = None
        return

    def _populate(self):
        super(ModulesPanel, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(ModulesPanel, self)._dispose()

    def update(self, *args):
        self._update()

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentPreviewVehicle.item.descriptor)
        return

    def _update(self):
        if g_currentPreviewVehicle.isPresent():
            vehicle = g_currentPreviewVehicle.item
            devices = []
            self.as_setVehicleHasTurretS(vehicle.hasTurrets)
            for slotType in _MODULE_SLOTS:
                data = self.__itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.CUSTOM(lambda item: item.isInstalled(vehicle))).values()
                devices.append(FittingSlotVO(data, vehicle, slotType))

            self.__setHasCounter(devices)
            modulesEnabled = self.__hasCounter or vehicle.hasModulesToSelect
            for device in devices:
                device['isDisabledBgVisible'] = modulesEnabled

            self.as_setDataS({'devices': devices})

    def __setHasCounter(self, devices):
        if self.__hasCounter is None:
            self.__hasCounter = False
            for deviceData in devices:
                if deviceData.get('counter', 0):
                    self.__hasCounter = True

        return

    def __onSettingsChanged(self, diff):
        if SETTINGS_SECTIONS.UI_STORAGE not in diff:
            return
        self._update()


def _makeStatusText(textRes, iconRes, style):
    return style(''.join((backport.text(textRes()), _makeStatusIcon(iconRes))))


def _makeStatusIcon(iconRes):
    return icons.makeImageTag(backport.image(iconRes()), 24, 24, -7, -4)
