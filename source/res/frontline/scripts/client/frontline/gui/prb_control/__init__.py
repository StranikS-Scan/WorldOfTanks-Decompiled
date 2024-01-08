# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/__init__.py
from frontline.gui.prb_control.entities.epic.pre_queue import entity as fl_entity
from frontline.gui.prb_control.entities.epic.squad import entity as fl_squad_entity
from frontline.gui.prb_control.entities.epic_battle_training import entity as fl_training_entity
from frontline.gui.prb_control.storages.frontline_storage import FrontLineStorage
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.storages import makeQueueName
from gui.shared.system_factory import registerQueueEntity, registerEntryPoint, registerUnitEntryPointByType, registerUnitEntity, registerLegacyEntryPointByType, registerLegacyEntryPoint, registerLegacyEntity, registerPrbStorage
from gui.prb_control.factories.LegacyFactory import extendSupportedIntroByType

def registerFLPrebattles():
    registerQueueEntity(QUEUE_TYPE.EPIC, fl_entity.EpicEntity)
    registerEntryPoint(PREBATTLE_ACTION_NAME.EPIC, fl_entity.EpicEntryPoint)
    registerUnitEntity(PREBATTLE_TYPE.EPIC, fl_squad_entity.EpicSquadEntity)
    registerUnitEntryPointByType(PREBATTLE_TYPE.EPIC, fl_squad_entity.EpicSquadEntryPoint)
    registerLegacyEntryPointByType(PREBATTLE_TYPE.EPIC_TRAINING, fl_training_entity.EpicBattleTrainingEntryPoint)
    registerLegacyEntryPoint(PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST, fl_training_entity.EpicBattleTrainingIntroEntryPoint)
    registerLegacyEntity(PREBATTLE_TYPE.EPIC_TRAINING, fl_training_entity.EpicBattleTrainingEntity)
    registerPrbStorage(makeQueueName(QUEUE_TYPE.EPIC), FrontLineStorage())


def extendIntroByType():
    extendSupportedIntroByType({PREBATTLE_TYPE.EPIC_TRAINING: fl_training_entity.EpicBattleTrainingIntroEntity})
