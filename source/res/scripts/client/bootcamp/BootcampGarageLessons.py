# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampGarageLessons.py
from ResMgr import openSection
from soft_exception import SoftException
XML_BATTLE_RESULTS_PATH = 'scripts/bootcamp_docs/garage_lessons/battle_results.xml'

class _FillStruct(object):

    def __init__(self, key, vtype, funcs=None, default=None):
        self._key = key
        self._vtype = vtype
        funcs = funcs or []
        if not isinstance(funcs, list):
            funcs = [funcs]
        self._funcs = funcs
        self._default = default

    def __call__(self, section, container):
        if section.has_key(self._key):
            container[self._key] = self._vtype()
            for func in self._funcs:
                func(section[self._key], container[self._key])

        elif self._default is not None:
            container[self._key] = self._default
        return


class _FillValue(_FillStruct):

    def __call__(self, section, container):
        if section.has_key(self._key):
            container[self._key] = getattr(section[self._key], self._vtype)
            for func in self._funcs:
                func(section[self._key], container[self._key])

        elif self._default is not None:
            container[self._key] = self._default
        return


class GarageLessons:

    def __init__(self):
        self.__battleResults = {}
        self.readBattleResultsFile(XML_BATTLE_RESULTS_PATH)

    def getBattleResult(self, lessonId):
        if lessonId in self.__battleResults:
            return self.__battleResults[lessonId]
        raise SoftException('Battle results not found. Lesson - {0}.'.format(lessonId))

    def readBattleResultsData(self, datas, section):
        for _, dataSection in section.items():
            dataSectionDict = {}
            _FillValue('id', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('label', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('description', 'asString', default='')(dataSection, dataSectionDict)
            _FillValue('icon', 'asString')(dataSection, dataSectionDict)
            _FillValue('iconTooltip', 'asString')(dataSection, dataSectionDict)
            datas.append(dataSectionDict)

    def readBattleResultsFile(self, path):
        resultsConfig = openSection(path)
        if resultsConfig is None:
            raise SoftException("Can't open config file (%s)" % path)
        for name, section in resultsConfig.items():
            if name == 'lesson':
                lesson_id = section['id'].asInt
                currentBattle = self.__battleResults[lesson_id] = {}
                medals = currentBattle['medals'] = []
                unlocks = currentBattle['unlocks'] = []
                self.readBattleResultsData(medals, section['medals'])
                self.readBattleResultsData(unlocks, section['unlocks'])

        return
