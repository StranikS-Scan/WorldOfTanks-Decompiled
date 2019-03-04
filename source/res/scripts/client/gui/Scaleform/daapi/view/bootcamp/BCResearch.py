# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCResearch.py
from bootcamp.Bootcamp import g_bootcamp, DISABLED_TANK_LEVELS
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
from gui.shared import event_dispatcher as shared_events

class BCResearchItemsData(ResearchItemsData):

    def __init__(self, dumper):
        super(BCResearchItemsData, self).__init__(dumper)
        lessonNum = g_bootcamp.getLessonNum()
        self.__overrideResearch = lessonNum < g_bootcamp.getContextIntParameter('researchFreeLesson')
        self.__secondVehicleResearch = lessonNum < g_bootcamp.getContextIntParameter('researchSecondVehicleLesson')
        nationData = g_bootcamp.getNationData()
        self.__firstVehicleNode = nationData['vehicle_first']
        self.__secondVehicleNode = nationData['vehicle_second']
        self.__moduleNodeCD = nationData['module']

    def _addNode(self, nodeCD, node):
        state = node.getState()
        if not NODE_STATE.isAnnouncement(state):
            if self.__overrideResearch:
                if not NODE_STATE.inInventory(state):
                    state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.NOT_CLICKABLE)
                if self.getRootCD() == self.__firstVehicleNode:
                    if self.__secondVehicleResearch:
                        if nodeCD == self.__secondVehicleNode:
                            return -1
                    if not NODE_STATE.inInventory(state) and not NODE_STATE.isInstalled(state) and nodeCD != self.__moduleNodeCD and nodeCD != self.__secondVehicleNode:
                        return -1
            item = self._items.getItemByCD(nodeCD)
            if item.level in DISABLED_TANK_LEVELS and NODE_STATE.isAvailable2Buy(state):
                state = NODE_STATE.add(state, NODE_STATE_FLAGS.PURCHASE_DISABLED)
        if NODE_STATE.hasBlueprints(state):
            state = NODE_STATE.remove(state, NODE_STATE_FLAGS.BLUEPRINT)
        node.setState(state)
        return super(BCResearchItemsData, self)._addNode(nodeCD, node)

    def _addTopNode(self, nodeCD, node):
        state = node.getState()
        if self.__overrideResearch:
            if not NODE_STATE.inInventory(state):
                state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.NOT_CLICKABLE)
        if nodeCD != self.__firstVehicleNode:
            state = NODE_STATE.addIfNot(state, NODE_STATE_FLAGS.LOCKED)
        node.setState(state)
        return super(BCResearchItemsData, self)._addTopNode(nodeCD, node)

    def _change2Unlocked(self, node):
        super(BCResearchItemsData, self)._change2Unlocked(node)
        state = node.getState()
        state = NODE_STATE.removeIfHas(state, NODE_STATE_FLAGS.BLUEPRINT)
        node.setState(state)

    def _getBlueprintsProps(self, vehicleCD, level):
        return None

    def _getNewCost(self, vehicleCD, level, oldCost):
        return (oldCost, 0)


class BCResearch(Research):

    def __init__(self, ctx=None):
        super(BCResearch, self).__init__(ctx, skipConfirm=True)
        self._data = BCResearchItemsData(dumpers.ResearchItemsObjDumper())
        self._resolveLoadCtx(ctx=ctx)

    def request4Unlock(self, unlockCD, topLevel):
        nationData = g_bootcamp.getNationData()
        if nationData['vehicle_second'] == unlockCD:
            shared_events.showOldVehiclePreview(int(unlockCD), self.alias)
        else:
            super(BCResearch, self).request4Unlock(unlockCD, topLevel)

    def request4Buy(self, itemCD):
        nationData = g_bootcamp.getNationData()
        if nationData['vehicle_second'] == itemCD:
            shared_events.showOldVehiclePreview(int(itemCD), self.alias)
        else:
            super(BCResearch, self).request4Buy(itemCD)

    def invalidateVehCompare(self):
        pass

    def invalidateUnlocks(self, unlocks):
        self.redraw()

    def goToVehicleView(self, itemCD):
        vehicle = self._itemsCache.items.getItemByCD(int(itemCD))
        if vehicle.isPreviewAllowed():
            shared_events.showOldVehiclePreview(int(itemCD), self.alias)
        elif vehicle.isInInventory:
            shared_events.selectVehicleInHangar(itemCD)

    def setupContextHints(self, hintID):
        pass

    def _getRootData(self):
        result = super(BCResearch, self)._getRootData()
        result['compareBtnEnabled'] = False
        result['previewBtnEnabled'] = False
        return result

    def _dispose(self):
        self._listener.stopListen()
        super(BCResearch, self)._dispose()

    def _getExperienceInfoLinkage(self):
        return RESEARCH_ALIASES.BOOTCAMP_EXPERIENCE_INFO
