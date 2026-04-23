# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/tooltips/event.py
from __future__ import absolute_import
import BigWorld
from future.utils import viewvalues
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.tooltips import formatters
from gui.shared.tooltips.vehicle import VehicleInfoTooltipData, StatusBlockConstructor, HeaderBlockConstructor, SimplifiedStatsBlockConstructor, CommonStatsBlockConstructor
from gui.shared.tooltips.module import ModuleBlockTooltipData, EffectsBlockConstructor, InventoryBlockConstructor, HeaderBlockConstructor as ModuleHeaderBlockConstructor
from gui.shared.tooltips.shell import ShellBlockToolTipData
from last_stand.gui.scaleform.genConsts.LS_ICON_TEXT_FRAMES import LS_ICON_TEXT_FRAMES
from last_stand.gui.scaleform.genConsts.LS_BLOCKS_TOOLTIP_TYPES import LS_BLOCKS_TOOLTIP_TYPES
from LSAccountEquipmentController import getLSConsumables

class EventVehicleInfoTooltipData(VehicleInfoTooltipData, IGlobalListener):

    def _getCrewIconBlock(self):
        tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
        return [formatters.packImageBlockData(img=tImg, alpha=0)]

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        isShort = self.context.getParams().get('isShort', False)
        items = []
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = self._LEFT_PADDING
        rightPadding = self._RIGHT_PADDING
        bottomPadding = 12
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 77
        headerItems = [formatters.packBuildUpBlockData(EventHeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        account = getattr(BigWorld.player(), 'LSAccountComponent', None)
        if account and vehicle.intCD not in account.vehicleDailyCompleted and not isShort:
            headerBlockItems.append(formatters.packTextParameterWithIconBlockData(linkage=LS_BLOCKS_TOOLTIP_TYPES.LS_TOOLTIP_TEXT_PARAMETER_WITH_ICON_BLOCK_LINKAGE, name=text_styles.main(backport.text(R.strings.last_stand_tooltips.vehicle.eventBonus())), value='', icon=LS_ICON_TEXT_FRAMES.LS_EVENT_KEY, iconYOffset=-2, valueWidth=valueWidth - 8, nameOffset=8, gap=0, padding=formatters.packPadding(left=2, top=3, bottom=3)))
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-12)))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked and not isShort:
            statusBlock, operationError, _ = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not operationError:
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding, blockWidth=440))
            else:
                self._setContentMargin(bottom=bottomPadding)
        return items


class EventHeaderBlockConstructor(HeaderBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        nameStr = text_styles.highTitle(self.vehicle.userName)
        icon = getTypeBigIconPath(self.vehicle.type, False)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc='', img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        headerBlocks.append(formatters.packTextBlockData(text_styles.main(self.vehicle.fullDescription), padding=formatters.packPadding(top=-28, left=99, bottom=9)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class EventModuleBlockTooltipData(ModuleBlockTooltipData):

    def _getHeaderBlockConstructor(self):
        return EventModuleHeaderBlockConstructor

    def _getEffectsBlockConstructor(self):
        return EventEffectsBlockConstructor

    def _getInventoryBlockConstructor(self):
        return EventInventoryBlockConstructor


class EventModuleHeaderBlockConstructor(ModuleHeaderBlockConstructor):

    def _getCooldownSeconds(self):
        vehicle = self.configuration.vehicle
        descr = self.module.descriptor
        variant = descr.getVariant(vehicle.descriptor) if vehicle else descr.fallbackVariant
        return variant.cooldownSeconds


class EventEffectsBlockConstructor(EffectsBlockConstructor):

    def _getOnUseStr(self, attribs, isRemovingStun, **kpiArgs):
        vehicle = self.configuration.vehicle
        descr = self.module.descriptor
        variant = descr.getVariant(vehicle.descriptor) if vehicle else descr.fallbackVariant
        base = super(EventEffectsBlockConstructor, self)._getOnUseStr(attribs, isRemovingStun, **kpiArgs)
        if variant.usageCost > 0:
            usageCostStr = backport.text(attribs.dyn('usageCost', R.strings.artefacts.lsAbility.usageCost.default)())
            return makeHtmlString('html_templates:lobby/hangar', 'LS_abilityUsageCost', ctx={'onUse': base,
             'usageCostStr': usageCostStr,
             'cost': variant.usageCost})
        return makeHtmlString('html_templates:lobby/hangar', 'LS_abilityDefault', ctx={'onUse': base})


class EventInventoryBlockConstructor(InventoryBlockConstructor):

    def _getInstalledVehicles(self, module, inventoryVehicles):
        return set((v for v in viewvalues(inventoryVehicles) if getLSConsumables(v).installed.containsIntCD(module.intCD))) if 'LS_equipment' in module.tags else module.getInstalledVehicles(viewvalues(inventoryVehicles))


class EventShellBlockToolTipData(ShellBlockToolTipData):
    pass


class EventVehicleInfoTooltipDataDef(VehicleInfoTooltipData, IGlobalListener):

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = []
        vehicle = self.context.itemsCache.items.getLayoutsVehicleCopy(self.item)
        vehicle.consumables.setLayout(*([None] * len(vehicle.consumables.layout)))
        vehicle.consumables.setInstalled(*([None] * len(vehicle.consumables.installed)))
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = self._LEFT_PADDING
        rightPadding = self._RIGHT_PADDING
        bottomPadding = 12
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 77
        textGap = -2
        headerItems = [formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        account = getattr(BigWorld.player(), 'LSAccountComponent', None)
        if account and vehicle.intCD not in account.vehicleDailyCompleted:
            headerBlockItems.append(formatters.packTextParameterWithIconBlockData(linkage=LS_BLOCKS_TOOLTIP_TYPES.LS_TOOLTIP_TEXT_PARAMETER_WITH_ICON_BLOCK_LINKAGE, name=text_styles.main(backport.text(R.strings.last_stand_tooltips.vehicle.eventBonus())), value='', icon=LS_ICON_TEXT_FRAMES.LS_EVENT_KEY, iconYOffset=-2, valueWidth=valueWidth - 8, nameOffset=8, gap=0, padding=formatters.packPadding(left=2, top=3, bottom=3)))
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-12)))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=-3)))
        if not vehicle.isRotationGroupLocked:
            statusBlock, operationError, _ = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not operationError:
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding, blockWidth=440))
            else:
                self._setContentMargin(bottom=bottomPadding)
        return items
