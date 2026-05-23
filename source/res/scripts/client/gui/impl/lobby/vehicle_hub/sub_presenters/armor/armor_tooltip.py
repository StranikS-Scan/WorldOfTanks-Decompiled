# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/armor_tooltip.py
from __future__ import absolute_import
import typing
from builtins import round
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_layer_model import ArmorLayerModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_tooltip_model import ArmorTooltipModel
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.penetration_utils import calculatePenetrationInfo
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import getMaterialsAtCursor, stackMaterials
from gui.impl.pub import ViewImpl
from gui.impl.pub.window_impl import WindowImpl
from items.components.component_constants import MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS
if typing.TYPE_CHECKING:
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.penetration_utils import ShellParams
_DEFAULT_REDUCTION_FACTOR = 1

class ArmorTooltipView(ViewImpl):
    __slots__ = ('_vehicleEntity',)

    def __init__(self, vehicleEntity):
        super(ArmorTooltipView, self).__init__(ViewSettings(R.views.mono.vehicle_hub.tooltips.armor_tooltip(), model=ArmorTooltipModel()))
        self._vehicleEntity = vehicleEntity

    def update(self, currentMode, shellParams, collisions):
        materials = getMaterialsAtCursor(self._vehicleEntity, collisions, shellParams)
        with self.getViewModel().transaction() as model:
            armorLayers = model.getArmorLayers()
            armorLayers.clear()
            stackedMaterials = stackMaterials(materials, self._vehicleEntity.typeDescriptor.level)
            for material in stackedMaterials:
                layer = ArmorLayerModel()
                layer.setLayerName(material.partName)
                layer.setNominalArmor(round(material.nominalArmor))
                layer.setResultArmor(material.resArmor)
                layer.setImpactAngle(material.viewAngle)
                layer.setColor(material.color)
                layer.setCount(material.count)
                if shellParams is not None and shellParams.useHEShell and material.isSpacedArmor:
                    layer.setReductionFactor(int(MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS))
                else:
                    layer.setReductionFactor(_DEFAULT_REDUCTION_FACTOR)
                armorLayers.addViewModel(layer)

            armorLayers.invalidate()
            model.setSelectedMode(currentMode)
            penetrationInfo = calculatePenetrationInfo(shellParams, collisions)
            if penetrationInfo is not None:
                model.setDccColor(penetrationInfo.color)
                model.setDccType(penetrationInfo.resultType.value)
                model.setDccValue(penetrationInfo.chance)
        return


class ArmorTooltipWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, vehicleEntity, parent=None):
        super(ArmorTooltipWindow, self).__init__(content=ArmorTooltipView(vehicleEntity), wndFlags=WindowFlags.TOOLTIP, parent=parent, layer=WindowLayer.TOOLTIP, areaID=R.areas.specific())

    def update(self, currentMode, shellParams, collisions):
        self.content.update(currentMode, shellParams, collisions)
