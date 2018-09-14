# Embedded file name: scripts/client/gui/prb_control/factories/PrebattleFactory.py
import inspect
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.context import prb_ctx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional import battle_session
from gui.prb_control.functional import company
from gui.prb_control.functional import default
from gui.prb_control.functional import not_supported
from gui.prb_control.functional import training
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
__all__ = ('PrebattleFactory',)
_PAN = PREBATTLE_ACTION_NAME
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.TRAINING: training.TrainingEntry,
 PREBATTLE_TYPE.COMPANY: company.CompanyEntry,
 PREBATTLE_TYPE.TOURNAMENT: battle_session.BattleSessionEntry,
 PREBATTLE_TYPE.CLAN: battle_session.BattleSessionEntry}
_SUPPORTED_ENTRY_BY_ACTION = {_PAN.TRAINING: (default.PrbIntro, (PREBATTLE_TYPE.TRAINING,)),
 _PAN.COMPANY: (default.PrbIntro, (PREBATTLE_TYPE.COMPANY,)),
 _PAN.SPEC_BATTLE: (battle_session.BattleSessionListEntry, None)}
_SUPPORTED_FUNCTIONAL = {PREBATTLE_TYPE.TRAINING: training.TrainingFunctional,
 PREBATTLE_TYPE.COMPANY: company.CompanyFunctional,
 PREBATTLE_TYPE.TOURNAMENT: battle_session.BattleSessionFunctional,
 PREBATTLE_TYPE.CLAN: battle_session.BattleSessionFunctional}
_SUPPORTED_INTRO = {PREBATTLE_TYPE.TRAINING: training.TrainingIntroFunctional,
 PREBATTLE_TYPE.COMPANY: company.CompanyIntroFunctional}

class PrebattleFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            prbEntry = default.PrbIntro(ctx.getEntityType())
        else:
            prbType = ctx.getEntityType()
            clazz = None
            if prbType in _SUPPORTED_ENTRY_BY_TYPE:
                clazz = _SUPPORTED_ENTRY_BY_TYPE[prbType]
            if clazz is None:
                LOG_ERROR('Given type of prebattle is not supported', prbType)
                clazz = not_supported.NotSupportedEntry
            prbEntry = clazz()
        return prbEntry

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.PREBATTLE:
            created = self._createByAccountState(ctx)
        else:
            created = self._createByFlags(ctx)
        return created

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo()
        return PlayerDecorator(info.isCreator, info.isReady())

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREBATTLE, functional.getEntityType(), True, functional.hasLockedState(), isinstance(functional, default.IntroPrbFunctional))

    def createLeaveCtx(self, flags = FUNCTIONAL_FLAG.UNDEFINED):
        return prb_ctx.LeavePrbCtx(waitingID='prebattle/leave', flags=flags)

    def _createByAccountState(self, ctx):
        created = None
        clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            if prb_getters.isPrebattleSettingsReceived(prebattle=clientPrb):
                prbSettings = prb_getters.getPrebattleSettings(prebattle=clientPrb)
                prbType = prb_getters.getPrebattleType(settings=prbSettings)
                clazz = None
                if prbType in _SUPPORTED_FUNCTIONAL:
                    clazz = _SUPPORTED_FUNCTIONAL[prbType]
                ctx.removeFlags(FUNCTIONAL_FLAG.PREBATTLE_BITMASK)
                ctx.addFlags(FUNCTIONAL_FLAG.PREBATTLE)
                if clazz:
                    created = clazz(prbSettings)
                else:
                    LOG_ERROR('Prebattle with given type is not supported', prbType)
                    created = not_supported.NotSupportedFunctional()
            elif not ctx.hasFlags(FUNCTIONAL_FLAG.PREBATTLE_INIT):
                ctx.removeFlags(FUNCTIONAL_FLAG.PREBATTLE_BITMASK)
                ctx.addFlags(FUNCTIONAL_FLAG.PREBATTLE_INIT)
                created = default.PrbInitFunctional()
        else:
            created = self._createByPrbType(ctx)
        return created

    def _createByFlags(self, ctx):
        if not ctx.hasFlags(FUNCTIONAL_FLAG.PREBATTLE):
            created = self._createByAccountState(ctx)
        else:
            created = self._createNoPrbFunctional(ctx)
        return created

    def _createByPrbType(self, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.PREBATTLE:
            return self._createNoPrbFunctional(ctx)
        prbType = ctx.getEntityType()
        prbType in _SUPPORTED_INTRO and ctx.removeFlags(FUNCTIONAL_FLAG.PREBATTLE_BITMASK)
        ctx.addFlags(FUNCTIONAL_FLAG.PREBATTLE_INTRO)
        clazz = _SUPPORTED_INTRO[prbType]
        if not inspect.isclass(clazz):
            raise AssertionError('Class is not found, checks settings')
            created = clazz()
        else:
            created = self._createNoPrbFunctional(ctx)
        return created

    @staticmethod
    def _createNoPrbFunctional(ctx):
        if ctx.hasFlags(FUNCTIONAL_FLAG.LEAVE_ENTITY) and ctx.hasFlags(FUNCTIONAL_FLAG.PREBATTLE_INTRO):
            return
        else:
            if not ctx.hasFlags(FUNCTIONAL_FLAG.NO_PREBATTLE):
                ctx.removeFlags(FUNCTIONAL_FLAG.PREBATTLE_BITMASK)
                ctx.addFlags(FUNCTIONAL_FLAG.NO_PREBATTLE)
                created = default.NoPrbFunctional()
            else:
                created = None
            return created
