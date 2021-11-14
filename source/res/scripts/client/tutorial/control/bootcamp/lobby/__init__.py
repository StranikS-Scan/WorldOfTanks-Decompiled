# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/__init__.py
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control import functional as core_func
from tutorial.control.bootcamp.lobby import queries, functional, context as bc_ctx
from tutorial.control.bootcamp.lobby.conditions import BOOTCAMP_CONDITION_TYPE

class BootcampLobbyControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.EFFECTS_GROUP: core_func.FunctionalEffectsGroup,
         EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.SET_VAR: core_func.FunctionalSetVarAction,
         EFFECT_TYPE.SET_GUI_ITEM_CRITERIA: core_func.FunctionalSetGuiItemCriteria,
         EFFECT_TYPE.SET_GUI_ITEM_VIEW_CRITERIA: core_func.FunctionalSetGuiItemViewCriteria,
         EFFECT_TYPE.SET_ACTION: core_func.FunctionalSetAction,
         EFFECT_TYPE.REMOVE_ACTION: core_func.FunctionalRemoveAction,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.SHOW_DIALOG: core_func.FunctionalShowDialogEffect,
         EFFECT_TYPE.SHOW_WINDOW: core_func.FunctionalShowWindowEffect,
         EFFECT_TYPE.SET_ITEM_PROPS: core_func.FunctionalSetGuiItemPropertiesEffect,
         EFFECT_TYPE.PLAY_ANIMATION: core_func.FunctionalPlayAnimationEffect,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.REQUEST_EXCLUSIVE_HINT: functional.FunctionalRequestExclusiveHintEffect,
         EFFECT_TYPE.UPDATE_EXCLUSIVE_HINTS: functional.FunctionalUpdateExclusiveHintsEffect,
         EFFECT_TYPE.START_VSE_PLAN: functional.FunctionalStartVSEPlan,
         EFFECT_TYPE.SET_ALLOWED_TO_FIGHT: core_func.FunctionalSetAllowedToFightEffect,
         EFFECT_TYPE.RESTORE_CHECKPOINT: functional.FunctionalRestoreCheckpointEffect,
         EFFECT_TYPE.SAVE_CHECKPOINT: functional.FunctionalSaveCheckpointEffect,
         EFFECT_TYPE.SAVE_ACCOUNT_SETTING: functional.FunctionalSetNationEffect,
         EFFECT_TYPE.SELECT_VEHICLE_IN_HANGAR: core_func.FunctionalSelectVehicleByCDEffect,
         EFFECT_TYPE.PLAY_VIDEO: functional.FunctionalPlayFinalVideoEffect,
         EFFECT_TYPE.PLAY_SOUND: core_func.FunctionalPlaySoundEffect,
         EFFECT_TYPE.FINISH_TRAINING: functional.FunctionalFinishBootcampEffect,
         EFFECT_TYPE.CLOSE_VIEW: core_func.FunctionalCloseViewEffect,
         EFFECT_TYPE.GLOBAL_ACTIVATE: core_func.FunctionalGlobalActivateEffect,
         EFFECT_TYPE.GLOBAL_DEACTIVATE: core_func.FunctionalGlobalDeactivateEffect,
         EFFECT_TYPE.SHOW_DEMO_ACCOUNT_RENAMING: functional.FunctionalShowDemoAccRenameOverlay}
        queries_ = {'bootcampVideo': queries.VideoDialogContentQuery,
         'bootcampSubtitle': queries.SubtitleDialogContentQuery,
         'bootcampMessage': queries.MessageDialogContentQuery,
         'bootcampSelectNation': queries.SubtitleDialogContentQuery}
        customConditions = {BOOTCAMP_CONDITION_TYPE.CHECKPOINT_REACHED: functional.FunctionalCheckpointReachedCondition}
        ControlsFactory.__init__(self, effects, queries_, customConditions)

    def createBonuses(self, _):
        return bc_ctx.BootcampBonusesRequester()

    def createSoundPlayer(self):
        return core_ctx.SimpleSoundPlayer()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncChapterCtx(self):
        return functional.FunctionalBootcampLobbyChapterContext()
