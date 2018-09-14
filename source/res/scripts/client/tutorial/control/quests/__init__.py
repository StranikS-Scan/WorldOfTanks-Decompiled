# Embedded file name: scripts/client/tutorial/control/quests/__init__.py
from tutorial.control.lobby.context import LobbyBonusesRequester
from tutorial.control.quests import queries
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control import functional as core_func
from tutorial.control.chains import functional as chains_func
from tutorial.control.lobby import functional as lobby_func
from tutorial.control.quests import functional as quests_func

class QuestsControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.SET_GUI_ITEM_CRITERIA: core_func.FunctionalSetGuiItemCriteria,
         EFFECT_TYPE.SET_ACTION: core_func.FunctionalSetAction,
         EFFECT_TYPE.REMOVE_ACTION: core_func.FunctionalRemoveAction,
         EFFECT_TYPE.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         EFFECT_TYPE.NEXT_CHAPTER: core_func.FunctionalNextChapterEffect,
         EFFECT_TYPE.CLEAR_SCENE: core_func.FunctionalClearScene,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.GO_SCENE: core_func.GoToSceneEffect,
         EFFECT_TYPE.SHOW_HINT: chains_func.FunctionalShowHint,
         EFFECT_TYPE.CLOSE_HINT: chains_func.FunctionalCloseHint,
         EFFECT_TYPE.SHOW_WINDOW: quests_func.ShowSharedWindowEffect,
         EFFECT_TYPE.SAVE_TUTORIAL_SETTING: quests_func.SaveTutorialSettingEffect,
         EFFECT_TYPE.SAVE_ACCOUNT_SETTING: quests_func.SaveAccountSettingEffect,
         EFFECT_TYPE.RUN_TRIGGER: quests_func.QuestsFunctionalRunTriggerEffect,
         EFFECT_TYPE.SHOW_UNLOCKED_CHAPTER: chains_func.FunctionalShowUnlockedChapter,
         EFFECT_TYPE.SHOW_AWARD_WINDOW: chains_func.FunctionalShowAwardWindow}
        _queries = {'awardWindow': queries.AwardWindowContentQuery}
        ControlsFactory.__init__(self, effects, _queries)

    def createBonuses(self, completed):
        return LobbyBonusesRequester(completed)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncInfo(self):
        return lobby_func.FunctionalLobbyChapterInfo()
