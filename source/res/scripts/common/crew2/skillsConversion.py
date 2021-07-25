# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/skillsConversion.py
from collections import namedtuple
import typing
from items import _xml
from items.utils.common import SoftAssert
from items.tankmen import getSkillsConfig
if typing.TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings
    from development.libs.ResMgr import DataSection
    from crew2.perk.matrix import PerkMatrix
PerkConversionRecord = namedtuple('PerkConversionRecord', ['crewSkill',
 'weight',
 'isAvg',
 'detPerkID',
 'group'])

class ConversionData(object):

    def __init__(self, levelInheritanceThresholds, levelInheritancePoints, skillsToPerkList):
        self.levelInheritanceThresholds = levelInheritanceThresholds
        self.levelInheritancePoints = levelInheritancePoints
        self.skillsToPerkList = skillsToPerkList


class SkillsConversion(object):

    def __init__(self, settings_locator, xmlCtx, rootSection):
        self._settingsLocator = settings_locator
        self._configuration = {}
        self._load(xmlCtx, rootSection)

    def getConversationData(self, matrixID):
        return self._configuration.get(matrixID)

    def _load(self, xmlCtx, rootSection):
        localCtx = (xmlCtx, 'skillsToPerks')
        for name, subSection in _xml.getChildren(xmlCtx, rootSection, 'skillsToPerks'):
            if name != 'matrix':
                _xml.raiseWrongXml(localCtx, 'skillsToPerks', 'Not supported section %s in skillsToPerks' % name)
            matrixID, conversionData = self._readMatrixSection(localCtx, subSection)
            self._configuration[matrixID] = conversionData

    def _readMatrixSection(self, xmlCtx, section):
        localCtx = (xmlCtx, 'matrix')
        matrixID = _xml.readInt(xmlCtx, section, 'id', minVal=1)
        matrixSettings = self._settingsLocator.perkSettings.matrices.getMatrix(matrixID)
        SoftAssert(matrixSettings is not None, "'matrix id' is not valid (%d)." % matrixID)
        thresholds, points = self._readlevelInheritanceThresholds(localCtx, section)
        skillsToPerkList = self._readConversationTable(localCtx, section, matrixSettings)
        return (matrixID, ConversionData(thresholds, points, skillsToPerkList))

    @staticmethod
    def _readlevelInheritanceThresholds(xmlCtx, section):
        thresholds = []
        points = []
        localCtx = ((xmlCtx, 'levelInheritance'), 'item')
        for name, subItem in _xml.getChildren(xmlCtx, section, 'levelInheritance'):
            thresholds.append(_xml.readInt(localCtx, subItem, 'threshold', minVal=0))
            points.append(_xml.readInt(localCtx, subItem, 'points', minVal=0))

        return (thresholds, points)

    @staticmethod
    def _readConversationTable(xmlCtx, section, matrixSettings):
        res = []
        valueTypes = ['avg', 'max']
        localCtx = ((xmlCtx, 'skills'), 'skill')
        for _, secSkill in _xml.getChildren(xmlCtx, section, 'skills'):
            crewSkill = _xml.readString(localCtx, secSkill, 'crewSkill')
            SoftAssert(getSkillsConfig().getSkill(crewSkill).name != 'unknown', "'crewSkill' is wrong (%s). Use skills from tankmen.xml" % crewSkill)
            detPerk = _xml.readPositiveInt(localCtx, secSkill, 'detachmentPerk')
            SoftAssert(matrixSettings.hasPerk(detPerk), 'perk %d is not in matrix #%d' % (detPerk, matrixSettings.id))
            valueType = _xml.readString(localCtx, secSkill, 'valueType')
            SoftAssert(valueType in valueTypes, "'valueType' is wrong (%s). Correct one of ['avg', 'max']" % valueType)
            valueTypeAvg = valueType == 'avg'
            weight = _xml.readFloat(localCtx, secSkill, 'weight')
            SoftAssert(0 < weight <= 1, "'weight' of skill is wrong (%f). Correct: 0 < W <= 1" % weight)
            group = _xml.readIntOrNone(localCtx, secSkill, 'group')
            res.append(PerkConversionRecord(crewSkill, weight, valueTypeAvg, detPerk, group))

        return res
