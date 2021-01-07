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


def _getSubSections(section, subsectionName):
    subsection = section[subsectionName]
    return [] if subsection is None else subsection.items()


def _readSequenceItem(section, fields):
    messageContent = {}
    if fields:
        subSection = section['data']
        for field in fields:
            _FillValue(field, 'asString', default='')(subSection, messageContent)

    return messageContent


def _readSubItemSectionSequence(section, key, fields):
    subSection = section['data']
    keySection = subSection[key]
    content = []
    if keySection:
        content = [ _readSequenceItem(messageSec, fields) for _, messageSec in _getSubSections(keySection, 'sequence') ]
    return content


def _readVideoSection(section):
    messagesFields = ('video-path', 'event-start', 'event-stop', 'event-pause', 'event-resume', 'event-loop', 'icon', 'video-fit-to-screen')
    subtitlesFields = ('subtitle', 'voiceover', 'keypoint')
    messageSec = section['message']
    content = {'messages': _readSequenceItem(messageSec, messagesFields),
     'voiceovers': _readSubItemSectionSequence(messageSec, 'subtitles', subtitlesFields)}
    return content


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
                ribbons = currentBattle['ribbons'] = []
                unlocks = currentBattle['unlocks'] = []
                self.readBattleResultsData(medals, section['medals'])
                self.readBattleResultsData(ribbons, section['ribbons'])
                self.readBattleResultsData(unlocks, section['unlocks'])
                currentBattle['videos'] = []
                videosSection = section['videos']
                if videosSection is not None:
                    currentBattle['videos'] = tuple((_readVideoSection(videoSection) for videoSection in videosSection.values()))

        return
