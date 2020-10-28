# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_helpers/dog_tags_helpers.py
import random
import BigWorld
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.components_packer import unpack_component
from dog_tags_common.config.common import ComponentViewType
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException

class DogTagsHelpers(object):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def showRandomVictimDogTag(cls):
        dogTag = cls._getRandomDogTagForVehicle(cls._selectRandomEnemyVehicleInfo())
        cls._getDogTagController().setVictimsDogTags([dogTag])

    @classmethod
    def showRandomKillerDogTag(cls):
        dogTag = cls._getRandomDogTagForVehicle(cls._selectRandomEnemyVehicleInfo())
        cls.guiSessionProvider.switchToPostmortem(True, False)
        cls._getDogTagController().onKillerDogTagCheat(cls._getDeadReasonInfo())
        cls._getDogTagController().setKillerDogTag(dogTag)

    @classmethod
    def _randomDogTag(cls):
        usedDogTagsComponents = BigWorld.player().arena.arenaInfo.dogTagsInfo.usedDogTagsComponents
        possibleDTs = []
        for componentPacked in usedDogTagsComponents:
            compId, grade, teamId = unpack_component(componentPacked)
            if teamId == BigWorld.player().team:
                continue
            possibleDTs.append((compId, grade))

        if not possibleDTs:
            raise SoftException('Could not generate random Dog Tag. No enemies in battle.')
        random.shuffle(possibleDTs)
        result = []
        allComponents = componentConfigAdapter.getAllComponents()
        for viewType in ComponentViewType.__members__.values():
            compID, grade = next((k for k in possibleDTs if allComponents[k[0]].viewType == viewType))
            progress = 0
            result.append({'id': compID,
             'progress': progress,
             'grade': grade})

        return result

    @classmethod
    def _getDeadReasonInfo(cls):
        return ['Cheat',
         True,
         'X',
         '',
         '',
         'Cheat',
         {'userName': 'Cheat',
          'clanAbbrev': '',
          'tags': set([]),
          'region': None,
          'fakeName': '',
          'igrType': 0}]

    @classmethod
    def _selectRandomEnemyVehicleInfo(cls):
        arenaDP = cls.guiSessionProvider.getArenaDP()
        infoIterator = arenaDP.getVehiclesInfoIterator()
        enemyVehicles = [ vInfo for vInfo in infoIterator if arenaDP.isEnemyTeam(vInfo.team) ]
        if not enemyVehicles:
            raise SoftException('Could not generate random Dog Tag. No enemies in battle.')
        return random.choice(enemyVehicles)

    @classmethod
    def _getRandomDogTagForVehicle(cls, vInfo):
        dogTag = {'vehicleId': vInfo.vehicleID,
         'dogTag': {'components': cls._randomDogTag()}}
        return dogTag

    @classmethod
    def _getDogTagController(cls):
        dogTagsCtrl = cls.guiSessionProvider.dynamic.dogTags
        if not dogTagsCtrl:
            raise SoftException('DogTagsController has not been found.')
        return dogTagsCtrl
