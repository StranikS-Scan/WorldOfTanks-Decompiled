# Embedded file name: scripts/common/ClubDescr.py
import cPickle
from club_shared import EMBLEM_TYPE
from dossiers2.custom.builders import getClubDossierDescr, getRated7x7DossierDescr

class ClubDescr(object):
    __slots__ = ('__databaseID', '__data')

    def __init__(self, clubDBID, webClubData):
        self.__databaseID = clubDBID
        self.__data = cPickle.loads(webClubData) if webClubData else {}

    def __repr__(self):
        return 'ClubDescr[%s]' % self.__databaseID + str(self.__data)

    databaseID = property(lambda self: self.__databaseID)
    rev = property(lambda self: self.__data['rev'])
    name = property(lambda self: self.__data.get('name', ''))
    description = property(lambda self: self.__data.get('description', ''))
    emblems = property(lambda self: self.__data.get('emblems', {}))
    owner = property(lambda self: self.__data['owner'])
    state = property(lambda self: self.__data['state'])
    createdAt = property(lambda self: self.__data['created_at'])
    dossier = property(lambda self: self.__data['dossiers'])

    def getDossierDescr(self):
        dossiers = self.__data['dossiers']
        dossiers = (getClubDossierDescr(dossiers[0] or ''), getClubDossierDescr(dossiers[1] or ''))
        return dossiers

    ladder = property(lambda self: self.__data['ladder'])
    members = property(lambda self: self.__data['members'])
    membersExtras = property(lambda self: self.__data['membersExtras'])

    def getMemberExtras(self, memberDBID):
        memberExtras = self.__data['membersExtras'].get(memberDBID)
        if memberExtras:
            memberExtras = (memberExtras[0], getRated7x7DossierDescr(memberExtras[1] or ''), getRated7x7DossierDescr(memberExtras[2] or ''))
        return memberExtras

    minWinRate = property(lambda self: self.__data['minWinRate'])
    minBattleCount = property(lambda self: self.__data['minBattleCount'])
    shortDescription = property(lambda self: self.__data.get('shortDescription', ''))
    applicants = property(lambda self: self.__data['applicants'])
    invites = property(lambda self: self.__data['invites'])
    restrictions = property(lambda self: self.__data['restrictions'])

    def getEmblemsForClient(self):
        e = self.emblems
        return (e.get(EMBLEM_TYPE.SIZE_24x24, None), e.get(EMBLEM_TYPE.SIZE_32x32, None), e.get(EMBLEM_TYPE.SIZE_64x64, None))
