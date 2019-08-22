# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_royale_modules.py
from gui.Scaleform.daapi.view.common.battle_royale.params import getModuleParameters, getVehicleParameters
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleIcon, getTreeModuleHeader
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_TOOLTIP_MIN_WIDTH = 410

class BattleRoyaleModulesTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(BattleRoyaleModulesTooltip, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        self.item, currentModule = self.context.buildItem(*args, **kwargs)
        items = super(BattleRoyaleModulesTooltip, self)._packBlocks()
        module = self.item
        if module is None:
            return []
        else:
            leftPadding = 20
            rightPadding = 20
            topPadding = 20
            textGap = -2
            headerBlock = HeaderBlockConstructor.construct(module)
            items.append(formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
            paramsBlock = ParamsBlockConstructor.construct(module, currentModule, self._getVehicle())
            if paramsBlock:
                items.append(formatters.packBuildUpBlockData(paramsBlock, padding=formatters.packPadding(left=leftPadding, top=-17), gap=textGap))
            return items

    def _getVehicle(self):
        return self.context.getVehicle()


class HeaderBlockConstructor(object):

    @classmethod
    def construct(cls, module):
        return cls.__constructVehicle(module) if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else cls.__constructModule(module)

    @classmethod
    def __constructModule(cls, module):
        block = []
        moduleDescr = module.descriptor
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(getTreeModuleHeader(moduleDescr.id)), desc=text_styles.standard(moduleDescr.userString), img=backport.image(R.images.gui.maps.icons.battleRoyale.tree.moduleIcons.dyn(getTreeModuleIcon(moduleDescr.id))()), imgPadding=formatters.packPadding(right=12), txtGap=1, txtPadding=formatters.packPadding(top=7)))
        return block

    @classmethod
    def __constructVehicle(cls, vehicle):
        block = []
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(vehicle.userName), img=backport.image(R.images.gui.maps.icons.battleRoyale.tree.moduleIcons.vehicle()), imgPadding=formatters.packPadding(right=12), txtGap=1, txtPadding=formatters.packPadding(top=7)))
        return block


class ParamsBlockConstructor(object):

    @staticmethod
    def construct(module, currentModule, vehicle):
        block = []
        if module.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            params = getModuleParameters(module, vehicle, currentModule)
            leftPadding = 40
        else:
            params = getVehicleParameters(vehicle)
            leftPadding = -45
        for item in params:
            bottomPadding = 10 if item.get('isLastInGroup', False) else 0
            block.append(formatters.packTextParameterBlockData(name=item['description'], value=item['value'], valueWidth=110, padding=formatters.packPadding(left=leftPadding, bottom=bottomPadding)))

        return block
