# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/__init__.py
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.shared.system_factory import registerQueueEntity, registerEntryPoint, registerUnitEntryPoint, registerUnitEntryPointByType, registerUnitEntity, registerLegacyEntryPointByType, registerPrbStorage, registerCustomizationHangarDecorator
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.storages import makeQueueName
from battle_royale.gui.prb_control.entities.regular.squad.entity import BattleRoyaleSquadEntryPoint, BattleRoyaleSquadEntity
from battle_royale.gui.prb_control.entities.regular.pre_queue import entity as br_entity
from battle_royale.gui.prb_control.entities.tournament.pre_queue import entity as br_tournament
from battle_royale.gui.prb_control.entities.tournament.legacy.entity import BattleRoyaleTournamentEntryPoint
from battle_royale.gui.prb_control.storages.battle_royale_storage import BattleRoyaleStorage

def registerBRPrebattles():
    registerQueueEntity(QUEUE_TYPE.BATTLE_ROYALE, br_entity.BattleRoyaleEntity)
    registerQueueEntity(QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT, br_tournament.BattleRoyaleTournamentEntity)
    registerEntryPoint(PREBATTLE_ACTION_NAME.BATTLE_ROYALE, br_entity.BattleRoyaleEntryPoint)
    registerEntryPoint(PREBATTLE_ACTION_NAME.BATTLE_ROYALE_TOURNAMENT, br_tournament.BattleRoyaleTournamentEntryPoint)
    registerUnitEntryPoint(PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, BattleRoyaleSquadEntryPoint)
    registerUnitEntryPointByType(PREBATTLE_TYPE.BATTLE_ROYALE, BattleRoyaleSquadEntryPoint)
    registerUnitEntity(PREBATTLE_TYPE.BATTLE_ROYALE, BattleRoyaleSquadEntity)
    registerLegacyEntryPointByType(PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT, BattleRoyaleTournamentEntryPoint)
    registerPrbStorage(makeQueueName(QUEUE_TYPE.BATTLE_ROYALE), BattleRoyaleStorage())
    registerCustomizationHangarDecorator(currentHangarIsBattleRoyale)
