# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_qualification_helpers.py
import typing
from helpers import dependency
from comp7_common import BattleStatuses
from frameworks.wulf.view.array import fillViewModelsArray
from skeletons.gui.game_control import IComp7Controller
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.qualification_battle import BattleState, QualificationBattle
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.comp7.qualification_model import QualificationModel
BATTLE_STATES = {BattleStatuses.WIN: BattleState.VICTORY,
 BattleStatuses.LOSE: BattleState.DEFEAT,
 BattleStatuses.DESERTER: BattleState.DEFEAT}

@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setQualificationInfo(model, comp7Controller=None):
    battleStatuses = comp7Controller.qualificationBattlesStatuses
    maxBattlesCount = comp7Controller.qualificationBattlesNumber
    model.setIsActive(comp7Controller.isQualificationActive())
    model.setBattlesCount(len(battleStatuses))
    model.setMaxBattlesCount(maxBattlesCount)
    model.setIsRatingCalculation(comp7Controller.isQualificationResultsProcessing())


def setQualificationBattles(qualificationArray):
    battles = [ __createQualificationBattleModel(state) for state in __getQualificationBattleStates() ]
    fillViewModelsArray(battles, qualificationArray)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def __getQualificationBattleStates(comp7Controller=None):
    battles = []
    battleStatuses = comp7Controller.qualificationBattlesStatuses
    maxBattlesCount = comp7Controller.qualificationBattlesNumber
    playedBattlesNumber = len(battleStatuses)
    for battleIdx in range(maxBattlesCount):
        state = BattleState.NOTPLAYED
        if battleIdx < playedBattlesNumber:
            state = BATTLE_STATES.get(battleStatuses[battleIdx], BattleState.INPROGRESS)
        battles.append(state)

    return battles


def __createQualificationBattleModel(state):
    battleModel = QualificationBattle()
    battleModel.setState(state)
    return battleModel
