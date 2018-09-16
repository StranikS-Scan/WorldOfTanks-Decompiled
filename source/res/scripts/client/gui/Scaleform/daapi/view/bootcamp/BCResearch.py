# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCResearch.py
from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
from gui.shared import events, EVENT_BUS_SCOPE
from bootcamp.Bootcamp import g_bootcamp, DISABLED_TANK_LEVELS
from debug_utils import LOG_DEBUG
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree import dumpers

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


class BCResearch(Research):

    def __init__(self, ctx=None):
        super(BCResearch, self).__init__(ctx, skipConfirm=True)
        self._data = BCResearchItemsData(dumpers.ResearchItemsObjDumper())
        self._resolveLoadCtx(ctx=ctx)

    def request4Info(self, itemCD, rootCD):
        LOG_DEBUG('BCResearch.request4Info', itemCD, rootCD)
        super(BCResearch, self).request4Info(itemCD, rootCD)

    def request4Unlock(self, unlockCD, vehCD, unlockIdx, xpCost):
        nationData = g_bootcamp.getNationData()
        if nationData['module'] == unlockCD:
            super(BCResearch, self).request4Unlock(unlockCD, vehCD, unlockIdx, xpCost)
        elif nationData['vehicle_second'] == unlockCD:
            shared_events.showVehiclePreview(int(unlockCD), self.alias)
        else:
            super(BCResearch, self).request4Unlock(unlockCD, vehCD, unlockIdx, xpCost)

    def request4Buy(self, itemCD):
        nationData = g_bootcamp.getNationData()
        if nationData['module'] == itemCD:
            super(BCResearch, self).request4Buy(itemCD)
        elif nationData['vehicle_second'] == itemCD:
            shared_events.showVehiclePreview(int(itemCD), self.alias)
        else:
            super(BCResearch, self).request4Buy(itemCD)

    def invalidateVehCompare(self):
        pass

    def goToTechTree(self, nation):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)

    def as_setRootNodeVehCompareDataS(self, unlocks):
        unlocks['modeAvailable'] = False
        super(BCResearch, self).as_setRootNodeVehCompareDataS(unlocks)

    def getResearchItemsData(self, vehCD, rootChanged):
        LOG_DEBUG('BCResearch.getResearchItemsData', g_bootcamp.getLessonNum())
        dumpData = super(BCResearch, self).getResearchItemsData(vehCD, rootChanged)
        nodes = dumpData.get('nodes', [])
        for node in nodes:
            if 'vehCompareRootData' in node:
                node['vehCompareRootData']['modeAvailable'] = False
            if 'vehCompareTreeNodeData' in node:
                node['vehCompareTreeNodeData']['modeAvailable'] = False
            node['showVehicleBtnVisible'] = False
            node['showVehicleBtnEnabled'] = False

        dumpData['global']['hasNationTree'] = False
        return dumpData

    def goToVehicleView(self, itemCD):
        LOG_DEBUG('BCResearch.goToVehicleView', itemCD, self.alias)
        itemsCache = dependency.instance(IItemsCache)
        vehicle = itemsCache.items.getItemByCD(int(itemCD))
        if vehicle.isPreviewAllowed():
            shared_events.showVehiclePreview(int(itemCD), self.alias)
        elif vehicle.isInInventory:
            shared_events.selectVehicleInHangar(itemCD)

    def setupContextHints(self, hintID):
        pass

    def _dispose(self):
        self._listener.stopListen()
        super(BCResearch, self)._dispose()

    def _getExperienceInfoLinkage(self):
        return RESEARCH_ALIASES.BOOTCAMP_EXPERIENCE_INFO
