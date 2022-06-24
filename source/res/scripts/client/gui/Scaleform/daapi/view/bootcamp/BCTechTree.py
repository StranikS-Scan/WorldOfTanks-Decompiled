# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechTree.py
from bootcamp.Bootcamp import g_bootcamp
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.daapi.view.lobby.techtree.techtree_page import TechTree
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.shared import event_dispatcher as shared_events, events
from nations import NAMES as NATION_NAMES

class BCTechTree(TechTree):

    def invalidateBlueprintMode(self, isEnabled):
        pass

    def goToNextVehicle(self, vehCD):
        if not g_bootcamp.isResearchFreeLesson():
            nationData = g_bootcamp.getNationData()
            vehicle = self._itemsCache.items.getItemByCD(int(vehCD))
            exitEvent = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': vehicle.nationName})
            if nationData['vehicle_second'] == vehCD:
                if vehicle.isInInventory:
                    shared_events.showResearchView(vehCD, exitEvent=exitEvent)
                    return
            if nationData['vehicle_first'] == vehCD:
                shared_events.showResearchView(vehCD, exitEvent=exitEvent)
        else:
            shared_events.showResearchView(vehCD)

    def getNationTreeData(self, nationName):
        data = super(BCTechTree, self).getNationTreeData(NATION_NAMES[g_bootcamp.nation])
        dataNodes = data.get('nodes', None)
        nationData = g_bootcamp.getNationData()
        if dataNodes is not None:
            dataNodes = [ node for node in dataNodes if not NODE_STATE.isPremium(node['state']) ]
            for node in dataNodes:
                if 'vehCompareTreeNodeData' in node:
                    node['vehCompareTreeNodeData']['modeAvailable'] = False
                nodeState = node['state']
                if not NODE_STATE.inInventory(nodeState):
                    isUnlocked = NODE_STATE.isUnlocked(nodeState)
                    isVehicleSecond = node['id'] == nationData['vehicle_second']
                    if not (isVehicleSecond and isUnlocked):
                        node['state'] = NODE_STATE_FLAGS.LOCKED
                    if isUnlocked:
                        node['state'] |= NODE_STATE_FLAGS.PURCHASE_DISABLED
                    if isVehicleSecond:
                        node['state'] |= NODE_STATE_FLAGS.NEXT_2_UNLOCK
                    if NODE_STATE.isAnnouncement(nodeState):
                        node['state'] |= NODE_STATE_FLAGS.ANNOUNCEMENT
                        node['state'] |= NODE_STATE_FLAGS.NOT_CLICKABLE

            data['nodes'] = dataNodes
        return data

    def setupContextHints(self, hintID):
        pass

    def _populate(self):
        super(BCTechTree, self)._populate()
        self.__populateAfter()

    def __populateAfter(self):
        self.as_hideNationsBarS(True)
        self.as_setBlueprintsSwitchButtonStateS(enabled=False, selected=False, tooltip='', visible=False)
        self.as_setVehicleCollectorStateS(enabled=False)
