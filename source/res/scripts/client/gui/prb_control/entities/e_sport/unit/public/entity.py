# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/public/entity.py
import account_helpers
from UnitBase import UNIT_BROWSER_TYPE
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.e_sport.unit.entity import ESportBrowserEntity, ESportEntity, ESportEntryPoint, ESportBrowserEntryPoint
from gui.prb_control.entities.e_sport.unit.public.actions_validator import ESportActionsValidator
from gui.prb_control.entities.e_sport.unit.public.requester import UnitsListRequester
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

class PublicDynamicRosterSettings(DynamicRosterSettings):
    """
    Class for dynamic roster settings that modifies min players count
    like we could go in search alone
    """

    def _extractSettings(self, unit):
        kwargs = super(PublicDynamicRosterSettings, self)._extractSettings(unit)
        if kwargs and unit.getCommanderDBID() == account_helpers.getAccountDatabaseID():
            kwargs['maxEmptySlots'] = kwargs['maxSlots'] - 1
        return kwargs


class PublicBrowserEntryPoint(ESportBrowserEntryPoint):
    """
    Public battles list entry point class
    """

    def __init__(self):
        super(PublicBrowserEntryPoint, self).__init__(PREBATTLE_TYPE.UNIT)


class PublicEntryPoint(ESportEntryPoint):
    """
    Public battle entry point class
    """
    pass


class PublicBrowserEntity(ESportBrowserEntity):
    """
    Public battles list entity
    """

    def __init__(self):
        super(PublicBrowserEntity, self).__init__(PREBATTLE_TYPE.UNIT)
        self.__listReq = None
        return

    def init(self, ctx=None):
        self.__listReq = UnitsListRequester()
        self.__listReq.subscribe(UNIT_BROWSER_TYPE.ALL)
        return super(PublicBrowserEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__listReq is not None:
            if not woEvents:
                self.__listReq.unsubscribe()
            self.__listReq = None
        return super(PublicBrowserEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getBrowser(self):
        return self.__listReq

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.E_SPORT:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(PublicBrowserEntity, self).doSelectAction(action)


class PublicEntity(ESportEntity):
    """
    Public battle entity
    """

    def __init__(self):
        super(PublicEntity, self).__init__(PREBATTLE_TYPE.UNIT)

    def getQueueType(self):
        return QUEUE_TYPE.UNITS

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.E_SPORT:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(PublicEntity, self).doSelectAction(action)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(PublicEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        self._rosterSettings = self._createRosterSettings()

    def _createRosterSettings(self):
        _, unit = self.getUnit()
        return PublicDynamicRosterSettings(unit)

    def _createActionsValidator(self):
        return ESportActionsValidator(self)
