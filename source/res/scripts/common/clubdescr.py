# Embedded file name: scripts/common/ClubDescr.py
import cPickle
from club_shared import EMBLEM_TYPE
from dossiers2.custom.builders import getClubDossierDescr, getRated7x7DossierDescr

class ClubDescr(object):
    __slots__ = ('__databaseID', '_data')

    def __init__(self, clubDBID, webClubData):
        self.__databaseID = clubDBID
        self._data = cPickle.loads(webClubData) if webClubData else {}

    def __repr__(self):
        return 'ClubDescr[%s]' % self.__databaseID + str(self._data)

    databaseID = property(lambda self: self.__databaseID)
    rev = property(lambda self: self._data['rev'])
    name = property(lambda self: self._data.get('name', ''))
    description = property(lambda self: self._data.get('description', ''))
    emblems = property(lambda self: self._data.get('emblems', {}))
    owner = property(lambda self: self._data['owner'])
    state = property(lambda self: self._data['state'])
    createdAt = property(lambda self: self._data['created_at'])
    dossier = property(lambda self: self._data['dossiers'])

    def getDossierDescr(self):
        dossiers = self._data['dossiers']
        dossiers = (getClubDossierDescr(dossiers[0] or ''), getClubDossierDescr(dossiers[1] or ''))
        return dossiers

    ladder = property(lambda self: self._data['ladder'])
    members = property(lambda self: self._data['members'])
    membersExtras = property(lambda self: self._data['membersExtras'])

    def getMemberExtras(self, memberDBID):
        memberExtras = self._data['membersExtras'].get(memberDBID)
        if memberExtras:
            memberExtras = (memberExtras[0], getRated7x7DossierDescr(memberExtras[1] or ''), getRated7x7DossierDescr(memberExtras[2] or ''))
        return memberExtras

    minWinRate = property(lambda self: self._data['minWinRate'])
    minBattleCount = property(lambda self: self._data['minBattleCount'])
    shortDescription = property(lambda self: self._data.get('shortDescription', ''))
    applicants = property(lambda self: self._data['applicants'])
    invites = property(lambda self: self._data['invites'])
    restrictions = property(lambda self: self._data['restrictions'])

    def getEmblemsForClient(self):
        e = self.emblems
        return (e.get(EMBLEM_TYPE.SIZE_24x24, None), e.get(EMBLEM_TYPE.SIZE_32x32, None), e.get(EMBLEM_TYPE.SIZE_64x64, None))
