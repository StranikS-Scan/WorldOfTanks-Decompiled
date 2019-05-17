# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_views.py
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.lobby.session_stats.shared import packLastBattleData, packBattleEfficiencyData, packTotalData, toIntegral, toNiceNumber, getDeltaAsData, getNationIcon
from gui.Scaleform.daapi.view.meta.SessionBattleStatsViewMeta import SessionBattleStatsViewMeta
from gui.Scaleform.daapi.view.meta.SessionVehicleStatsViewMeta import SessionVehicleStatsViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_VEH_LIST_LEN = 12

class SessionBattleStatsView(SessionBattleStatsViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        super(SessionBattleStatsView, self)._populate()
        self.as_setDataS(self.__makeVO())
        self.itemsCache.onSyncCompleted += self.__updateViewHandler

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__updateViewHandler

    def __updateViewHandler(self, *_):
        self.as_setDataS(self.__makeVO())

    def __makeVO(self):
        data = self.itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR)
        return {'collapseLabel': text_styles.middleTitle(backport.text(R.strings.session_stats.label.battleEfficiency())),
         'lastBattle': packLastBattleData(data),
         'total': packTotalData(data),
         'battleEfficiency': packBattleEfficiencyData(data)}


class SessionVehicleStatsView(SessionVehicleStatsViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        super(SessionVehicleStatsView, self)._populate()
        self.itemsCache.items.sessionStats.getVehiclesStats(ARENA_BONUS_TYPE.REGULAR, 0)
        self.as_setDataS(self.__makeVO)
        self.itemsCache.onSyncCompleted += self.__updateViewHandler

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__updateViewHandler

    @property
    def __makeVO(self):
        vehIdList = self.itemsCache.items.sessionStats.getStatsVehList(ARENA_BONUS_TYPE.REGULAR)
        vehiclesDict = self.itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(vehIdList))
        vehiclesData = []
        vehiclesSortData = []
        if vehiclesDict:
            for intCD, vehicle in vehiclesDict.iteritems():
                data = self.itemsCache.items.sessionStats.getVehiclesStats(ARENA_BONUS_TYPE.REGULAR, intCD)
                vehiclesSortData.append((intCD, (data.battleCnt, vehicle.level, data.averageDamage.value)))
                vehiclesData.append({'intCD': intCD,
                 'icon': vehicle.iconSmall,
                 'label': text_styles.main(vehicle.shortUserName),
                 'level': vehicle.level,
                 'nationIcon': getNationIcon(vehicle.nationID, width=155, height=31),
                 'type': vehicle.type,
                 'total': text_styles.stats(toNiceNumber(data.battleCnt)),
                 'damage': text_styles.stats(toIntegral(data.averageDamage.value)),
                 'wtr': text_styles.stats(toNiceNumber(data.wtr.value)),
                 'delta': getDeltaAsData(data.wtr.delta)})

        else:
            vehiclesData.append({'intCD': None,
             'icon': backport.image(R.images.gui.maps.icons.library.empty_veh()),
             'total': text_styles.stats(toNiceNumber(None)),
             'damage': text_styles.stats(toIntegral(None)),
             'wtr': text_styles.stats(toNiceNumber(None))})
        if vehiclesSortData:
            vehiclesData = self._sortedVehiclesData(vehiclesSortData, vehiclesData)
        vehiclesData = vehiclesData[0:_VEH_LIST_LEN]
        return {'headerName': text_styles.mainBig(backport.text(R.strings.menu.inventory.menu.vehicle.name())),
         'headerTotalIcon': backport.image(R.images.gui.maps.icons.statistic.battles24()),
         'headerTotalTooltip': backport.text(R.strings.session_stats.tooltip.header.battleCount()),
         'headerDamageIcon': backport.image(R.images.gui.maps.icons.statistic.avgDamage24()),
         'headerDamageTooltip': backport.text(R.strings.session_stats.tooltip.header.avgDamage()),
         'headerWtrIcon': backport.image(R.images.gui.maps.icons.library.wtrIcon_24()),
         'headerWtrTooltip': backport.text(R.strings.session_stats.tooltip.header.wtr()),
         'vehicles': vehiclesData}

    def _sortedVehiclesData(self, vehiclesSortData, vehiclesData):
        sortedParams = sorted(vehiclesSortData, key=lambda params: params[1], reverse=True)
        vehIds = [ sortedParam[0] for sortedParam in sortedParams ]
        return sorted(vehiclesData, key=lambda k: vehIds.index(k['intCD']))

    def __updateViewHandler(self, *_):
        self.as_setDataS(self.__makeVO)
