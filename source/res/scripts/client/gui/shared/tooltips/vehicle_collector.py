# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle_collector.py
import logging
from itertools import chain
from constants import MIN_VEHICLE_LEVEL
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BLOCKS_TOOLTIP_TYPES, BlocksTooltipData
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.utils import vehicle_collector_helper as helper
from dossiers2.custom.cache import getCache
from helpers import dependency
import nations
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class VehicleCollectorTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehicleCollectorTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE_COLLECTOR)
        self._setContentMargin(top=0, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(400)

    def _packBlocks(self, nationName):
        self.__nationName = nationName
        nationID = nations.INDICES.get(self.__nationName)
        if nationID is None:
            _logger.error('Incorrect nation %s', self.__nationName)
            return []
        else:
            items = [formatters.packBuildUpBlockData(blocks=list(chain(self.__getHeader(), self.__getDescription())))]
            items.append(self.__getDisabledStatusBlock())
            return items

    def __getHeader(self):
        nationID = nations.INDICES.get(self.__nationName)
        return [formatters.packImageBlockData(img=RES_ICONS.getTooltipFlag(self.__nationName), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(bottom=-80, left=-20)), formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.collectibleVehicleTooltip.header(), nation=backport.text(R.strings.nations.dyn(self.__nationName).genetiveCase())))), formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.buttons.icon_table_comparison_inhangar()), imgPadding=formatters.packPadding(top=-2, left=-5), desc=text_styles.main(backport.text(R.strings.tooltips.collectibleVehicleTooltip.statistics(), inventory=text_styles.stats(len(helper.getCollectibleVehiclesInInventory(nationID))), common=len(helper.getCollectibleVehicles(nationID)))))]

    def __getDisabledStatusBlock(self):
        nationID = nations.INDICES.get(self.__nationName)
        align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
        if helper.isAllCollectionPurchased(nationID):
            block = formatters.packAlignedTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.collectibleVehicleTooltip.status.purchased())), align=align)
        else:
            maxUnlockedLevel = self.__itemsCache.items.stats.getMaxResearchedLevelByNations().get(nationID, MIN_VEHICLE_LEVEL)
            vehicleLevels = getCache()['collectorVehiclesLevelsByNations'].get(nationID, set())
            if not vehicleLevels:
                raise SoftException('There are not collectible vehicles in the nation tree of {}'.format(self.__nationName))
            if min(vehicleLevels) <= maxUnlockedLevel:
                header = R.strings.tooltips.collectibleVehicleTooltip.status.purchaseAvailable()
                text = R.strings.tooltips.collectibleVehicleTooltip.status.condition()
                styleGetter = text_styles.middleTitle
            else:
                header = R.strings.tooltips.collectibleVehicleTooltip.status.purchaseUnavailable()
                text = R.strings.tooltips.collectibleVehicleTooltip.status.condition()
                styleGetter = text_styles.statusAttention
            block = formatters.packAlignedTextBlockData(text=text_styles.concatStylesToMultiLine(styleGetter(backport.text(header)), text_styles.main(backport.text(text))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        return formatters.packBuildUpBlockData(blocks=[block], padding=formatters.packPadding(top=5))

    @staticmethod
    def __getDescription():
        return [formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.vehicle_collector.collectibles_pic()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=10)), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.collectibleVehicleTooltip.description())), padding=formatters.packPadding(bottom=10)), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.collectibleVehicleTooltip.elite())))]


class VehicleCollectorDisabledTooltipData(BlocksTooltipData):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, context):
        super(VehicleCollectorDisabledTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE_COLLECTOR)

    def getDisplayableData(self, *args, **kwargs):
        if self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled():
            _logger.error('Vehicle collector is enabled')
            return {}
        return {'header': text_styles.critical(backport.text(R.strings.tooltips.collectibleVehicleTooltip.switchOff.header())),
         'body': text_styles.main(backport.text(R.strings.tooltips.collectibleVehicleTooltip.switchOff.text()))}
