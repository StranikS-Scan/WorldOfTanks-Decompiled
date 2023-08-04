# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/bonuses/bonus_tooltips.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import int2roman, dependency
from skeletons.gui.shared import IItemsCache

class LootBoxVehicleBlueprintFragmentTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(LootBoxVehicleBlueprintFragmentTooltipData, self).__init__(context, None)
        return

    def _packBlocks(self, vehicleCDs):
        self._items = super(LootBoxVehicleBlueprintFragmentTooltipData, self)._packBlocks()
        titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.fragmentHeader())), padding=formatters.packPadding(top=12))
        self._items.append(titleBlock)
        vehicleBlueprintFragmentBlocks = [ self.__packVehicleFragmentBlock(vehicleCD) for vehicleCD in vehicleCDs ]
        self._items.extend(vehicleBlueprintFragmentBlocks)
        return self._items

    def __packVehicleFragmentBlock(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        level = self.__itemsCache.items.getItemByCD(vehicleCD).level
        filledCount, totalCount = self.__itemsCache.items.blueprints.getBlueprintCount(vehicleCD, level)
        isFinal = filledCount == totalCount
        iconSource = R.images.gui.maps.icons.blueprints.fragment.medium.dyn('vehicle' if not isFinal else 'vehicle_complete', default=R.invalid)()
        return formatters.packImageTextBlockData(title=self.__getVehicleDescrStr(vehicle), img=backport.image(iconSource), txtPadding=formatters.packPadding(left=21), titleAtMiddle=True)

    @staticmethod
    def __getVehicleDescrStr(vehicle):
        vehicleType = vehicle.type.replace('-', '_')
        if vehicle.isElite:
            vehTypeIcon = icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.vehicleTypes.elite.dyn(vehicleType, default=R.invalid)()), width=28, height=28, vSpace=-6)
        else:
            vehTypeIcon = icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.vehicleTypes.dyn(vehicleType, default=R.invalid)()))
        return text_styles.concatStylesToSingleLine(text_styles.mainBig(int2roman(vehicle.level)), vehTypeIcon, text_styles.mainBig(vehicle.userName))
