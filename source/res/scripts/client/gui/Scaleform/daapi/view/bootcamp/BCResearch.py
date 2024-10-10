# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCResearch.py
from bootcamp.Bootcamp import g_bootcamp, DISABLED_TANK_LEVELS
from gui.techtree import dumpers
from gui.techtree.research_items_data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.research_page import Research
from gui.techtree.settings import NODE_STATE
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from items import getTypeOfCompactDescr
from skeletons.tutorial import ITutorialLoader
from uilogging.deprecated.bootcamp.loggers import BootcampLogger
from uilogging.deprecated.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.deprecated.bootcamp.constants import BC_LOG_ACTIONS, BC_LOG_KEYS, LIMITS
from uilogging.deprecated.bootcamp.loggers import BootcampUILogger

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
                if not NODE_STATE.inInventory(state) and not (NODE_STATE.isAvailable2Unlock(state) or NODE_STATE.isAvailable2Buy(state)):
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
            if not NODE_STATE.isAvailable2Unlock(state) and self._isLastUnlocked(nodeCD) and not NODE_STATE.inInventory(state):
                state |= NODE_STATE_FLAGS.LAST_2_BUY
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


@loggerTarget(logKey=BC_LOG_KEYS.BC_RESEARCH_VEHICLES, loggerCls=BootcampUILogger)
class BCResearch(Research):
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_RESEARCH_VEHICLES)
    tutorialLoader = dependency.descriptor(ITutorialLoader)
    BC_MESSAGE_WINDOW_OPEN_SOUND_ID = 'bc_info_line_woosh'
    SECOND_VEHICLE_FLAG = 'SecondVehicleIsOnResearch'

    def __init__(self, ctx=None):
        super(BCResearch, self).__init__(ctx, skipConfirm=False)
        self._data = BCResearchItemsData(dumpers.ResearchItemsObjDumper())
        self._resolveLoadCtx(ctx=ctx)

    @loggerEntry
    def _populate(self):
        super(BCResearch, self)._populate()

    @simpleLog(action=BC_LOG_ACTIONS.UNLOCK_ITEM, restrictions={'lesson_id': lambda x: x <= LIMITS.RESEARCH_MAX_LESSON}, logOnce=True)
    def request4Unlock(self, unlockCD, topLevel):
        self.soundManager.playSound(self.BC_MESSAGE_WINDOW_OPEN_SOUND_ID)
        super(BCResearch, self).request4Unlock(unlockCD, topLevel)

    def _doUnlockItemAction(self, itemCD, unlockProps):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BC_UNLOCK_ITEM, itemCD, unlockProps, skipConfirm=self._skipConfirm)

    @simpleLog(action=BC_LOG_ACTIONS.BUY_ITEM, restrictions={'lesson_id': lambda x: x <= LIMITS.RESEARCH_MAX_LESSON}, logOnce=True)
    def request4Buy(self, itemCD):
        if getTypeOfCompactDescr(int(itemCD)) != GUI_ITEM_TYPE.VEHICLE:
            self.soundManager.playSound(self.BC_MESSAGE_WINDOW_OPEN_SOUND_ID)
        super(BCResearch, self).request4Buy(itemCD)

    def _doBuyAndInstallItemAction(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BC_BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD(), skipConfirm=self._skipConfirm)

    def onModuleHover(self, itemCD):
        pass

    def invalidateVehCompare(self):
        pass

    def invalidateUnlocks(self, unlocks):
        self.redraw()

    def exitFromResearch(self):
        self.uiBootcampLogger.logOnce(action=BC_LOG_ACTIONS.BUTTON_BACK_TO_HANGAR)
        super(BCResearch, self).exitFromResearch()

    def goToVehicleView(self, itemCD):
        vehicle = self._itemsCache.items.getItemByCD(int(itemCD))
        if vehicle.isInInventory:
            self.uiBootcampLogger.logOnce(action=BC_LOG_ACTIONS.BUTTON_VIEW_IN_HANGAR)
            shared_events.selectVehicleInHangar(itemCD)

    def setupContextHints(self, hintID, hintsArgs=None):
        pass

    def redraw(self):
        super(BCResearch, self).redraw()
        nationData = g_bootcamp.getNationData()
        isSecondVehicle = self._data.getRootCD() == nationData['vehicle_second']
        flags = self.tutorialLoader.tutorial.getFlags()
        isFlagActive = flags.isActiveFlag(self.SECOND_VEHICLE_FLAG)
        if isSecondVehicle and not isFlagActive:
            flags.activateFlag(self.SECOND_VEHICLE_FLAG)
            self.tutorialLoader.tutorial.invalidateFlags()
        elif not isSecondVehicle and isFlagActive:
            flags.deactivateFlag(self.SECOND_VEHICLE_FLAG)
            self.tutorialLoader.tutorial.invalidateFlags()

    def _getRootData(self):
        result = super(BCResearch, self)._getRootData()
        result['vehicleButton']['compareBtnEnabled'] = False
        result['vehicleButton']['goToVehicleViewBtnVisible'] = False
        return result

    def _dispose(self):
        self._listener.stopListen()
        super(BCResearch, self)._dispose()

    def _getExperienceInfoLinkage(self):
        return RESEARCH_ALIASES.BOOTCAMP_EXPERIENCE_INFO
