# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/build.py
from collections import Counter
import typing
import ResMgr
from items import _xml
if typing.TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings

class PerkBuildPreset(object):
    __slots__ = ('_name', '_matrixID', '_progressionID', '_tankRole', '_perks')

    def __init__(self, xmlCtx, section, settingsLocator):
        self.__load(xmlCtx, section)
        self.__validate(xmlCtx, settingsLocator)

    @property
    def name(self):
        return self._name

    @property
    def matrixID(self):
        return self._matrixID

    @property
    def progressionID(self):
        return self._progressionID

    @property
    def tankRole(self):
        return self._tankRole

    @property
    def perks(self):
        return self._perks

    def __load(self, xmlCtx, section):
        self._name = _xml.readString(xmlCtx, section, 'name')
        self._matrixID = _xml.readPositiveInt(xmlCtx, section, 'matrixID')
        self._progressionID = _xml.readPositiveInt(xmlCtx, section, 'progressionID')
        self._tankRole = intern(_xml.readString(xmlCtx, section, 'tankRole'))
        self._perks = {}
        for _, perkSect in _xml.getChildren(xmlCtx, section, 'perks'):
            perkID = _xml.readPositiveInt(xmlCtx, perkSect, 'id')
            points = perkSect.readInt('points', 1)
            if perkID in self._perks:
                _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}' specifies perk {} more than once".format(self._name, perkID))
            self._perks[perkID] = points

    def __validate(self, xmlCtx, settingsLocator):
        self.__validateBuild(xmlCtx, settingsLocator)

    def __validateBuild(self, xmlCtx, settingsLocator):
        matrix = settingsLocator.perkSettings.matrices.getMatrix(self._matrixID)
        if matrix is None:
            _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}' specifies non-existing matrixID = {}".format(self._name, self._matrixID))
        branchPoints = Counter()
        branchesWithUlts = []
        for buildPerkID, buildPerkPoints in self._perks.iteritems():
            matrixPerk = matrix.perks.get(buildPerkID)
            if matrixPerk is None:
                _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}' specifies perkID = {}, which is not in matrix {}".format(self._name, buildPerkID, matrix.id))
            if buildPerkPoints > matrixPerk.max_points:
                _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}'. Perk {} points exceed max_points.".format(self._name, buildPerkID))
            if matrixPerk.ultimate:
                if matrixPerk.branch in branchesWithUlts:
                    _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}'. Cannot select more than one ultimate perk for branch {}".format(self._name, matrixPerk.branch))
                branchesWithUlts.append(matrixPerk.branch)
            branchPoints[matrixPerk.branch] += buildPerkPoints

        progression = settingsLocator.detachmentSettings.progression.getProgressionByID(self._progressionID)
        if progression is None:
            _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}'. Progression with ID {} does not exist".format(self._name, self._progressionID))
        pointsSum = sum(branchPoints.values())
        if pointsSum > progression.maxLevel:
            _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}'. Too many points - {}, progression allows only {}".format(self._name, pointsSum, progression.maxLevel))
        for branchID in branchesWithUlts:
            matrixBranch = matrix.branches[branchID]
            if branchPoints[branchID] < matrixBranch.ultimate_threshold:
                _xml.raiseWrongXml(xmlCtx, '', "Perk build '{}'. Cannot select ultimate for branch {} need {} points".format(self._name, matrixBranch.id, matrixBranch.ultimate_threshold))

        return
