# Embedded file name: scripts/client/gui/prb_control/factories/PrebattleFactory.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import prb_control
from gui.prb_control.context.prb_ctx import LeavePrbCtx, OpenPrbListCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional.no_prebattle import NoPrbFunctional
from gui.prb_control.functional.not_supported import PrbNotSupportedFunctional
from gui.prb_control.functional.not_supported import NotSupportedEntry
from gui.prb_control.functional.default import PrbInitFunctional
from gui.prb_control.functional.training import TrainingEntry, TrainingFunctional
from gui.prb_control.functional.squad import SquadEntry, SquadFunctional
from gui.prb_control.functional.company import CompanyEntry, CompanyFunctional
from gui.prb_control.functional.battle_session import BattleSessionEntry
from gui.prb_control.functional.battle_session import BattleSessionFunctional
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
_SUPPORTED_PREBATTLE = {PREBATTLE_TYPE.TRAINING: (TrainingEntry, TrainingFunctional),
 PREBATTLE_TYPE.SQUAD: (SquadEntry, SquadFunctional),
 PREBATTLE_TYPE.COMPANY: (CompanyEntry, CompanyFunctional),
 PREBATTLE_TYPE.TOURNAMENT: (BattleSessionEntry, BattleSessionFunctional),
 PREBATTLE_TYPE.CLAN: (BattleSessionEntry, BattleSessionFunctional)}
_OPEN_PRB_LIST_BY_ACTION = {PREBATTLE_ACTION_NAME.TRAINING_LIST: PREBATTLE_TYPE.TRAINING,
 PREBATTLE_ACTION_NAME.LEAVE_TRAINING_LIST: PREBATTLE_TYPE.TRAINING,
 PREBATTLE_ACTION_NAME.COMPANY_LIST: PREBATTLE_TYPE.COMPANY,
 PREBATTLE_ACTION_NAME.SPEC_BATTLE_LIST: PREBATTLE_TYPE.CLAN}
_CREATE_PRB_BY_ACTION = {PREBATTLE_ACTION_NAME.SQUAD: PREBATTLE_TYPE.SQUAD}

class PrebattleFactory(ControlFactory):

    def createEntry(self, ctx):
        prbType = ctx.getPrbType()
        if prbType in _SUPPORTED_PREBATTLE:
            prbEntry = _SUPPORTED_PREBATTLE[prbType][0]()
        else:
            LOG_ERROR('Given type of prebattle is not supported', prbType)
            prbEntry = NotSupportedEntry()
        return prbEntry

    def createFunctional(self, dispatcher, ctx):
        clientPrb = prb_control.getClientPrebattle()
        if clientPrb is not None:
            if prb_control.isPrebattleSettingsReceived(prebattle=clientPrb):
                prbSettings = prb_control.getPrebattleSettings(prebattle=clientPrb)
                prbType = prb_control.getPrebattleType(settings=prbSettings)
                if prbType in _SUPPORTED_PREBATTLE:
                    prbFunctional = _SUPPORTED_PREBATTLE[prbType][1](prbSettings)
                    for listener in dispatcher._globalListeners:
                        prbFunctional.addListener(listener())

                else:
                    LOG_ERROR('Prebattle with given type is not supported', prbType)
                    prbFunctional = PrbNotSupportedFunctional(prbSettings)
            else:
                prbFunctional = PrbInitFunctional()
        else:
            prbFunctional = NoPrbFunctional()
        return prbFunctional

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo()
        return PlayerDecorator(info.isCreator, info.isReady())

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREBATTLE, functional.getPrbType(), True)

    def createLeaveCtx(self):
        return LeavePrbCtx(waitingID='prebattle/leave')

    def getLeaveCtxByAction(self, action):
        ctx = None
        if action == PREBATTLE_ACTION_NAME.PREBATTLE_LEAVE:
            ctx = self.createLeaveCtx()
        return ctx

    def getOpenListCtxByAction(self, action):
        ctx = None
        if action in _OPEN_PRB_LIST_BY_ACTION:
            ctx = OpenPrbListCtx(_OPEN_PRB_LIST_BY_ACTION[action])
        return ctx
