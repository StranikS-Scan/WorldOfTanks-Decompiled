# Embedded file name: scripts/client/gui/battle_results/results/club.py
from collections import namedtuple
from functools import partial
from club_shared import ladderRating, ladderRatingLocal
from shared_utils import makeTupleByDict
from gui import makeHtmlString
from gui.shared.formatters import icons
from gui.shared.view_helpers.emblems import ClubEmblemsHelper
from gui.battle_results import abstract, items
from gui.clubs.club_helpers import ClubListener
from gui.clubs.settings import getLadderChevron128x128

def _getClubWinString(isWin):
    if isWin:
        return 'win'
    return 'lose'


def _getClubWinStatus(isWin):
    return makeHtmlString('html_templates:lobby/battleResult/cyberSport/status', _getClubWinString(isWin), {'ico': icons.swords(vspace=-2)})


def _getPointsDiffString(diffValue):
    if not diffValue:
        diff = ''
    else:
        diff = '%+d' % diffValue
    return makeHtmlString('html_templates:lobby/battleResult/cyberSport/pointsDif', 'positive' if diffValue >= 0 else 'negative', {'dif': diff})


class _ClubInfo(namedtuple('_ClubInfo', ['clubDBID', 'ratings', 'divisions'])):

    def getRating(self):
        return ladderRatingLocal(self.ratings[0], self.getDivision())

    def getRatingDiff(self):
        current, prev = self.ratings
        return ladderRating(current) - ladderRating(prev)

    def getDivision(self):
        return self.divisions[0]

    def getDivisions(self):
        return self.divisions


_ClubInfo.__new__.__defaults__ = (-1, ((0, 0), (0, 0)), (-1, -1))

class ClubResults(abstract.BattleResults, ClubEmblemsHelper, ClubListener):

    def __init__(self, results, dp):
        super(ClubResults, self).__init__(results, dp)
        personal = results['personal'].values()[0]
        self._ownClub = makeTupleByDict(_ClubInfo, personal['club'])
        self._enemyClub = makeTupleByDict(_ClubInfo, personal['enemyClub'])
        self.__teamInfoCBs = {}
        for clubDbID in (self._ownClub.clubDBID, self._enemyClub.clubDBID):
            self.startClubListening(clubDbID)

    def clear(self):
        for clubDbID in (self._ownClub.clubDBID, self._enemyClub.clubDBID):
            self.stopClubListening(clubDbID)

    def getOwnClubDbID(self):
        return self._ownClub.clubDBID

    def getOwnClubInfo(self):
        return self._ownClub

    def getEnemyClubInfo(self):
        return self._enemyClub

    def getDivisions(self):
        return self._ownClub.getDivisions()

    def requestTeamInfo(self, isMy, callback):
        if isMy:
            clubDbID = self._ownClub.clubDBID
        else:
            clubDbID = self._enemyClub.clubDBID
        club = self.clubsCtrl.getClub(clubDbID)
        if club:
            callback(items.TeamInfo(club.getUserName(), self._getEmblemRq(club)))
        else:
            self.__teamInfoCBs[clubDbID] = (isMy, callback)

    def updateViewData(self, viewData):
        isWin = self.isWin()
        data = viewData.setdefault('cyberSport', {})
        data.update({'teams': {'allies': self._packClubViewData(self._ownClub, isWin),
                   'enemies': self._packClubViewData(self._enemyClub, not isWin)}})

    def onClubUpdated(self, club):
        if club and club.getClubDbID() in self.__teamInfoCBs:
            self.requestTeamInfo(*self.__teamInfoCBs.pop(club.getClubDbID()))

    def _getEmblemRq(self, club):

        def _cbWrapper(callback, _, emblem):
            callback(emblem)

        return lambda callback: self.requestClubEmblem32x32(club.getClubDbID(), club.getEmblem32x32(), partial(_cbWrapper, callback))

    def _packClubViewData(self, clubInfo, isWin):
        ratingDiff = clubInfo.getRatingDiff()
        return {'teamDBID': clubInfo.clubDBID,
         'resultShortStr': _getClubWinString(isWin),
         'status': _getClubWinStatus(isWin),
         'ladder': getLadderChevron128x128(clubInfo.getDivision()),
         'points': clubInfo.getRating(),
         'pointsDif': ratingDiff,
         'pointsDifStr': _getPointsDiffString(ratingDiff)}
