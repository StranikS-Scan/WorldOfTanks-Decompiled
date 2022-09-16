# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/entity.py
from debug_utils import LOG_ERROR
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.permissions import SquadPermissions
from gui.prb_control.entities.base.unit.entity import UnitEntryPoint, UnitEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.prb_control.items import SelectResult
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.gen.resources import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from wg_async import wg_async, wg_await

class SquadEntryPoint(UnitEntryPoint):

    def makeDefCtx(self):
        return SquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def join(self, ctx, callback=None):
        super(SquadEntryPoint, self).join(ctx, callback)
        LOG_ERROR('Player can join to squad by invite only')
        if callback:
            callback(False)


class SquadEntity(UnitEntity):
    __appLoader = dependency.descriptor(IAppLoader)

    def init(self, ctx=None):
        self.invalidateVehicleStates()
        return super(SquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        self.__clearCustomVehicleStates()
        super(SquadEntity, self).fini(ctx, woEvents)

    def canKeepMode(self):
        return False

    def hasLockedState(self):
        pInfo = self.getPlayerInfo()
        return pInfo.isReady and super(SquadEntity, self).hasLockedState()

    def unit_onUnitRosterChanged(self):
        rosterSettings = self._createRosterSettings()
        if rosterSettings != self.getRosterSettings():
            self._rosterSettings = rosterSettings
            self.invalidateVehicleStates()
            self._vehiclesWatcher.validate()
        self._invokeListeners('onUnitRosterChanged')
        g_eventDispatcher.updateUI()

    def rejoin(self):
        super(SquadEntity, self).rejoin()
        self.unit_onUnitRosterChanged()
        self._actionsHandler.setUnitChanged()

    def invalidateVehicleStates(self, vehicles=None):
        state = Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT
        if vehicles:
            criteria = REQ_CRITERIA.IN_CD_LIST(vehicles)
        else:
            criteria = REQ_CRITERIA.INVENTORY
        vehicles = self.itemsCache.items.getVehicles(criteria)
        updatedVehicles = [ intCD for intCD, v in vehicles.iteritems() if self._updateVehicleState(v, state) ]
        if updatedVehicles:
            g_prbCtrlEvents.onVehicleClientStateChanged(updatedVehicles)

    def isBalancedSquadEnabled(self):
        return False

    def getSquadLevelBounds(self):
        pass

    def showDialog(self, meta, callback):
        self.__showDefaultDialog(meta, callback)

    def doSelectAction(self, action):
        name = action.actionName
        if name in self._showUnitActionNames:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(SquadEntity, self).doSelectAction(action)

    @property
    def _showUnitActionNames(self):
        pass

    def _buildPermissions(self, roles, flags, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        return SquadPermissions(roles, flags, isCurrentPlayer, isPlayerReady)

    def _createActionsHandler(self):
        return SquadActionsHandler(self)

    def _createActionsValidator(self):
        return SquadActionsValidator(self)

    def _vehicleStateCondition(self, v):
        return True

    def _updateVehicleState(self, vehicle, state):
        invalid = not self._vehicleStateCondition(vehicle)
        stateSet = vehicle.getCustomState() == state
        if invalid and not stateSet:
            vehicle.setCustomState(state)
        elif not invalid and stateSet:
            vehicle.clearCustomState()
        changed = invalid != stateSet
        return changed

    def __clearCustomVehicleStates(self):
        vehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        updatedVehicles = []
        for intCD, v in vehicles.iteritems():
            if v.isCustomStateSet():
                v.clearCustomState()
                updatedVehicles.append(intCD)

        if updatedVehicles:
            g_prbCtrlEvents.onVehicleClientStateChanged(updatedVehicles)

    def __resourceSplitter(self, resourceStr):
        resourceList = resourceStr.split('/')
        if not resourceList:
            return None
        else:
            current = R.strings.dialogs.dyn(resourceList[0])
            i = 1
            while i < len(resourceList):
                current = current.dyn(resourceList[i])
                i += 1

            return current

    @wg_async
    def __showDefaultDialog(self, meta, callback):
        from gui.shared.event_dispatcher import showDynamicButtonInfoDialogBuilder
        key = meta.getKey()
        res = self.__resourceSplitter(key)
        if res:
            app = self.__appLoader.getApp()
            parent = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            result = yield wg_await(showDynamicButtonInfoDialogBuilder(res, None, '', parent))
            callback(result)
        return
