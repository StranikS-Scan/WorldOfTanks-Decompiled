# Embedded file name: scripts/client/gui/prb_control/factories/PrebattleFactory.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import prb_control
from gui.prb_control.context import prb_ctx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional import isStatefulFunctional
from gui.prb_control.functional.event_squad import EventSquadEntry, EventSquadFunctional
from gui.prb_control.functional.no_prebattle import NoPrbFunctional
from gui.prb_control.functional.not_supported import PrbNotSupportedFunctional
from gui.prb_control.functional.not_supported import NotSupportedEntry
from gui.prb_control.functional.default import PrbInitFunctional, PrbIntro, IntroPrbFunctional
from gui.prb_control.functional.training import TrainingEntry, TrainingFunctional
from gui.prb_control.functional.training import TrainingIntroFunctional
from gui.prb_control.functional.squad import SquadEntry, SquadFunctional
from gui.prb_control.functional.company import CompanyEntry, CompanyFunctional
from gui.prb_control.functional.company import CompanyIntroFunctional
from gui.prb_control.functional.battle_session import BattleSessionEntry
from gui.prb_control.functional.battle_session import BattleSessionListEntry
from gui.prb_control.functional.battle_session import BattleSessionFunctional
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE, FUNCTIONAL_EXIT
_PAN = PREBATTLE_ACTION_NAME
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.TRAINING: TrainingEntry,
 PREBATTLE_TYPE.SQUAD: SquadEntry,
 PREBATTLE_TYPE.EVENT_SQUAD: EventSquadEntry,
 PREBATTLE_TYPE.COMPANY: CompanyEntry,
 PREBATTLE_TYPE.TOURNAMENT: BattleSessionEntry,
 PREBATTLE_TYPE.CLAN: BattleSessionEntry}
_SUPPORTED_ENTRY_BY_ACTION = {_PAN.SQUAD: (SquadEntry, None),
 _PAN.EVENT_SQUAD: (EventSquadEntry, None),
 _PAN.TRAINING: (PrbIntro, (PREBATTLE_TYPE.TRAINING,)),
 _PAN.COMPANY: (PrbIntro, (PREBATTLE_TYPE.COMPANY,)),
 _PAN.SPEC_BATTLE: (BattleSessionListEntry, None)}
_SUPPORTED_FUNCTIONAL = {PREBATTLE_TYPE.TRAINING: TrainingFunctional,
 PREBATTLE_TYPE.SQUAD: SquadFunctional,
 PREBATTLE_TYPE.EVENT_SQUAD: EventSquadFunctional,
 PREBATTLE_TYPE.COMPANY: CompanyFunctional,
 PREBATTLE_TYPE.TOURNAMENT: BattleSessionFunctional,
 PREBATTLE_TYPE.CLAN: BattleSessionFunctional}
_SUPPORTED_INTRO = {PREBATTLE_TYPE.TRAINING: TrainingIntroFunctional,
 PREBATTLE_TYPE.COMPANY: CompanyIntroFunctional}

class PrebattleFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            prbEntry = PrbIntro(ctx.getPrbType())
        else:
            prbType = ctx.getPrbType()
            clazz = None
            if prbType in _SUPPORTED_ENTRY_BY_TYPE:
                clazz = _SUPPORTED_ENTRY_BY_TYPE[prbType]
            if clazz is None:
                LOG_ERROR('Given type of prebattle is not supported', prbType)
                clazz = NotSupportedEntry
            prbEntry = clazz()
        return prbEntry

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, dispatcher, ctx):
        clientPrb = prb_control.getClientPrebattle()
        if clientPrb is not None:
            if prb_control.isPrebattleSettingsReceived(prebattle=clientPrb):
                prbSettings = prb_control.getPrebattleSettings(prebattle=clientPrb)
                prbType = prb_control.getPrebattleType(settings=prbSettings)
                clazz = None
                if prbType in _SUPPORTED_FUNCTIONAL:
                    clazz = _SUPPORTED_FUNCTIONAL[prbType]
                if clazz:
                    prbFunctional = clazz(prbSettings)
                    for listener in dispatcher._globalListeners:
                        prbFunctional.addListener(listener())

                    createParams = ctx.getCreateParams()
                    if 'settings' in createParams and isStatefulFunctional(prbFunctional):
                        guiSettings = createParams['settings']
                        if guiSettings:
                            prbFunctional.applyStates(guiSettings.get(CTRL_ENTITY_TYPE.PREBATTLE))
                else:
                    LOG_ERROR('Prebattle with given type is not supported', prbType)
                    prbFunctional = PrbNotSupportedFunctional(prbSettings)
            else:
                prbFunctional = PrbInitFunctional()
        else:
            prbType = ctx.getPrbType()
            clazz = None
            if prbType in _SUPPORTED_INTRO:
                clazz = _SUPPORTED_INTRO[prbType]
            if clazz is None:
                clazz = NoPrbFunctional
            prbFunctional = clazz()
        return prbFunctional

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo()
        return PlayerDecorator(info.isCreator, info.isReady())

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREBATTLE, functional.getPrbType(), True, functional.hasLockedState(), isinstance(functional, IntroPrbFunctional))

    def createLeaveCtx(self, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        return prb_ctx.LeavePrbCtx(waitingID='prebattle/leave', funcExit=funcExit)
