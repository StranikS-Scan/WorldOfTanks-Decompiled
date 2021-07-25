# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/professions.py
import typing
import ResMgr
from crew2.instructor.profession import InstructorProfession
from items import _xml
from items.components.detachment_constants import INSTRUCTOR_PROFESSIONS_MAP, INSTRUCTOR_PROFESSIONS_INDICES

class InstructorProfessions(object):

    def __init__(self, configPath):
        self._professions = {}
        self._professionIDs = []
        self._load(configPath)

    def getAllProffessionIDs(self):
        return self._professionIDs

    def getProfession(self, professionID):
        return self._professions.get(professionID)

    def getPerksByProfessionID(self, professionID):
        profession = self.getProfession(professionID)
        return profession.perksIDs if profession else []

    def getProfessionIDByPerk(self, perkID):
        for professionID, profession in self._professions.iteritems():
            if perkID in profession.perksIDs:
                return professionID

        return None

    def getProfessionByPerk(self, perkID):
        for profession in self._professions.itervalues():
            if perkID in profession.perksIDs:
                return profession

        return None

    def isValidProfessionID(self, professionID):
        return professionID in self._professions

    @staticmethod
    def getProfessionNameByID(professinoID):
        return INSTRUCTOR_PROFESSIONS_MAP[professinoID]

    @staticmethod
    def getProfessionIDByName(professionName):
        return INSTRUCTOR_PROFESSIONS_INDICES[professionName]

    def _load(self, configPath):
        section = ResMgr.openSection(configPath)
        if section is None:
            _xml.raiseWrongXml(None, configPath, 'can not open or read')
        setOfPerks = set()
        xmlCtx = (None, configPath)
        for _, professionSec in _xml.getChildren(xmlCtx, section, 'professions'):
            profession = InstructorProfession(xmlCtx, professionSec)
            self._professions[profession.id] = profession
            self._professionIDs.append(profession.id)
            for perkID in profession.perksIDs:
                if perkID not in setOfPerks:
                    setOfPerks.add(perkID)
                _xml.raiseWrongXml(xmlCtx, '', 'perkID={} is contained in different professions'.format(perkID))

        return
