# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/dog_tags_storage.py
import typing
from collections import namedtuple
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import NO_PROGRESS, DEFAULT_GRADE
from dog_tags_common.player_dog_tag import PlayerDogTag, DogTagComponent

class Storage(object):
    key = ''

    def __init__(self, data):
        self._section = data[self.key]

    @classmethod
    def empty(cls):
        raise NotImplementedError

    @classmethod
    def default(cls):
        raise NotImplementedError


class UnlockedComponentsStorage(Storage):
    key = 'unlockedComponents'

    @classmethod
    def default(cls):
        return cls.empty()

    @classmethod
    def empty(cls):
        return set()

    def getAll(self):
        for compId in self._section:
            yield compId

    def isUnlocked(self, compId):
        return compId in self._section


ProgressRecord = namedtuple('ProgressRecord', 'value, grade')
EMPTY_PROGRESS_RECORD = ProgressRecord(NO_PROGRESS, DEFAULT_GRADE)

class ProgressStorage(Storage):
    key = 'progress'

    @classmethod
    def default(cls):
        return cls.empty()

    @classmethod
    def empty(cls):
        return {}

    def getAllItems(self):
        for compId, progress in self._section.iteritems():
            yield (compId, ProgressRecord(*progress))

    def get(self, compId):
        progress = self._section.get(compId)
        return ProgressRecord(*progress) if progress else EMPTY_PROGRESS_RECORD


SkillDataRecord = namedtuple('SkillDataRecord', 'date, value')

class ExtraDataStorage(Storage):
    key = 'extra'
    skillDataKey = 'skillData'

    @classmethod
    def default(cls):
        return cls.empty()

    @classmethod
    def empty(cls):
        return {cls.skillDataKey: {}}

    def getSkillData(self, compId):
        return [ SkillDataRecord(*i) for i in self._section[self.skillDataKey].get(compId, []) ]


class PlayerDogTagStorage(Storage):
    key = 'playerDogTag'

    def __init__(self, data):
        super(PlayerDogTagStorage, self).__init__(data)
        self._progressStorage = ProgressStorage(data)

    @classmethod
    def default(cls):
        return [ compDef.componentId for compDef in componentConfigAdapter.getDefaultDogTag().components ]

    @classmethod
    def empty(cls):
        return []

    def get(self):
        compIds = self._section or self.default()
        return self.buildPlayerDogTag(compIds)

    def getData(self):
        return self._section

    def buildPlayerDogTag(self, compIds):
        return PlayerDogTag((self._buildComponentForAccount(compId) for compId in compIds))

    def _buildComponentForAccount(self, compId):
        value, grade = self._progressStorage.get(compId) or EMPTY_PROGRESS_RECORD
        return DogTagComponent(compId, value, grade)
