# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ExampleDestructible.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from constants import DESTRUCTIBLE_MATKIND

class ExampleDestructible(BigWorld.Entity):
    __MATKINDS_ALL = range(DESTRUCTIBLE_MATKIND.NORMAL_MIN, DESTRUCTIBLE_MATKIND.DAMAGED_MAX + 1)
    __MODEL_NAME = 'content/MilitaryEnvironment/mleSU_83_02_OpelBlitz/normal/lod0/mleSU_83_02_OpelBlitz_01.model'

    def __init__(self):
        self.__materialDisabler = None
        return

    def prerequisites(self):
        return [self.__MODEL_NAME]

    def showDamage(self, componentID, isShotDamage):
        LOG_DEBUG('ExampleDestructible.showDamage %d %b', componentID, isShotDamage)

    def set_health(self, prev):
        LOG_DEBUG('ExampleDestructible.set_health %d', self.health)
        self.__onHealthChanged()

    def onEnterWorld(self, prereqs):
        if prereqs.failedIDs:
            LOG_ERROR('Failed to load model %s' % (prereqs.failedIDs,))
            return
        self.model = prereqs[self.__MODEL_NAME]
        self.model.addMotor(BigWorld.Servo(self.matrix))
        md = BigWorld.WGMaterialDisabler()
        self.model.matDisabler = md
        md.setPyModel(self.model)
        self.__materialDisabler = md
        self.__onHealthChanged()

    def __onHealthChanged(self):
        if self.model is not None:
            isDestroyed = self.health <= 0
            for matId in self.__MATKINDS_ALL:
                self.__materialDisabler.setMaterialKindVisible(matId, isDestroyed == (matId >= DESTRUCTIBLE_MATKIND.DAMAGED_MIN))

        return
