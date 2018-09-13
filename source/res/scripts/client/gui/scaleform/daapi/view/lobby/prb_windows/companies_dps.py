# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/companies_dps.py
from constants import PREBATTLE_COMPANY_DIVISION, PREBATTLE_COMPANY_DIVISION_NAMES
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.prb_control.formatters import getCompanyDivisionString
from gui.prb_control.settings import PREBATTLE_ROSTER
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter

def getDivisionsList(addAll = True):
    result = []
    if addAll:
        result.append({'data': 0,
         'label': i18n.makeString('#prebattle:labels/company/division/ALL')})
    for divID in PREBATTLE_COMPANY_DIVISION.RANGE:
        divName = PREBATTLE_COMPANY_DIVISION_NAMES[divID]
        result.append({'data': divID,
         'label': getCompanyDivisionString(divName)})

    return result


class CompaniesDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(CompaniesDataProvider, self).__init__()
        self.__list = []

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def collection(self):
        return self.__list

    def buildList(self, prebattles):
        self.__list = []
        for item in prebattles:
            self.__list.append({'prbID': item.prbID,
             'creatorName': item.creator,
             'creatorClan': item.clanAbbrev,
             'creatorIgrType': item.creatorIgrType,
             'creatorRegion': g_lobbyContext.getRegionCode(item.creatorDbId),
             'comment': item.getCensoredComment(),
             'playersCount': item.playersCount,
             'division': getCompanyDivisionString(item.getDivisionName()),
             'players': []})

    def emptyItem(self):
        return {'prbID': 0,
         'creatorName': '',
         'comment': '',
         'playersCount': 0,
         'division': '',
         'players': []}

    def setPlayers(self, prbID, roster):
        foundIdx = -1
        getUser = self.usersStorage.getUser
        getColor = g_settings.getColorScheme('rosters').getColor
        for idx, item in enumerate(self.__list):
            if item['prbID'] == prbID:
                players = []
                foundIdx = idx
                for info in roster:
                    if info.roster is PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1:
                        user = getUser(info.dbID)
                        if user is not None:
                            key = user.getGuiType()
                        else:
                            key = USER_GUI_TYPE.OTHER
                        players.append({'label': info.getFullName(),
                         'userName': info.name,
                         'clanAbbrev': info.clanAbbrev,
                         'igrType': info.igrType,
                         'region': g_lobbyContext.getRegionCode(info.dbID),
                         'color': getColor(key)})

                item['players'] = players
            else:
                item['players'] = []

        return foundIdx
