# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_hangar_widget_view.py
import BigWorld
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_not_active_tooltip_view import EntryPointNotActiveTooltipView
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from frameworks.wulf import ViewFlags, ViewSettings
from armory_yard_constants import State, PDATA_KEY_ARMORY_YARD
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_widget_entry_point_view_model import ArmoryYardWidgetEntryPointViewModel
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IArmoryYardController, IBootcampController

@dependency.replace_none_kwargs(ctrl=IArmoryYardController)
def isArmoryYardEntryPointAvailable(ctrl=None):
    return ctrl.isEnabled()


class ArmoryYardWidgetEntryPointView(ViewImpl):
    __slots__ = ()
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)
    __bootcampCtrl = dependency.descriptor(IBootcampController)
    __LOW_QUALITY_PRESETS = ('LOW', 'MIN')

    @staticmethod
    def getIsActive(state):
        return ArmoryYardWidgetEntryPointView.__armoryYardCtrl.isEnabled() and not ArmoryYardWidgetEntryPointView.__bootcampCtrl.isInBootcamp()

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.armory_yard.lobby.feature.ArmoryYardWidgetView(), flags=ViewFlags.VIEW, model=ArmoryYardWidgetEntryPointViewModel())
        super(ArmoryYardWidgetEntryPointView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return EntryPointNotActiveTooltipView() if contentID == R.views.armory_yard.lobby.feature.tooltips.EntryPointNotActiveTooltipView() else super(ArmoryYardWidgetEntryPointView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(ArmoryYardWidgetEntryPointView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardWidgetEntryPointView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addCallbacks({PDATA_KEY_ARMORY_YARD: self.__checkRerollState})
        self.__updateModel()
        self.__armoryYardCtrl.onUpdated += self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated += self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated += self.__updateModel
        self.__armoryYardCtrl.serverSettings.onUpdated += self.__updateModel
        self.__armoryYardRerollCtrl.onPDataUpdated += self.__updateModel

    def _finalize(self):
        super(ArmoryYardWidgetEntryPointView, self)._finalize()
        self.__armoryYardCtrl.onUpdated -= self.__updateModel
        self.__armoryYardCtrl.onProgressUpdated -= self.__updateModel
        self.__armoryYardCtrl.onQuestsUpdated -= self.__updateModel
        self.__armoryYardCtrl.serverSettings.onUpdated -= self.__updateModel
        self.__armoryYardRerollCtrl.onPDataUpdated -= self.__updateModel

    def _getEvents(self):
        return ((self.__armoryYardCtrl.onUpdated, self.__updateModel),
         (self.__armoryYardCtrl.serverSettings.onUpdated, self.__updateModel),
         (self.__armoryYardRerollCtrl.onPDataUpdated, self.__updateModel),
         (self.viewModel.onAction, self.__showMainView))

    def __updateModel(self, *_):
        if not self.__armoryYardCtrl.isEnabled():
            self.destroy()
            return
        presetIdx = BigWorld.detectGraphicsPresetFromSystemSettings()
        lowPresets = [ BigWorld.getSystemPerformancePresetIdFromName(pName) for pName in self.__LOW_QUALITY_PRESETS ]
        self.__checkRerollState()
        with self.viewModel.transaction() as model:
            startProgressionTime, finishProgressionTime = self.__armoryYardCtrl.getProgressionTimes()
            _, endSeasonDate = self.__armoryYardCtrl.getSeasonInterval()
            state = self.__armoryYardCtrl.getState()
            model.setStartTime(startProgressionTime)
            model.setEndTime(endSeasonDate if state == State.PURCHASESTAGE else finishProgressionTime)
            model.setCurrentTime(getServerUTCTime())
            model.setIsRewardAvailable(self.__armoryYardCtrl.hasCurrentRewards())
            model.setIsLowPreset(presetIdx in lowPresets)
            if self.__armoryYardCtrl.isActive() and self.__armoryYardCtrl.isClaimedPostProgressionReward():
                state = State.COMPLETED
            model.setState(state)

    def __checkRerollState(self, diff=None):
        replacedQuestID = self.__armoryYardRerollCtrl.getReplacedTokenQuestID()
        questsToSelect = self.__armoryYardRerollCtrl.getConditionIDsForReroll(replacedQuestID)
        state = self.__armoryYardCtrl.getState()
        with self.viewModel.transaction() as model:
            model.setIsQuestRerollState(bool(replacedQuestID and questsToSelect and state != State.PURCHASESTAGE))

    def __showMainView(self):
        rerollContext = self.__armoryYardRerollCtrl.getRerollContext()
        if rerollContext is not None:
            self.__armoryYardCtrl.goToArmoryYard(tabId=TabId.QUESTS, ctx=rerollContext)
        else:
            self.__armoryYardCtrl.goToArmoryYard(tabId=TabId.PROGRESS)
        return
