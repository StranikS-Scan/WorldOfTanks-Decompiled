# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/__init__.py
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control.sales import functional
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import functional as core_func

class SalesControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.EFFECTS_GROUP: core_func.FunctionalEffectsGroup,
         EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.GLOBAL_ACTIVATE: core_func.FunctionalGlobalActivateEffect,
         EFFECT_TYPE.GLOBAL_DEACTIVATE: core_func.FunctionalGlobalDeactivateEffect,
         EFFECT_TYPE.LOAD_VIEW: functional.LoadViewEffect,
         EFFECT_TYPE.CLEAR_SCENE: core_func.FunctionalClearScene,
         EFFECT_TYPE.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.GO_SCENE: core_func.GoToSceneEffect,
         EFFECT_TYPE.SHOW_HINT: functional.FunctionalShowHint,
         EFFECT_TYPE.CLOSE_HINT: functional.FunctionalCloseHint,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.SET_GUI_ITEM_CRITERIA: core_func.FunctionalSetGuiItemCriteria}
        queries_ = {}
        ControlsFactory.__init__(self, effects, queries_)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncChapterCtx(self):
        return core_func.FunctionalChapterContext()

    def createBonuses(self, completed):
        pass


class SalesBonusesRequester(core_ctx.BonusesRequester):

    def request(self, chapterID=None):
        pass
