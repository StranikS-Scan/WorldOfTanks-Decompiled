# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/builds.py
from collections import namedtuple
import typing
import ResMgr
from crew2.perk.build import PerkBuildPreset
from items import _xml
if typing.TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings
    from crew2.perk.matrix import PerkMatrix
BuildPresetsKey = namedtuple('BuildPresetsKey', ('matrixID', 'progressionID', 'tankRole'))

class PerkBuildPresets(object):

    def __init__(self, configPath, settingsLocator=None):
        self._settingsLocator = settingsLocator
        self._builds = {}
        self._buildsByKey = {}
        self._tankRoles = []
        self.__load(configPath)

    @property
    def tankRoles(self):
        return self._tankRoles

    def getBuild(self, name):
        return self._builds.get(name)

    def getBuildsByKey(self, buildPresetsKey):
        return self._buildsByKey.get(buildPresetsKey, [])

    def findMatchingBuild(self, buildPresetsKey, buildA):
        builds = self.getBuildsByKey(buildPresetsKey)
        if len(builds) == 1:
            return builds[0]
        elif len(buildA) == 0 and len(builds) > 0:
            return builds[0]
        else:
            matrix = self._settingsLocator.perkSettings.matrices.getMatrix(buildPresetsKey.matrixID)
            minDiff = float('inf')
            matchingBuild = None
            for buildPresetB in builds:
                diff = self.__class__.__calculateBuildDifference(matrix, buildA, buildPresetB.perks)
                if diff < minDiff:
                    minDiff = diff
                    matchingBuild = buildPresetB

            return matchingBuild

    def __load(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongXml(None, path, 'can not open or read')
        xmlCtx = (None, path)
        self.__readBuilds(xmlCtx, section)
        ResMgr.purge(path)
        return

    def __readBuilds(self, xmlCtx, section):
        buildsXmlCtx = (xmlCtx, 'builds')
        for _, buildSect in _xml.getChildren(xmlCtx, section, 'builds'):
            preset = PerkBuildPreset(buildsXmlCtx, buildSect, self._settingsLocator)
            self._builds[preset.name] = preset
            key = BuildPresetsKey(preset.matrixID, preset.progressionID, preset.tankRole)
            if preset.tankRole not in self._tankRoles:
                self._tankRoles.append(preset.tankRole)
            self._buildsByKey.setdefault(key, []).append(preset)

    @staticmethod
    def __calculateBuildDifference(matrix, buildA, buildB):
        diff = 0
        for perkID, matrixPerk in matrix.perks.iteritems():
            perkA = buildA.get(perkID, 0)
            perkB = buildB.get(perkID, 0)
            perkWeight = 15 if matrixPerk.ultimate else 1
            diff += perkWeight * abs(perkA - perkB)

        return diff
