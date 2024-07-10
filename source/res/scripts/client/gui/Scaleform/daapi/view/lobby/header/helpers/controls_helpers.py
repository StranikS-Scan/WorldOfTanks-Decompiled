# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import TOOLTIP_TYPES
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getComp7FightBtnTooltipData, getEventTooltipData, getMapboxFightBtnTooltipData, getMapsTrainingTooltipData, getRandomTooltipData, getRankedFightBtnTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult

class ILobbyHeaderControlsHelper(object):
    __slots__ = ()

    @classmethod
    def isEventSquadEnable(cls):
        return False

    @classmethod
    def getFightControlTooltipData(cls, prbValidation, isInSquad, isFightBtnDisabled, isNavigationEnabled):
        raise NotImplementedError

    @classmethod
    def getSquadControlTooltipData(cls, prbValidation, isInSquad):
        raise NotImplementedError


class DefaultLobbyHeaderHelper(ILobbyHeaderControlsHelper):
    __slots__ = ()
    _IN_SQUAD_TOOLTIP_KEY = 'inSquad'
    _OUT_SQUAD_TOOLTIP_KEY = 'squad'

    @classmethod
    def getSquadControlTooltipData(cls, prbValidation, isInSquad):
        tooltipBuilder = cls._getInSquadTooltipData if isInSquad else cls._getOutSquadTooltipData
        return tooltipBuilder(prbValidation)

    @classmethod
    def getFightControlTooltipData(cls, prbValidation, isInSquad, isFightBtnDisabled, isNavigationEnabled):
        isDisabledBulder = isFightBtnDisabled and isNavigationEnabled
        tooltipBuilder = cls._getDisabledFightTooltipData if isDisabledBulder else cls._getCommonFightTooltipData
        return tooltipBuilder(prbValidation, isInSquad)

    @classmethod
    def _getCommonFightTooltipData(cls, _, __):
        return ('', False)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getRandomTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getInSquadTooltipData(cls, _):
        header = backport.text(R.strings.platoon.headerButton.tooltips.dyn(cls._IN_SQUAD_TOOLTIP_KEY).header())
        body = backport.text(R.strings.platoon.headerButton.tooltips.dyn(cls._IN_SQUAD_TOOLTIP_KEY).body())
        return (makeTooltip(header, body), TOOLTIP_TYPES.COMPLEX)

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        header = backport.text(R.strings.platoon.headerButton.tooltips.dyn(cls._OUT_SQUAD_TOOLTIP_KEY).header())
        body = backport.text(R.strings.platoon.headerButton.tooltips.dyn(cls._OUT_SQUAD_TOOLTIP_KEY).body())
        return (makeTooltip(header, body), TOOLTIP_TYPES.COMPLEX)


class RankedLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    _IN_SQUAD_TOOLTIP_KEY = 'rankedSquad'
    _OUT_SQUAD_TOOLTIP_KEY = 'rankedSquad'

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getRankedFightBtnTooltipData(prbValidation), False)


class MapboxLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    _IN_SQUAD_TOOLTIP_KEY = 'inMapboxSquad'
    _OUT_SQUAD_TOOLTIP_KEY = 'mapboxSquad'

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getMapboxFightBtnTooltipData(prbValidation, isInSquad), False)


class MapsTrainingLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getMapsTrainingTooltipData(), False)


class Comp7LobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getComp7FightBtnTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        resRoot = R.strings.platoon.headerButton.tooltips.comp7Squad
        if prbValidation.restriction == PRE_QUEUE_RESTRICTION.BAN_IS_SET:
            resRoot = R.strings.menu.headerButtons.fightBtn.tooltip.comp7BanIsSet
        if not cls.__comp7Controller.isQualificationSquadAllowed():
            resRoot = R.strings.platoon.headerButton.tooltips.comp7QualificationSquad
        return (makeTooltip(backport.text(resRoot.header()), backport.text(resRoot.body())), TOOLTIP_TYPES.COMPLEX)


class EventLobbyHeaderHelper(DefaultLobbyHeaderHelper):
    __slots__ = ('__bonusType', '__bonusCapsOverrides')
    _OUT_SQUAD_TOOLTIP_KEY = 'eventSquad'

    def __init__(self, bonusType, bonusCapsOverrides):
        self.__bonusType = bonusType
        self.__bonusCapsOverrides = bonusCapsOverrides

    def isEventSquadEnable(self):
        return BONUS_CAPS.checkAny(self.__bonusType, BONUS_CAPS.SQUADS, specificOverrides=self.__bonusCapsOverrides)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getEventTooltipData(), False)
