# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_tooltips.py
import logging
from collections import namedtuple
from constants import ARENA_BONUS_TYPE
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from gui.Scaleform.daapi.view.lobby.session_stats.shared import packLastBattleData, packBattleEfficiencyData, packEfficiencyPropData, packTotalPropData
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.dossier.achievements.MarkOfMasteryAchievement import isMarkOfMasteryAchieved
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, int2roman
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
TankStatsHeaderVO = namedtuple('TankStatsHeaderVO', ('tankName', 'flagImage', 'tankImage', 'isFavorite', 'favoriteText', 'tankParams', 'smallSize', 'tankType', 'tankTier', 'tankNameSmall', 'isElite'))
TankBattleResultsStatsVO = namedtuple('TankBattleResultsStatsVO', ('lastBattle',))
TankBattleEfficiencyStatsVO = namedtuple('TankBattleEfficiencyStatsVO', ('battleEfficiency', 'collapseLabel'))
TankStatusVO = namedtuple('TankStatusVO', 'status')
_TANK_MASTER_TYPES_TEXT = [backport.text(R.strings.achievements.achievement.master1()),
 backport.text(R.strings.achievements.achievement.master2()),
 backport.text(R.strings.achievements.achievement.master3()),
 backport.text(R.strings.achievements.achievement.master4())]
_MARK_ON_GUN_ICONS = [backport.image(R.images.gui.maps.icons.library.marksOnGun.mark_1()), backport.image(R.images.gui.maps.icons.library.marksOnGun.mark_2()), backport.image(R.images.gui.maps.icons.library.marksOnGun.mark_3())]
_TOTAL_BLOCK_PARAMS = [SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS, SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL]

class SessionStatsEfficiencyParam(BlocksTooltipData):
    itemsCache = dependency.instance(IItemsCache)

    def __init__(self, context):
        super(SessionStatsEfficiencyParam, self).__init__(context, TOOLTIPS_CONSTANTS.SESSION_STATS_EFFICIENCY_PARAM)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)

    def _packBlocks(self, *args, **kwargs):
        self._propId = args[0]
        return self._packInfoBlocks()

    def _packInfoBlocks(self):
        sessionStats = self.itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR)
        items = []
        if self._propId in _TOTAL_BLOCK_PARAMS:
            data = packTotalPropData(sessionStats, self._propId)
        else:
            accountWtr = self.itemsCache.items.sessionStats.getAccountWtr()
            randomStats = self.itemsCache.items.getAccountDossier().getRandomStats()
            data = packEfficiencyPropData(randomStats, sessionStats, accountWtr, self._propId)
        items.append(formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SESSION_STATS_EFFICIENCY_PARAM_BLOCK, data=data, padding=formatters.packPadding(top=0, bottom=42)))
        return items


class SessionStatsTankInfo(BlocksTooltipData):
    itemsCache = dependency.instance(IItemsCache)

    def __init__(self, context):
        super(SessionStatsTankInfo, self).__init__(context, TOOLTIPS_CONSTANTS.SESSION_STATS_TANK_INFO)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)

    def _packBlocks(self, *args, **kwargs):
        self.smallLayout = args[1]
        self.vehicle = self.context.buildItem(args[0], **kwargs)
        if self.vehicle:
            self.randomStats = self.itemsCache.items.getAccountDossier().getRandomStats()
            self.vehicleStats = self.itemsCache.items.sessionStats.getVehiclesStats(ARENA_BONUS_TYPE.REGULAR, self.vehicle.intCD)
            return self._packTankBlocks()
        return []

    def _packTankBlocks(self):
        items = []
        self._headerPadding = 0
        items.append(self._packHeaderBlock())
        items.append(self._packBattleResultsBlock())
        items.append(self._packBattleEfficiencyBlock())
        return items

    def _packStatusBlock(self):
        data = self._getStatusData()._asdict()
        return formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SESSION_STATS_TANK_INFO_STATUS_BLOCK, data=data, padding=formatters.packPadding(top=-2, bottom=16))

    def _getStatusData(self):
        message = ''
        if self.vehicleStats.battleCnt:
            message = text_styles.statInfo(backport.text(R.strings.session_stats.tankInfo.status.total(), total=self.vehicleStats.battleCnt))
        else:
            message = text_styles.warning(backport.text(R.strings.session_stats.tankInfo.status.warning()))
        return TankStatusVO(status=message)

    def _packBattleResultsBlock(self):
        data = self._getBattleResultsData()._asdict()
        return formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SESSION_STATS_TANK_INFO_BATTLE_RESULTS_BLOCK, data=data, padding=formatters.packPadding(top=-16, bottom=-10))

    def _getBattleResultsData(self):
        return TankBattleResultsStatsVO(lastBattle=packLastBattleData(self.vehicleStats))

    def _packBattleEfficiencyBlock(self):
        data = self._getBattleEfficiencyData()._asdict()
        return formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SESSION_STATS_TANK_INFO_BATTLE_EFFICIENCY_BLOCK, data=data, padding=formatters.packPadding(bottom=35))

    def _getBattleEfficiencyData(self):
        return TankBattleEfficiencyStatsVO(battleEfficiency=packBattleEfficiencyData(self.vehicleStats), collapseLabel='')

    def _packHeaderBlock(self):
        data = self._getHeaderBlockData()._asdict()
        return formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_SESSION_STATS_TANK_INFO_HEADER_BLOCK, data=data, padding=formatters.packPadding(bottom=-125 + self._headerPadding))

    def _getHeaderBlockData(self):
        vehInfo = self.vehicle.name.split(':')
        tankImage = R.images.gui.maps.icons.vehicle.c_420x307.dyn(self._tankNameToRClassName(vehInfo[1]))()
        if tankImage == -1:
            _logger.error('no background image for tooltip for tank %s', str(self._tankNameToRClassName(vehInfo[1])))
            tankImage = R.images.gui.maps.icons.vehicle.c_420x307.dyn('tank_empty')()
        return TankStatsHeaderVO(tankName=text_styles.grandTitle(self.vehicle.userName), isFavorite=self.vehicle.isFavorite, flagImage=backport.image(R.images.gui.maps.icons.flags.c_362x362.dyn(vehInfo[0])()), tankImage=backport.image(tankImage) if tankImage != -1 else '', tankParams=self._getTankParamsVO(True), favoriteText=text_styles.bonusPreviewText(backport.text(R.strings.session_stats.tankInfo.main())), smallSize=True, tankType='{}_elite'.format(self.vehicle.type) if self.vehicle.isElite else self.vehicle.type, tankTier=text_styles.grandTitle(str(int2roman(self.vehicle.level))), tankNameSmall=text_styles.grandTitle(self.vehicle.shortUserName), isElite=self.vehicle.isElite)

    def _getTankParamsVO(self, smallLayout=False):
        self._headerPadding = 0
        itemOffset = 29
        tankItems = []
        if not smallLayout:
            tankItems.append(self._getTankParamVO(text_styles.stats(self.vehicle.typeUserName), self._getTankIcon()))
            tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.session_stats.tankInfo.level())), backport.image(R.images.gui.maps.icons.levels.dyn('tank_level_{}'.format(self.vehicle.level))())))
        markOfMastery = self.randomStats.getMarkOfMasteryForVehicle(self.vehicle.intCD)
        if isMarkOfMasteryAchieved(markOfMastery):
            tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.achievements.markOfMastery(), name=text_styles.stats(_TANK_MASTER_TYPES_TEXT[markOfMastery - 1]))), backport.image(R.images.gui.maps.icons.library.proficiency.dyn('class_icons_{}_small'.format(markOfMastery))())))
        else:
            tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.session_stats.tankInfo.mastery.warning())), backport.image(R.images.gui.maps.icons.library.class_icon())))
        vehDossier = self.itemsCache.items.getVehicleDossier(self.vehicle.intCD)
        vehStats = vehDossier.getTotalStats()
        marksOnGun = vehStats.getAchievement(MARK_ON_GUN_RECORD)
        if marksOnGun.getValue() > 0:
            tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.session_stats.tankInfo.markOnGun(), progress=text_styles.stats('{}{}'.format(marksOnGun.getDamageRating(), '%')))), _MARK_ON_GUN_ICONS[marksOnGun.getValue() - 1]))
        else:
            tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.session_stats.tankInfo.markOnGun.warning(), progress=text_styles.stats('{}{}'.format(marksOnGun.getDamageRating(), '%')))), backport.image(R.images.gui.maps.icons.library.mark_on_gun_icon())))
        tankItems.append(self._getTankParamVO(text_styles.main(backport.text(R.strings.session_stats.tankInfo.status.total(), total=text_styles.stats(self.vehicleStats.battleCnt))), backport.image(R.images.gui.maps.icons.statistic.battles24())))
        if smallLayout:
            self._headerPadding = -itemOffset * 2
        return tankItems

    @staticmethod
    def _getTankParamVO(text, icon):
        return {'text': text,
         'icon': icon}

    @staticmethod
    def _tankNameToRClassName(name):
        return name.lower().replace('-', '_')

    def _getTankIcon(self):
        return RES_ICONS.maps_icons_vehicletypes_elite_all_png(self.vehicle.type) if self.vehicle.isElite else RES_ICONS.maps_icons_vehicletypes_all_png(self.vehicle.type)
