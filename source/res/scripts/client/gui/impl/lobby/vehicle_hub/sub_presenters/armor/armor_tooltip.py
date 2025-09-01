# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/armor_tooltip.py
from __future__ import absolute_import
from account_helpers.settings_core import settings_constants
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_layer_model import ArmorLayerModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_tooltip_model import ArmorTooltipModel
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getMaterialsAtCursor, stackMaterials
from gui.impl.pub import ViewImpl
from gui.impl.pub.window_impl import WindowImpl
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace

class ArmorTooltipView(ViewImpl):
    __slots__ = ('_vehicleEntity',)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, vehicleEntity):
        settings = ViewSettings(R.views.mono.vehicle_hub.tooltips.armor_tooltip(), model=ArmorTooltipModel())
        super(ArmorTooltipView, self).__init__(settings)
        self._vehicleEntity = vehicleEntity

    def _getEvents(self):
        return ((self._settingsCore.onSettingsChanged, self._onSettingsChanged),)

    def _onLoading(self, *args, **kwargs):
        super(ArmorTooltipView, self)._onLoading(*args, **kwargs)
        self.update()

    def _onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self.update()

    def update(self):
        materials = getMaterialsAtCursor(self._vehicleEntity, self._hangarSpace.spaceID)
        with self.getViewModel().transaction() as model:
            armorLayers = model.getArmorLayers()
            armorLayers.clear()
            stackedMaterials = stackMaterials(materials, self._vehicleEntity.typeDescriptor.level)
            for material in stackedMaterials:
                layer = ArmorLayerModel()
                layer.setLayerName(material.partName)
                layer.setNominalArmor(material.nominalArmor)
                layer.setResultArmor(material.resArmor)
                layer.setImpactAngle(material.viewAngle)
                layer.setColor(material.color)
                layer.setCount(material.count)
                armorLayers.addViewModel(layer)

            armorLayers.invalidate()


class ArmorTooltipWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, vehicleEntity, parent=None):
        super(ArmorTooltipWindow, self).__init__(content=ArmorTooltipView(vehicleEntity), wndFlags=WindowFlags.TOOLTIP, parent=parent, layer=WindowLayer.TOOLTIP, areaID=R.areas.specific())

    def update(self):
        self.content.update()
