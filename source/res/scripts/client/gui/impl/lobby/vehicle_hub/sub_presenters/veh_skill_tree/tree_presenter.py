# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/veh_skill_tree/tree_presenter.py
from __future__ import absolute_import
import logging
import typing
from gui.shared.lock_overlays import lockNotificationManager
from wg_async import wg_async
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEH_SKILL_TREE_HINT_SHOWN, VEH_SKILL_TREE_PRESTIGE_GLARE_SHOWN
from adisp import adisp_process, adisp_async
from frameworks.wulf import Array
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.lobby.vehicle_hub import VehicleHubCtx, VehSkillTreeProgressionState
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.presenter_location_controller import IPresenterLocationController
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import fillNodeModel, getEliteExpirience, constructNodeUiId, deconstructNodeUiId
from gui.impl.lobby.veh_skill_tree.tooltips.final_perk_tooltip import FinalPerkTooltipView
from gui.impl.lobby.veh_skill_tree.tooltips.common_perk_tooltip import CommonPerkTooltipView
from gui.impl.lobby.veh_skill_tree.tooltips.major_perk_tooltip import MajorPerkTooltipView
from gui.impl.lobby.veh_skill_tree.tooltips.special_perk_tooltip import SpecialPerkTooltipView
from gui.impl.gui_decorators import args2params
from gui.shared.event_dispatcher import showAlternateConfigurationDialog
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.veh_post_progression.models.progression import PostProgressionAvailability, PostProgressionCompletion
from gui.veh_post_progression.models.progression_step import PostProgressionStepItem
from PlayerEvents import g_playerEvents
from post_progression_common import ROLESLOT_FEATURE, SETUPS_FEATURES
from helpers import dependency
from helpers.algorithms import shortestPath
from skeletons.gui.shared import IItemsCache
from uilogging.veh_skill_tree.logger import SkillTreeUILogger
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.tree_view_model import TreeViewModel, ResearchAvailability
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.path_model import PathModel, LineType
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.node_model import NodeModel, Type, Status
_logger = logging.getLogger(__name__)
_DIRECTION_TO_LINE_TYPE = {'r2l': LineType.RIGHTTOLEFT,
 'l2r': LineType.LEFTTORIGHT,
 'b2t': LineType.BOTTOMTOTOP,
 't2b': LineType.TOPTOBOTTOM,
 'r2b': LineType.RIGHTTOBOTTOM,
 'b2r': LineType.BOTTOMTORIGHT,
 't2r': LineType.TOPTORIGHT,
 'r2t': LineType.RIGHTTOTOP,
 'l2b': LineType.LEFTTOBOTTOM,
 'b2l': LineType.BOTTOMTOLEFT,
 't2l': LineType.TOPTOLEFT,
 'l2t': LineType.LEFTTOTOP}
_AVAILABILITY_MAP = {PostProgressionAvailability.AVAILABLE: ResearchAvailability.AVAILABLE,
 PostProgressionAvailability.VEH_NOT_IN_INVENTORY: ResearchAvailability.NOT_IN_INVENTORY,
 PostProgressionAvailability.VEH_IN_BATTLE: ResearchAvailability.IN_BATTLE,
 PostProgressionAvailability.VEH_IN_QUEUE: ResearchAvailability.IN_BATTLE,
 PostProgressionAvailability.VEH_IN_FORMATION: ResearchAvailability.IN_FORMATION,
 PostProgressionAvailability.VEH_IS_BROKEN: ResearchAvailability.NEEDS_REPAIR}
_STEP_TYPE_TO_TOOLTIP = {Type.MAJOR: MajorPerkTooltipView,
 Type.FINAL: FinalPerkTooltipView,
 Type.COMMON: CommonPerkTooltipView,
 Type.SPECIAL: SpecialPerkTooltipView}

class TreePresenter(SubModelPresenter, IPresenterLocationController):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView):
        super(TreePresenter, self).__init__(viewModel, parentView)
        self.__vehicle = None
        self.__selectedNodeIDs = None
        self.__researchedNodeIDs = None
        self.__lastSelectedNodeID = None
        self.__uiLogger = SkillTreeUILogger()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx):
        super(TreePresenter, self).initialize()
        self.__vehicle = self.__itemsCache.items.getItemByCD(vhCtx.intCD)
        self.__selectedNodeIDs = []
        self.__researchedNodeIDs = []
        self._initializeLocation()
        self.__update()

    def finalize(self):
        lockNotificationManager(False, source=VehSkillTreeProgressionState.STATE_ID)
        self._finalizeLocation()
        super(TreePresenter, self).finalize()

    def clear(self):
        self.__vehicle = None
        self.__researchedNodeIDs = None
        self.__selectedNodeIDs = None
        self.__lastSelectedNodeID = None
        self.__uiLogger = None
        super(TreePresenter, self).clear()
        return

    def _initializeLocation(self):
        self.__uiLogger.onSkillTreeOpened()

    def _finalizeLocation(self):
        self.__uiLogger.onSkillTreeClosed()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.vehicle_hub.tooltips.perk_tooltip():
            nodeID = event.getArgument('nodeID')
            nodeID = deconstructNodeUiId(self.__vehicle.intCD, int(nodeID))
            if nodeID is not None:
                step = self.__vehicle.postProgression.getStep(nodeID)
                stepType = Type(step.getType())
                if stepType in _STEP_TYPE_TO_TOOLTIP:
                    return _STEP_TYPE_TO_TOOLTIP[stepType](self.__vehicle.intCD, step, self.__getNodeStatus(step))
                _logger.error('Node type not in %s', ', '.join([ t.value for t in _STEP_TYPE_TO_TOOLTIP ]))
            else:
                _logger.error('Missing nodeID to show tooltip')
        return super(TreePresenter, self).createToolTipContent(event, contentID)

    def _getCallbacks(self):
        return super(TreePresenter, self)._getCallbacks() + (('stats.freeXP', self.__onXPStatsChanged), ('stats.vehTypeXP', self.__onXPStatsChanged))

    def _getEvents(self):
        return super(TreePresenter, self)._getEvents() + ((self.viewModel.onResearch, self.__onResearch),
         (self.viewModel.onShowNodeConfigurationWindow, self.__onShowNodeConfigurationWindow),
         (self.viewModel.onSelectNode, self.__onSelectNode),
         (self.viewModel.onFinalNodeResearchAnimationFinished, self.__onFinalNodeResearchAnimationFinished),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def __onXPStatsChanged(self, *args):
        self.viewModel.setResearchAvailability(self.__getResearchState())

    @adisp_process
    def __onResearch(self):
        if not self.__selectedNodeIDs:
            return
        action = factory.getAction(factory.PURCHASE_VEH_SKILL_TREE_STEPS, self.__vehicle, self.__selectedNodeIDs)
        result = yield factory.asyncDoAction(action)
        if result:
            self.__researchedNodeIDs = self.__selectedNodeIDs
            self.__selectedNodeIDs = []
            self.__uiLogger.onNodesResearched(self.__researchedNodeIDs)
            progression = self.__vehicle.postProgression
            if len(self.__researchedNodeIDs) == 1:
                nodeID = self.__researchedNodeIDs[0]
                node = progression.getStep(nodeID)
                if Type(node.getType()) == Type.SPECIAL:
                    yield self.__showTreeNodeDialog(node.action, nodeID)
            if Type(progression.getStep(self.__researchedNodeIDs[-1]).getType()) == Type.FINAL:
                lockNotificationManager(True, source=VehSkillTreeProgressionState.STATE_ID)
            self.__update()
            self.__researchedNodeIDs = []

    @adisp_process
    @args2params(int)
    def __onShowNodeConfigurationWindow(self, nodeID):
        nodeID = deconstructNodeUiId(self.__vehicle.intCD, int(nodeID))
        progression = self.__vehicle.postProgression
        step = progression.getStep(nodeID)
        if Type(step.getType()) == Type.SPECIAL:
            yield self.__showTreeNodeDialog(step.action, nodeID)
            self.__update()

    def __onFinalNodeResearchAnimationFinished(self):
        lockNotificationManager(False, source=VehSkillTreeProgressionState.STATE_ID)

    @args2params(int)
    def __onSelectNode(self, targetNodeID):
        self.__selectedNodeIDs = []
        targetNodeID = deconstructNodeUiId(self.__vehicle.intCD, targetNodeID)
        if targetNodeID != self.__lastSelectedNodeID:
            progression = self.__vehicle.postProgression
            targetStep = progression.getStep(targetNodeID)
            if Type(targetStep.getType()) == Type.FINAL:
                for stepID in targetStep.getParentStepIDs():
                    step = progression.getStep(stepID)
                    if not step.isReceived():
                        self.__selectedNodeIDs.append(step.stepID)

                self.__selectedNodeIDs.append(targetNodeID)
            else:
                self.__selectedNodeIDs = self.__generatePath(targetStep)
            self.__lastSelectedNodeID = targetNodeID
        else:
            self.__lastSelectedNodeID = None
        self.__update()
        return

    @adisp_async
    @adisp_process
    def __showTreeNodeDialog(self, feature, nodeID, callback):
        self.__setVehSkillTreeHintShownFlag(nodeID)
        if feature.getTechName() == ROLESLOT_FEATURE:
            action = factory.getAction(factory.SET_EQUIPMENT_SLOT_TYPE, self.__vehicle)
            yield factory.asyncDoAction(action)
        elif feature.getTechName() in SETUPS_FEATURES:
            yield self.__showAlternateConfigurationDialog(feature, nodeID)
        callback(None)
        return

    def __onCacheResync(self, _, diff):
        if self.__vehicle is not None and self.__vehicle.intCD in diff.get(GUI_ITEM_TYPE.VEHICLE, {}):
            self.__vehicle = self.__itemsCache.items.getItemByCD(self.__vehicle.intCD)
            if self.__vehicle.intCD not in diff.get(GUI_ITEM_TYPE.VEH_POST_PROGRESSION, {}):
                self.__update()
        return

    def __onDisconnected(self):
        self.__vehicle = None
        return

    def __update(self):
        if not self.isLoaded:
            _logger.warning('TreePresenter is not loaded')
            return
        elif self.__vehicle is None:
            return
        else:
            rootStep = self.__vehicle.postProgression.getRawTree().rootStep
            with self.viewModel.transaction() as vm:
                self.__fillNodes(vm)
                self.__fillIntsArray(vm.getResearchedPerks())
                vm.setResearchAvailability(self.__getResearchState())
                vm.setIsProgressionCompleted(self.__isPorgressionCompleted())
                vm.setIsPrestigeGlareShown(self.__isPrestigeGlareShown())
                vm.setRootNodeId(rootStep)
                vm.setRootNodeUiId(constructNodeUiId(self.__vehicle.intCD, rootStep))
                vm.setLockedTree(self.__isTreeLocked())
            return

    def __fillIntsArray(self, array):
        array.clear()
        for node in self.__researchedNodeIDs:
            array.addNumber(constructNodeUiId(self.__vehicle.intCD, node))

        array.invalidate()

    def __fillNodes(self, viewModel):
        nodesVM = viewModel.getNodes()
        nodesVM.clear()
        pathsVM = viewModel.getPaths()
        pathsVM.clear()
        progression = self.__vehicle.postProgression
        for step in progression.iterUnorderedSteps():
            nodeModel = NodeModel()
            self.__fillNode(step, nodeModel)
            nodesVM.addViewModel(nodeModel)
            adjacentNodes = Array()
            self.__fillPath(step, adjacentNodes)
            pathsVM.addArray(adjacentNodes)

        pathsVM.invalidate()
        nodesVM.invalidate()

    def __fillNode(self, step, nodeVM):
        fillNodeModel(nodeVM, step, self.__getNodeStatus(step), self.__vehicle)
        nodeVM.setIsHintRequired(self.__isHintRequired(step))

    def __fillPath(self, step, pathVM):
        for nextStepID, direction in zip(step.getNextStepIDs(), step.getDirections()):
            if direction in _DIRECTION_TO_LINE_TYPE:
                pathModel = PathModel()
                pathModel.setId(constructNodeUiId(self.__vehicle.intCD, nextStepID))
                pathModel.setLineType(_DIRECTION_TO_LINE_TYPE[direction])
                pathVM.addViewModel(pathModel)

    def __setVehSkillTreeHintShownFlag(self, nodeID):
        settings = AccountSettings.getUIFlag(VEH_SKILL_TREE_HINT_SHOWN)
        settings.setdefault(self.__vehicle.intCD, set()).add(nodeID)
        AccountSettings.setUIFlag(VEH_SKILL_TREE_HINT_SHOWN, settings)

    def __isHintRequired(self, step):
        nodeType = Type(step.getType())
        nodeStatus = self.__getNodeStatus(step)
        if nodeType == Type.COMMON:
            return nodeStatus == Status.DEFAULT and step.stepID == self.__vehicle.postProgression.getRawTree().rootStep
        if nodeType == Type.SPECIAL:
            return nodeStatus == Status.RESEARCHED and step.stepID not in AccountSettings.getUIFlag(VEH_SKILL_TREE_HINT_SHOWN).get(self.__vehicle.intCD, set())
        return nodeStatus == Status.DEFAULT if nodeType == Type.FINAL else False

    def __generatePath(self, targetStep):
        progression = self.__vehicle.postProgression
        graph = {}
        for step in progression.iterUnorderedSteps():
            graph[step] = []
            for nextStepID in step.getNextStepIDs():
                nextStep = progression.getStep(nextStepID)
                graph[step].append((nextStep, nextStep.getPrice().xp if not nextStep.isReceived() else 0.0))

        rootStep = progression.getStep(progression.getRawTree().rootStep)
        path = shortestPath(graph, rootStep, targetStep)
        return [ step.stepID for step in path if not step.isReceived() ]

    def __getNodeStatus(self, step):
        if step.isReceived():
            return Status.RESEARCHED
        return Status.SELECTED if step.stepID in self.__selectedNodeIDs else Status.DEFAULT

    def __getResearchState(self):
        progression = self.__vehicle.postProgression
        _, reason = self.__vehicle.postProgressionAvailability()
        researchCost = sum([ progression.getStep(nodeID).getPrice().xp for nodeID in self.__selectedNodeIDs ])
        freeXP = self.__itemsCache.items.stats.freeXP
        eliteXP = getEliteExpirience(exclude=(self.__vehicle.intCD,))
        return ResearchAvailability.NOT_ENOUGH_EXP if reason == PostProgressionAvailability.AVAILABLE and researchCost > self.__vehicle.xp + freeXP + eliteXP else _AVAILABILITY_MAP.get(reason, ResearchAvailability.AVAILABLE)

    @adisp_async
    @wg_async
    def __showAlternateConfigurationDialog(self, feature, nodeID, callback):
        yield showAlternateConfigurationDialog(self.__vehicle.intCD, feature, nodeID)
        callback(None)
        return

    def __isPorgressionCompleted(self):
        return self.__vehicle.postProgression.getCompletion() == PostProgressionCompletion.FULL

    def __isPrestigeGlareShown(self):
        return self.__vehicle.intCD in AccountSettings.getUIFlag(VEH_SKILL_TREE_PRESTIGE_GLARE_SHOWN)

    def __isTreeLocked(self):
        _, reason = self.__vehicle.postProgressionAvailability()
        return reason == PostProgressionAvailability.VEH_NOT_IN_INVENTORY or not self.__vehicle.isUnlocked
