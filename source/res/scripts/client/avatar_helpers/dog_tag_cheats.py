# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_helpers/dog_tag_cheats.py
import random
from dog_tags_common.components_config import componentConfigAdapter, SourceData
from dog_tags_common.config.common import ComponentViewType
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException

class DogTagCheats(object):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def showRandomVictimDogTag(cls):
        dogTag = cls._getRandomDogTagForVehicle(cls._selectRandomEnemyVehicleInfo())
        cls._getDogTagController().setVictimsDogTags([dogTag])

    @classmethod
    def showRandomKillerDogTag(cls):
        dogTag = cls._getRandomDogTagForVehicle(cls._selectRandomEnemyVehicleInfo())
        cls._getDogTagController().setKillerDogTag(dogTag)

    @classmethod
    def _randomDogTag(cls):
        result = []
        allComponents = componentConfigAdapter.getAllComponents(SourceData.NON_DEPRECATED_ONLY)
        keysRandom = list(allComponents.keys())
        random.shuffle(keysRandom)
        for viewType in ComponentViewType.__members__.values():
            component = next((allComponents[k] for k in keysRandom if allComponents[k].viewType == viewType))
            grades = component.grades
            if grades:
                maxIndex = len(grades) - 1
                grade = random.randint(0, maxIndex)
                progressLower = grades[grade]
                if grade != maxIndex:
                    progress = int((progressLower + grades[grade + 1]) / 2)
                else:
                    progress = int(progressLower + progressLower / 2)
            else:
                grade = 0
                progress = 0
            result.append({'id': component.componentId,
             'progress': progress,
             'grade': grade})

        return result

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
