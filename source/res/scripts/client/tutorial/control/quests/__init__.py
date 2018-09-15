# Python bytecode 2.7 (decompiled from Python 2.7)
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
         EFFECT_TYPE.GLOBAL_ACTIVATE: core_func.FunctionalGlobalActivateEffect,
         EFFECT_TYPE.GLOBAL_DEACTIVATE: core_func.FunctionalGlobalDeactivateEffect,
         EFFECT_TYPE.SET_GUI_ITEM_CRITERIA: core_func.FunctionalSetGuiItemCriteria,
         EFFECT_TYPE.SET_ACTION: core_func.FunctionalSetAction,
         EFFECT_TYPE.REMOVE_ACTION: core_func.FunctionalRemoveAction,
         EFFECT_TYPE.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         EFFECT_TYPE.NEXT_CHAPTER: core_func.FunctionalNextChapterEffect,
         EFFECT_TYPE.CLEAR_SCENE: core_func.FunctionalClearScene,
         EFFECT_TYPE.GO_SCENE: core_func.GoToSceneEffect,
         EFFECT_TYPE.SHOW_HINT: chains_func.FunctionalShowHint,
         EFFECT_TYPE.CLOSE_HINT: chains_func.FunctionalCloseHint,
         EFFECT_TYPE.SHOW_WINDOW: quests_func.ShowSharedWindowEffect,
         EFFECT_TYPE.SELECT_VEHICLE_IN_HANGAR: quests_func.SelectVehicleInHangar,
         EFFECT_TYPE.SAVE_TUTORIAL_SETTING: quests_func.SaveTutorialSettingEffect,
         EFFECT_TYPE.SAVE_ACCOUNT_SETTING: quests_func.SaveAccountSettingEffect,
         EFFECT_TYPE.RUN_TRIGGER: quests_func.QuestsFunctionalRunTriggerEffect,
         EFFECT_TYPE.SHOW_AWARD_WINDOW: chains_func.FunctionalShowAwardWindow,
         EFFECT_TYPE.ENTER_QUEUE: chains_func.FunctionalSwitchToRandom}
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
