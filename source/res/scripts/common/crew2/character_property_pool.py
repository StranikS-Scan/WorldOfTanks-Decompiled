# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/character_property_pool.py
import typing
import ResMgr
from crew2.crew2_consts import GENDER, TAG_TO_GENDER
from items import _xml
from items.components.detachment_constants import InstructorMaxValues
import nations

class CharacterPropertyPool(object):

    def __init__(self, folderPath):
        self._firstNames = {}
        self._commonFirstNameIDs = {}
        self._secondNames = {}
        self._commonSecondNameIDs = {}
        self._portraits = {}
        self._commonPortraitIDs = {}
        for nation in nations.NAMES:
            self.__loadNation(folderPath, nation)

    def getFirstNameByID(self, nationID, ID, gender=None):
        return self._getByID(self._firstNames, nationID, ID, gender)

    def getCommonFirstNameIDs(self, nationID, gender):
        return self._commonFirstNameIDs[nationID][gender]

    def getSecondNameByID(self, nationID, ID, gender=None):
        return self._getByID(self._secondNames, nationID, ID, gender)

    def getCommonSecondNameIDs(self, nationID, gender):
        return self._commonSecondNameIDs[nationID][gender]

    def getPortraitByID(self, nationID, ID, gender=None):
        return self._getByID(self._portraits, nationID, ID, gender)

    def getCommonPortraitIDs(self, nationID, gender):
        return self._commonPortraitIDs[nationID][gender]

    def _getByID(self, container, nationID, ID, gender):
        if gender is not None:
            return container[nationID][gender].get(ID)
        else:
            for gender, idDict in container[nationID].iteritems():
                value = idDict.get(ID)
                if value is not None:
                    return value

            return

    def __loadNation(self, folderPath, nation):
        filePath = '{}/{}.xml'.format(folderPath, nation)
        nationID = nations.INDICES[nation]
        section = ResMgr.openSection(filePath)
        if section is None:
            _xml.raiseWrongXml(None, filePath, 'can not open or read')
        xmlCtx = (None, filePath)
        for secName, charPropSec in _xml.getChildren(xmlCtx, section, 'properties'):
            self.__loadCharProp(xmlCtx, secName, charPropSec, nationID)

        self.__convertListsToTuples(self._commonFirstNameIDs)
        self.__convertListsToTuples(self._commonSecondNameIDs)
        self.__convertListsToTuples(self._commonPortraitIDs)
        ResMgr.purge(filePath)
        return

    def __convertListsToTuples(self, container):
        for nation in container.itervalues():
            for gender in nation.iterkeys():
                nation[gender] = tuple(nation[gender])

    def __loadCharProp(self, xmlCtx, secName, section, nationID):
        SECT_NAME_LOAD_FUNC = {'firstName': self.__loadCharFirstName,
         'secondName': self.__loadCharSecondName,
         'portrait': self.__loadCharPortrait}
        SECT_NAME_LOAD_FUNC[secName](xmlCtx, section, nationID)

    def __loadCharFirstName(self, xmlCtx, section, nationID):
        ID, gender, locale, vip = self.__loadCharName(xmlCtx, section, InstructorMaxValues.FIRST_NAME_ID)
        self._firstNames.setdefault(nationID, {}).setdefault(gender, {})[ID] = locale
        if not vip:
            self._commonFirstNameIDs.setdefault(nationID, {}).setdefault(gender, []).append(ID)

    def __loadCharSecondName(self, xmlCtx, section, nationID):
        ID, gender, locale, vip = self.__loadCharName(xmlCtx, section, InstructorMaxValues.SECOND_NAME_ID)
        self._secondNames.setdefault(nationID, {}).setdefault(gender, {})[ID] = locale
        if not vip:
            self._commonSecondNameIDs.setdefault(nationID, {}).setdefault(gender, []).append(ID)

    def __loadCharName(self, xmlCtx, section, maxID):
        ID = _xml.readInt(xmlCtx, section, 'id', 1, maxID)
        genderStr = _xml.readString(xmlCtx, section, 'gender')
        gender = TAG_TO_GENDER[genderStr]
        locale = _xml.readString(xmlCtx, section, 'locale')
        vip = _xml.readBool(xmlCtx, section, 'vip', False)
        return (ID,
         gender,
         locale,
         vip)

    def __loadCharPortrait(self, xmlCtx, section, nationID):
        ID = _xml.readInt(xmlCtx, section, 'id', 1, InstructorMaxValues.PORTRAIT_ID)
        genderStr = _xml.readString(xmlCtx, section, 'gender')
        gender = TAG_TO_GENDER[genderStr]
        icon = _xml.readString(xmlCtx, section, 'icon')
        vip = _xml.readBool(xmlCtx, section, 'vip', False)
        self._portraits.setdefault(nationID, {}).setdefault(gender, {})[ID] = icon
        if not vip:
            self._commonPortraitIDs.setdefault(nationID, {}).setdefault(gender, []).append(ID)
