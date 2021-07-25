# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/classes.py
import typing
import ResMgr
from items import _xml
InstructorClass = typing.NamedTuple('InstructorClass', [('slotsCount', int),
 ('xpBonus', float),
 ('perkPoints', typing.List[int]),
 ('overcapPoints', typing.List[int]),
 ('levelRules', typing.List[int])])

class InstructorClasses(object):

    def __init__(self, configPath):
        self._classes = {}
        self._load(configPath)
        self._classesIDs = []
        self._maxBonusPoints = self._getMaxBonusPoints()

    @property
    def maxBonusPoints(self):
        return self._maxBonusPoints

    def getClassIDs(self):
        if not self._classesIDs:
            return sorted([ cl for cl in self._classes.iterkeys() ])
        return self._classesIDs

    def getClassByID(self, classID):
        return self._classes.get(classID)

    def _getMaxBonusPoints(self):
        return max((max(instClass.perkPoints) for instClass in self._classes.itervalues()))

    def _load(self, xmlPath):
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        xmlCtx = (None, xmlPath)
        self._loadClasses(xmlCtx, section)
        ResMgr.purge(xmlPath, True)
        return

    def _loadClasses(self, xmlCtx, section):
        progression = section['classes']
        if progression is None:
            _xml.raiseWrongSection(xmlCtx, 'classes')
        for classSec in progression.values():
            ID = _xml.readPositiveInt(xmlCtx, classSec, 'id')
            slotsCount = _xml.readPositiveInt(xmlCtx, classSec, 'slotsCount')
            xpBonus = _xml.readFloat(xmlCtx, classSec, 'xpBonus')
            perkPointsStr = _xml.readString(xmlCtx, classSec, 'perkPoints')
            perkPoints = [ int(x) for x in perkPointsStr.split() ]
            overcapPointsStr = _xml.readString(xmlCtx, classSec, 'overcapPoints')
            overcapPoints = [ int(x) for x in overcapPointsStr.split() ]
            levelRulesStr = _xml.readString(xmlCtx, classSec, 'rules')
            levelRules = [ int(x) for x in levelRulesStr.split() ]
            if len(perkPoints) != len(overcapPoints) != levelRules:
                _xml.raiseWrongXml(xmlCtx, '', 'perkPoints, overcapPoints, rules should have same size')
            instructorClass = InstructorClass(slotsCount, xpBonus, perkPoints, overcapPoints, levelRules)
            self._classes[ID] = instructorClass

        return
