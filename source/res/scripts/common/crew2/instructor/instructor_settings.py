# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/instructor_settings.py
import random
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import ResMgr
import constants
from crew2.instructor.nation_settings import InstructorNationSettings
from crew2.instructor.token import Token
from crew2.instructor.backgrounds import Backgrounds
from items import _xml
from items.components.detachment_constants import InstructorMaxValues
import nations
if TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings
if constants.IS_CLIENT or TYPE_CHECKING:
    import SoundGroups

class InstructorSettings(object):
    __slots__ = ('_id', '_name', '_nations', '_classID', '_isFemale', '_voiceover', '_professionVariants', '_defaultPerksIDs', '_description', '_token', '_backgrounds')

    def __init__(self, xmlCtx, section, settingsLocator):
        self._id = None
        self._name = None
        self._nations = {}
        self._classID = None
        self._isFemale = None
        self._voiceover = None
        self._professionVariants = None
        self._defaultPerksIDs = None
        self._description = None
        self._token = None
        self._backgrounds = None
        self.__load(xmlCtx, section, settingsLocator)
        self.__validate(xmlCtx)
        return

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def nations(self):
        return self._nations

    @property
    def classID(self):
        return self._classID

    @property
    def isFemale(self):
        return self._isFemale

    @property
    def voiceover(self):
        return self._voiceover

    @property
    def professionVariants(self):
        return self._professionVariants

    @property
    def defaultPerksIDs(self):
        return self._defaultPerksIDs

    @property
    def description(self):
        return self._description

    @property
    def token(self):
        return self._token

    @property
    def backgrounds(self):
        return self._backgrounds

    def getAvailableNations(self):
        return self._nations.keys()

    def getNationSettings(self, nationID):
        return self._nations[nationID]

    def getCharacterProperties(self, nationID):
        nationSettings = self._nations[nationID]
        firstName = random.choice(nationSettings.firstNameIDs)
        secondName = random.choice(nationSettings.secondNameIDs)
        portrait = random.choice(nationSettings.portraitIDs)
        return (firstName, secondName, portrait)

    def isRandomized(self):
        for ns in self._nations.itervalues():
            if len(ns.firstNameIDs) > 1 or len(ns.secondNameIDs) > 1 or len(ns.portraitIDs) > 1:
                return True

        return False

    def __load(self, xmlCtx, section, settingsLocator):
        self._id = _xml.readInt(xmlCtx, section, 'id', 1, InstructorMaxValues.SETTINGS_ID)
        self._name = _xml.readString(xmlCtx, section, 'name')
        self._classID = _xml.readPositiveInt(xmlCtx, section, 'classID')
        self._isFemale = _xml.readBool(xmlCtx, section, 'isFemale')
        self._voiceover = _xml.readStringOrNone(xmlCtx, section, 'voiceover')
        self._description = _xml.readStringOrNone(xmlCtx, section, 'description')
        backgroundsSec = section['backgrounds']
        if backgroundsSec is not None:
            self._backgrounds = Backgrounds(xmlCtx, backgroundsSec)
        tokenSec = section['token']
        if tokenSec is not None:
            tokenCtx = (xmlCtx, self._name)
            self._token = Token(tokenCtx, tokenSec)
        for _, nationSec in _xml.getChildren(xmlCtx, section, 'nations'):
            nation = _xml.readString(xmlCtx, nationSec, 'name')
            nationXmlCtx = (xmlCtx, nation)
            nationID = nations.INDICES.get(nation)
            if nationID is None:
                _xml.raiseWrongXml(nationXmlCtx, '', "Instructor '{}'. Unknown nation name '{}'".format(self._name, nation))
            nationSettings = self._nations.setdefault(nationID, InstructorNationSettings())
            nationSettings.loadFromXml(nationXmlCtx, nationSec, settingsLocator)

        professionsStr = _xml.readStringOrNone(xmlCtx, section, 'professionVariants')
        settings = settingsLocator.instructorSettingsProvider
        if professionsStr is not None:
            self._professionVariants = [ int(x) for x in professionsStr.split() ]
            for professionID in self._professionVariants:
                if settings.professions.isValidProfessionID(professionID):
                    continue
                _xml.raiseWrongXml(xmlCtx, '', 'incorrect profession ID in professionVariants: preset name={}, prf id={}'.format(self._name, professionID))

        else:
            self._professionVariants = settings.professions.getAllProffessionIDs()
        perksIDsStr = _xml.readString(xmlCtx, section, 'defaultPerks')
        if perksIDsStr is not None:
            self._defaultPerksIDs = [ int(x) for x in perksIDsStr.split() ]
        if not self._defaultPerksIDs:
            _xml.raiseWrongXml(xmlCtx, '', 'defaultPerksIDs must be init: preset name={}'.format(self._name))
        instrClass = settings.classes.getClassByID(self._classID)
        if len(instrClass.perkPoints) != len(set(self._defaultPerksIDs)):
            _xml.raiseWrongXml(xmlCtx, '', 'incorrect number of perks specified for instructor:preset={}, class={}'.format(self._name, self._classID))
        defaultPerkProfessionIDs = set()
        for perkID in self._defaultPerksIDs:
            professionID = settings.professions.getProfessionIDByPerk(perkID)
            if professionID is None:
                _xml.raiseWrongXml(xmlCtx, '', 'perkID={} doesnt belong to any profession: preset={}'.format(perkID, self._name))
            defaultPerkProfessionIDs.add(professionID)

        if len(defaultPerkProfessionIDs) != 1:
            _xml.raiseWrongXml(xmlCtx, '', 'defaultPerksIDs contains items from different professions or it doesnt belong to any:preset={}'.format(self._name))
        return

    def __validate(self, xmlCtx):
        self.__validateNations(xmlCtx)
        self.__validateToken(xmlCtx)

    def __validateNations(self, xmlCtx):
        if len(self._nations) < 1:
            _xml.raiseWrongXml(xmlCtx, '', "Instructor '{}'. Must have at least 1 nation specified".format(self._name))

    def __validateToken(self, xmlCtx):
        availableNations = self.getAvailableNations()
        if len(availableNations) <= 1:
            return
        else:
            if self._token is None:
                _xml.raiseWrongXml(xmlCtx, '', "Instructor '{}' can be token, but has no token config".format(self._name))
            nameFromNationID = self._token.nameFromNationID
            if nameFromNationID is not None and nameFromNationID not in availableNations:
                _xml.raiseWrongXml(xmlCtx, '', "Instructor '{}' specifies <token/nameFromNation> '{}', without specifying this nation in <nations>".format(self._name, nations.NAMES[nameFromNationID]))
            if self.isRandomized() and nameFromNationID is not None:
                _xml.raiseWrongXml(xmlCtx, '', "Instructor '{}' is not allowed to specify <token/nameFromNation> because its name is undefined".format(self._name))
            return
