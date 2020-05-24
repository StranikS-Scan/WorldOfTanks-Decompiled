# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/stats_exchage/vehicle.py
from gui.shared.badges import buildBadge
from gui.Scaleform.daapi.view.battle.shared.stats_exchage import broker
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control.arena_info import vos_collections
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class ISortedIDsComposer(object):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        raise NotImplementedError


class VehiclesSortedIDsComposer(broker.SingleSideComposer, ISortedIDsComposer):
    __slots__ = ('_items',)

    def __init__(self, voField='vehiclesIDs', sortKey=vos_collections.VehicleInfoSortKey):
        super(VehiclesSortedIDsComposer, self).__init__(voField=voField, sortKey=sortKey)

    def addSortIDs(self, isEnemy, arenaDP):
        self._items = vos_collections.VehiclesInfoCollection().ids(arenaDP)

    def removeObserverIDs(self, arenaDP):
        self._items = [ vID for vID in self._items if not arenaDP.getVehicleInfo(vID).vehicleType.isObserver ]


class AllySortedIDsComposer(VehiclesSortedIDsComposer):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        self._items = vos_collections.AllyItemsCollection(sortKey=self._sortKey).ids(arenaDP)
        self.removeObserverIDs(arenaDP)


class EnemySortedIDsComposer(VehiclesSortedIDsComposer):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        self._items = vos_collections.EnemyItemsCollection(sortKey=self._sortKey).ids(arenaDP)
        self.removeObserverIDs(arenaDP)


class BiSortedIDsComposer(broker.BiDirectionComposer, ISortedIDsComposer):
    __slots__ = ()

    def addSortIDs(self, isEnemy, arenaDP):
        if isEnemy:
            self._right.addSortIDs(isEnemy, arenaDP)
        else:
            self._left.addSortIDs(isEnemy, arenaDP)


class TeamsSortedIDsComposer(BiSortedIDsComposer):
    __slots__ = ()

    def __init__(self, sortKey=vos_collections.VehicleInfoSortKey):
        super(TeamsSortedIDsComposer, self).__init__(left=AllySortedIDsComposer(voField='leftItemsIDs', sortKey=sortKey), right=EnemySortedIDsComposer(voField='rightItemsIDs', sortKey=sortKey))


class TeamsCorrelationIDsComposer(BiSortedIDsComposer):
    __slots__ = ()

    def __init__(self):
        sortKey = vos_collections.FragCorrelationSortKey
        super(TeamsCorrelationIDsComposer, self).__init__(left=AllySortedIDsComposer(voField='leftCorrelationIDs', sortKey=sortKey), right=EnemySortedIDsComposer(voField='rightCorrelationIDs', sortKey=sortKey))


class TotalStatsComposer(broker.IExchangeComposer):
    __slots__ = ('_stats',)

    def __init__(self):
        super(TotalStatsComposer, self).__init__()
        self._stats = {}

    def clear(self):
        self._stats = None
        return

    def compose(self, data):
        if self._stats:
            data['totalStats'] = self._stats
        return data

    def addTotalStats(self, stats):
        self._stats = stats


class VehicleInfoComponent(broker.ExchangeComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('_data',)

    def __init__(self):
        super(VehicleInfoComponent, self).__init__()
        self._data = {}

    def clear(self):
        self._data = {}
        super(VehicleInfoComponent, self).clear()

    def get(self, forced=False):
        return self._data

    def addVehicleInfo(self, vInfoVO, overrides):
        vehicleID = vInfoVO.vehicleID
        vTypeVO = vInfoVO.vehicleType
        playerVO = vInfoVO.player
        accountDBID = playerVO.accountDBID
        sessionID = playerVO.avatarSessionID
        battleCtx = self.__sessionProvider.getCtx()
        isTeamKiller = playerVO.isTeamKiller or battleCtx.isTeamKiller(vehicleID, sessionID) or overrides.isTeamKiller(vInfoVO)
        parts = self._ctx.getPlayerFullName(vInfoVO)
        hasPrefixBadge = bool(vInfoVO.selectedBadge or vInfoVO.overriddenBadge)
        data = {'accountDBID': accountDBID,
         'sessionID': sessionID,
         'playerName': parts.playerName,
         'playerFakeName': parts.playerFakeName,
         'playerFullName': parts.playerFullName,
         'playerStatus': overrides.getPlayerStatus(vInfoVO, isTeamKiller),
         'clanAbbrev': playerVO.clanAbbrev,
         'region': parts.regionCode,
         'userTags': self._ctx.getUserTags(sessionID, playerVO.igrType),
         'squadIndex': vInfoVO.squadIndex,
         'invitationStatus': overrides.getInvitationDeliveryStatus(vInfoVO),
         'vehicleID': vehicleID,
         'vehicleName': vTypeVO.shortName,
         'vehicleType': vTypeVO.getClassName(),
         'vehicleLevel': vTypeVO.level,
         'vehicleIcon': vTypeVO.iconPath,
         'vehicleIconName': vTypeVO.iconName,
         'vehicleStatus': vInfoVO.vehicleStatus,
         'isObserver': vInfoVO.isObserver(),
         'vehicleAction': overrides.getAction(vInfoVO),
         'isVehiclePremiumIgr': vTypeVO.isPremiumIGR,
         'teamColor': overrides.getColorScheme(),
         'hasSelectedBadge': hasPrefixBadge}
        if vInfoVO.overriddenBadge:
            data['badge'] = {'icon': 'override_badge_{}'.format(vInfoVO.overriddenBadge),
             'content': None,
             'sizeContent': ICONS_SIZES.X24,
             'isDynamic': False,
             'isAtlasSource': True}
        elif vInfoVO.selectedBadge:
            badgeID = vInfoVO.selectedBadge
            badge = buildBadge(badgeID, vInfoVO.getBadgeExtraInfo())
            if badge is not None:
                data['badge'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        if vInfoVO.selectedSuffixBadge:
            data['suffixBadgeType'] = 'badge_{}'.format(vInfoVO.selectedSuffixBadge)
            data['suffixBadgeStripType'] = 'strip_{}'.format(vInfoVO.selectedSuffixBadge)
        return self._data.update(data)


class VehicleStatusComponent(broker.ExchangeComponent):
    __slots__ = ('_vehicleID', '_status', '_idsComposers', '_statsComposers')

    def __init__(self, idsComposers=None, statsComposers=None):
        super(VehicleStatusComponent, self).__init__()
        self._vehicleID = 0
        self._status = 0
        self._idsComposers = idsComposers or ()
        self._statsComposers = statsComposers or ()

    def clear(self):
        self._vehicleID = 0
        self._status = 0
        for composer in self._idsComposers:
            composer.clear()

        for composer in self._statsComposers:
            composer.clear()

        super(VehicleStatusComponent, self).clear()

    def get(self, forced=False):
        data = {'isEnemy': self._isEnemy,
         'vehicleID': self._vehicleID,
         'status': self._status}
        for composer in self._idsComposers:
            composer.compose(data)

        for composer in self._statsComposers:
            composer.compose(data)

        return data

    def addVehicleInfo(self, vInfoVO):
        self._vehicleID = vInfoVO.vehicleID
        self._status = vInfoVO.vehicleStatus

    def addTotalStats(self, stats):
        for composer in self._statsComposers:
            composer.addTotalStats(stats)

    def addSortIDs(self, arenaDP):
        for composer in self._idsComposers:
            composer.addSortIDs(self._isEnemy, arenaDP)


class VehicleStatsComponent(broker.VehicleComponent):
    __slots__ = ()

    def addStats(self, vStatsVO):
        raise NotImplementedError


class VehiclesExchangeBlock(broker.ExchangeBlock):
    __slots__ = ('_idsComposers', '_statsComposers')

    def __init__(self, itemComponent, positionComposer=None, idsComposers=None, statsComposers=None):
        super(VehiclesExchangeBlock, self).__init__(itemComponent, composer=positionComposer)
        self._idsComposers = idsComposers or ()
        self._statsComposers = statsComposers or ()

    def clear(self):
        for composer in self._idsComposers:
            composer.clear()

        for composer in self._statsComposers:
            composer.clear()

        super(VehiclesExchangeBlock, self).clear()

    def get(self, forced=False):
        data = super(VehiclesExchangeBlock, self).get(forced=forced)
        if data or forced:
            for composer in self._idsComposers:
                composer.compose(data)

            for composer in self._statsComposers:
                composer.compose(data)

        return data

    def addSortIDs(self, arenaDP, *flags):
        for composer in self._idsComposers:
            for flag in flags:
                composer.addSortIDs(flag, arenaDP)

    def addTotalStats(self, stats):
        for composer in self._statsComposers:
            composer.addTotalStats(stats)
