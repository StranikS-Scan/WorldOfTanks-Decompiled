# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/tech_tree_custom_hints.py
import weakref
import typing
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.techtree.custom_tech_tree_hint import CustomTechTreeHint, HintIDs
from gui.impl.gui_decorators import args2params
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.techtree.event_helpers import TechTreeFormatters
from gui.techtree.techtree_dp import g_techTreeDP
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.techtree_events import ITechTreeEventsListener
from tutorial.hints_manager import HINT_SHOWN_STATUS
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.techtree.tech_tree_custom_hints_model import TechTreeCustomHintsModel

class ITechTreeCustomHint(object):

    @classmethod
    def getHintID(cls):
        raise NotImplementedError

    def markHint(self):
        raise NotImplementedError

    def getHintModel(self):
        raise NotImplementedError

    def needShowHint(self):
        raise NotImplementedError


class EventActionHint(ITechTreeCustomHint):
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    __slots__ = ('__nationID', '__actionID', '__nodeID')

    def __init__(self, nationID, nodeID, actionID=None):
        self.__nationID = nationID
        self.__nodeID = nodeID
        self.__actionID = actionID if actionID is not None else self.__techTreeEventsListener.getActiveAction(self.__nodeID, self.__nationID)
        return

    @classmethod
    def getHintID(cls):
        return HintIDs.TECHTREEACTION

    def markHint(self):
        self.__techTreeEventsListener.setNationViewed(self.__nationID)

    def getHintModel(self):
        model = CustomTechTreeHint()
        model.setHintID(self.getHintID())
        model.setHintText(TechTreeFormatters.getActionInfoStr(self.__techTreeEventsListener.getUserName(self.__actionID), self.__techTreeEventsListener.getFinishTime(self.__actionID)))
        model.setNodeID(self.__nodeID)
        return model

    def needShowHint(self):
        return self.__nationID in self.__techTreeEventsListener.getNations(unviewed=True)


class BlueprintConvertHint(ITechTreeCustomHint):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getHintID(cls):
        return HintIDs.BLUEPRINTSCONVERT

    def markHint(self):
        self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.BLUEPRINTS_TECHTREE_CONVERT_BUTTON_HINT: HINT_SHOWN_STATUS})

    def getHintModel(self):
        model = CustomTechTreeHint()
        model.setHintID(self.getHintID())
        model.setHintText(backport.text(R.strings.tutorial.blueprints.convertButton()))
        return model

    def needShowHint(self):
        return self.__itemsCache.items.blueprints.getIntelligenceCount() > 0 and not self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.BLUEPRINTS_TECHTREE_CONVERT_BUTTON_HINT)


class TechTreeCustomHints(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __slots__ = ('__viewRef', '__activeHints')

    def __init__(self, view):
        self.__viewRef = weakref.ref(view)
        self.__activeHints = {}

    @property
    def hintsModel(self):
        return self.__viewRef().viewModel.hints

    def init(self, nationID=None):
        self.hintsModel.onHintShown += self.__onHintShown
        if not self.__limitedUIController.isRuleCompleted(LuiRules.TECH_TREE_EVENTS):
            self.__techTreeEventsListener.setNationViewed(nationID)
        blueprintsConvertHint = BlueprintConvertHint()
        if blueprintsConvertHint.needShowHint():
            self.__activeHints[blueprintsConvertHint.getHintID()] = blueprintsConvertHint
        if nationID is not None:
            self.setCurrentNation(nationID)
        else:
            self.__updateHintsModel()
        return

    def fini(self):
        self.hintsModel.onHintShown -= self.__onHintShown

    def setCurrentNation(self, nationID):
        hasAction = self.__techTreeEventsListener.hasActiveAction
        oldHint = self.__activeHints.pop(EventActionHint.getHintID(), None)
        if oldHint is not None:
            oldHint.markHint()
        if not self.__limitedUIController.isRuleCompleted(LuiRules.TECH_TREE_EVENTS):
            self.__techTreeEventsListener.setNationViewed(nationID)
        for vehicleCD in self.__techTreeEventsListener.getVehicles(nationID):
            if not any((hasAction(boundCD, nationID) for boundCD in g_techTreeDP.getTopLevel(vehicleCD))):
                hint = EventActionHint(nationID, vehicleCD)
                if hint.needShowHint():
                    self.__activeHints[hint.getHintID()] = hint
                break

        self.__updateHintsModel()
        return

    def markHints(self):
        for hint in self.__activeHints.values():
            hint.markHint()

    def markNationHints(self, nationID):
        if nationID is not None:
            self.__techTreeEventsListener.setNationViewed(nationID)
        return

    def __updateHintsModel(self):
        activeHints = self.hintsModel.getActiveHints()
        activeHints.clear()
        for hint in self.__activeHints.values():
            activeHints.addViewModel(hint.getHintModel())

        activeHints.invalidate()

    @args2params(HintIDs)
    def __onHintShown(self, hintID):
        hint = self.__activeHints.pop(hintID, None)
        if hint is not None:
            hint.markHint()
        self.__updateHintsModel()
        return
