# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_modules_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.VehiclePreviewModulesTabMeta import VehiclePreviewModulesTabMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.vehicle_collector_helper import wasModulesAnimationShown

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
        self.updateStatus()

    def updateStatus(self):
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                icon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.info_yellow()), 24, 24, -7, -4)
                text = text_styles.neutral('%s%s' % (backport.text(R.strings.vehicle_preview.modulesPanel.status.text()), icon))
            else:
                icon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.info()), 24, 24, -7, -4)
                text = text_styles.stats('%s%s' % (backport.text(R.strings.vehicle_preview.modulesPanel.Label()), icon))
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULS
        else:
            icon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.info()), 24, 24, -7, -4)
            text = text_styles.stats('%s%s' % (backport.text(R.strings.vehicle_preview.modulesPanel.noModulesOptions()), icon))
            tooltip = TOOLTIPS.VEHICLEPREVIEW_MODULSNOMODULES
        self.as_setStatusInfoS(text, tooltip, g_currentPreviewVehicle.getVehiclePreviewType(), needToShowAnim=self.__showAnimation())

    @staticmethod
    def __showAnimation():
        vehicle = g_currentPreviewVehicle.item
        return not wasModulesAnimationShown() if vehicle is not None and vehicle.isCollectible and vehicle.hasModulesToSelect else False
