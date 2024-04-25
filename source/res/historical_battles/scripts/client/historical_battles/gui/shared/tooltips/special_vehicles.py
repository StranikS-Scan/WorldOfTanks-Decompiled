# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/tooltips/special_vehicles.py
import typing
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons, text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from skeletons.gui.shared import IItemsCache
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from historical_battles.gui.server_events.game_event.front_progress import FrontProgress

class HBSpecialVehiclesTooltip(BlocksTooltipData):
    __gameEventController = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(HBSpecialVehiclesTooltip, self).__init__(context, None)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(HBSpecialVehiclesTooltip, self)._packBlocks()
        buildUpItems = []
        buildUpItems.append(self.__getTitleBlock())
        buildUpItems.append(self.__getDescriptionBlock())
        buildUpItems.append(self.__getNoteBlock())
        items.append(formatters.packBuildUpBlockData(buildUpItems))
        return items

    def __getTitleBlock(self):
        return formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.hb_tooltips.specialVehiclesTooltip.header())), padding=formatters.packPadding(bottom=7))

    def __getDescriptionBlock(self):
        image = backport.image(R.images.historical_battles.gui.maps.icons.hbCoin.c_16x16.offence())
        iconTag = icons.makeImageTag(image)
        multiplier = text_styles.stats(backport.text(R.strings.hb_tooltips.specialVehiclesTooltip.multiplier()))
        base = text_styles.main(backport.text(R.strings.hb_tooltips.awardScreen.specialVehiclesTooltip.base()))
        hbCoins = text_styles.stats(backport.text(R.strings.hb_tooltips.specialVehiclesTooltip.hbCoins()))
        end = text_styles.main(backport.text(R.strings.hb_tooltips.awardScreen.specialVehiclesTooltip.end()))
        result = text_styles.concatStylesToSingleLine(base, u' ', multiplier, u' ', iconTag, u' ', hbCoins, u' ', end)
        return formatters.packTextBlockData(result, padding=formatters.packPadding(bottom=7))

    def __getNoteBlock(self):
        front = self.__gameEventController.frontController.getSelectedFront()
        if not front:
            return {}
        vehiclesData = front.getVehiclesByLevel()
        maxLevel = max(vehiclesData.keys())
        vehicles = vehiclesData[maxLevel]
        if not vehicles:
            return {}
        items = self.__itemsCache.items
        vehNamesStr = '\n'
        separator = ', '
        for index, vehCD in enumerate(vehicles):
            vehNamesStr += items.getItemByCD(vehCD).shortUserName
            if index != len(vehicles) - 1:
                vehNamesStr += separator

        note = text_styles.main(backport.text(R.strings.hb_tooltips.specialVehiclesTooltip.footerUnlocked(), value=text_styles.gold(vehNamesStr)))
        return formatters.packTextBlockData(note, padding=formatters.packPadding(bottom=-12))
