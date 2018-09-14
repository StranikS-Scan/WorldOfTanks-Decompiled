# Embedded file name: scripts/client/tutorial/control/chains/__init__.py
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control import functional as core_func
from tutorial.control.chains import functional as chains_func
from tutorial.control.quests import queries
from tutorial.control.chains.context import ChainsStartReqs, ChainsBonusesRequester
from tutorial.control.lobby import functional as lobby_func
__all__ = ('ChainsControlsFactory', 'ChainsStartReqs')

class ChainsControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.SET_GUI_ITEM_CRITERIA: core_func.FunctionalSetGuiItemCriteria,
         EFFECT_TYPE.SET_ACTION: core_func.FunctionalSetAction,
         EFFECT_TYPE.REMOVE_ACTION: core_func.FunctionalRemoveAction,
         EFFECT_TYPE.SET_VAR: core_func.FunctionalSetVarAction,
         EFFECT_TYPE.SHOW_MESSAGE: core_func.FunctionalShowMessageEffect,
         EFFECT_TYPE.CLEAR_SCENE: core_func.FunctionalClearScene,
         EFFECT_TYPE.SHOW_WINDOW: core_func.FunctionalShowWindowEffect,
         EFFECT_TYPE.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         EFFECT_TYPE.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.GO_SCENE: core_func.GoToSceneEffect,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.SHOW_HINT: chains_func.FunctionalShowHint,
         EFFECT_TYPE.CLOSE_HINT: chains_func.FunctionalCloseHint,
         EFFECT_TYPE.ENTER_QUEUE: chains_func.FunctionalSwitchToRandom,
         EFFECT_TYPE.SHOW_UNLOCKED_CHAPTER: chains_func.FunctionalShowUnlockedChapter,
         EFFECT_TYPE.SHOW_AWARD_WINDOW: chains_func.FunctionalShowAwardWindow}
        queries_ = {'awardWindow': queries.AwardWindowContentQuery}
        ControlsFactory.__init__(self, effects, queries_)

    def createBonuses(self, completed):
        return ChainsBonusesRequester(completed)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncInfo(self):
        return lobby_func.FunctionalLobbyChapterInfo()
