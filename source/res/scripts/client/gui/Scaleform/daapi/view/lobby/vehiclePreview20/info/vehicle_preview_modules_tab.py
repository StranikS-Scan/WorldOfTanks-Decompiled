# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_modules_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.meta.VehiclePreviewModulesTabMeta import VehiclePreviewModulesTabMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class VehiclePreviewModulesTab(VehiclePreviewModulesTabMeta):
    itemsCache = dependency.descriptor(IItemsCache)

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
        self.updateStatus()

    def updateStatus(self):
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO_YELLOW, 24, 24, -7, -4)
                text = text_styles.neutral('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_STATUS_TEXT), icon))
            else:
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
                text = text_styles.stats('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_LABEL), icon))
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULS
        else:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
            text = text_styles.stats('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_NOMODULESOPTIONS), icon))
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULSNOMODULES
        self.as_setStatusInfoS(text, tooltip)
