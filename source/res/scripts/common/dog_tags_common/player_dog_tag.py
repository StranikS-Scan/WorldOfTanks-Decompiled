# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/player_dog_tag.py
import typing
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict

class DogTagComponent(object):

    def __init__(self, compId, value, grade):
        self._componentDefinition = componentConfigAdapter.getComponentById(compId)
        self._value = value
        self._grade = grade

    @property
    def compId(self):
        return self._componentDefinition.componentId

    @property
    def value(self):
        return self._value

    @property
    def grade(self):
        return self._grade

    @property
    def componentDefinition(self):
        return self._componentDefinition


class PlayerDogTag(object):

    def __init__(self, comps):
        self._components = {}
        for comp in comps:
            if self._components.get(comp.componentDefinition.viewType, None):
                raise SoftException('Cannot have more than one component of the same view type')
            self._components[comp.componentDefinition.viewType] = comp

        return

    def getComponentByType(self, viewType):
        return self._components.get(viewType, None)

    def getComponentIter(self):
        return self._components.itervalues()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ if isinstance(other, PlayerDogTag) else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        retStr = '('
        for component in self._components.values():
            retStr += 'DogTagComponent(compId={}, value={}, grade={}), '.format(component.compId, component.value, component.grade)

        retStr += ')'
        return retStr

    __str__ = __repr__

    @staticmethod
    def fromDict(dtDict):
        comps = [ DogTagComponent(comp['id'], comp['progress'], comp['grade']) for comp in dtDict['components'] ]
        return PlayerDogTag(comps)

    def toDict(self):
        return {'components': [ {'id': comp.compId,
                        'progress': comp.value,
                        'grade': comp.grade} for comp in self.getComponentIter() ]}


class DisplayableDogTag(object):

    def __init__(self, playerDT, nickName='', clanTag=''):
        self._nickName = nickName
        self._clanTag = clanTag
        self._playerDT = playerDT

    def getNickName(self):
        return self._nickName

    def getClanTag(self):
        return self._clanTag

    def getComponentByType(self, viewType):
        return self._playerDT.getComponentByType(viewType)

    def __repr__(self):
        return '<PlayerDogTag(nickname={}, clantag={}, components={})>'.format(self._nickName, self._clanTag, self._playerDT)

    __str__ = __repr__

    @staticmethod
    def fromDict(dtDict):
        return DisplayableDogTag(PlayerDogTag.fromDict(dtDict), dtDict['playerName'], dtDict['clanTag'])
