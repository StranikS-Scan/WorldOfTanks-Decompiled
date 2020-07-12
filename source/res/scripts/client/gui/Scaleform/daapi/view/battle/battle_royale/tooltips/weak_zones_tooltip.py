# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/tooltips/weak_zones_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Vehicle
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData

class WeakZonesTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(WeakZonesTooltip, self).__init__(context, TOOLTIPS_CONSTANTS.BATTLE_ROYALE_WEAK_ZONES)
        self._setContentMargin(top=20, left=20, bottom=0, right=20)
        self._setWidth(430)

    def _packBlocks(self):
        items = super(WeakZonesTooltip, self)._packBlocks()
        vehicle = self.context.getVehicle()
        items.append(self.__packWeakZonesBlockData(title=text_styles.highTitle(backport.text(R.strings.battle_royale.tooltips.weakZones.title())), desc=text_styles.main(backport.text(R.strings.battle_royale.tooltips.weakZones.description())), img=self.__getTooltipWeakZonesImage(vehicle)))
        return items

    @staticmethod
    def __packWeakZonesBlockData(img, title=None, desc=None, padding=None, linkage=BLOCKS_TOOLTIP_TYPES.BATTLE_ROYALE_WEAK_ZONES_UI):
        data = {}
        if title is not None:
            data['title'] = title
        if desc is not None:
            data['description'] = desc
        if img is not None:
            data['imagePath'] = img
        data['engineLabel'] = backport.text(R.strings.battle_royale.tooltips.weakZones.engine())
        data['ammunitionLabel'] = backport.text(R.strings.battle_royale.tooltips.weakZones.ammunition())
        data['fuelTankLabel'] = backport.text(R.strings.battle_royale.tooltips.weakZones.fuelTank())
        return formatters.packBlockDataItem(linkage, data, padding)

    @staticmethod
    def __getTooltipWeakZonesImage(vehicle):
        vehicleName = Vehicle.getIconResourceName(vehicle.name)
        return backport.image(R.images.gui.maps.icons.battleRoyale.weakZones.tooltip.dyn(vehicleName)())
