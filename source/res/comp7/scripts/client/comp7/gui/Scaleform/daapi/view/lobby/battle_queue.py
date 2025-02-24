# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/battle_queue.py
import constants
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared, comp7_i18n_helpers, comp7_model_helpers
from gui.Scaleform.daapi.view.lobby.battle_queue import RandomQueueProvider
from gui.impl import backport
from gui.impl.gen import R

class Comp7QueueProvider(RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        ranks = info.get('ranks', {})
        qualPlayers = info.get('qualPlayers', 0)
        allPlayersCount = info.get('players', sum(ranks.values()) + qualPlayers)
        self._createCommonPlayerString(allPlayersCount)
        if ranks:
            ranksData = []
            isInQualification = comp7_shared.isQualification()
            playerRankIdx = comp7_shared.getPlayerDivision().rank if not isInQualification else None
            for rankIdx, playersCount in ranks.items():
                rankName = comp7_i18n_helpers.RANK_MAP[rankIdx]
                ranksData.append(self.__getRankData(rankName, playersCount, rankIdx == playerRankIdx))

            ranksData.append(self.__getRankData('qualification', qualPlayers, isInQualification))
            self._proxy.as_setDPS(ranksData)
        self._proxy.as_showStartS(constants.IS_DEVELOPMENT and allPlayersCount > 1)
        return

    def getLayoutStr(self):
        pass

    def getIconPath(self, iconlabel):
        return backport.image(R.images.comp7.gui.maps.icons.battleTypes.c_136x136.comp7())

    def getTankInfoLabel(self):
        pass

    def getTankIcon(self, vehicle):
        pass

    def getTankName(self, vehicle):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass

    def __getRankData(self, rankName, playersCount, isHighlight):
        seasonName = comp7_model_helpers.getSeasonNameEnum().value
        rankImg = R.images.comp7.gui.maps.icons.ranks.dyn(seasonName).c_40.dyn(rankName)
        rankStr = R.strings.comp7_ext.rank.dyn(rankName)
        return {'type': backport.text(rankStr()),
         'icon': backport.image(rankImg()),
         'count': playersCount,
         'highlight': isHighlight}
