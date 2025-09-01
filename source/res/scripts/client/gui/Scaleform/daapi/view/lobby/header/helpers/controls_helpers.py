# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/helpers/controls_helpers.py
from __future__ import absolute_import
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getEventTooltipData, getMapboxFightBtnTooltipData, getMapsTrainingTooltipData, getRandomTooltipData, getRankedFightBtnTooltipData
from gui.impl.gen import R
from gui.impl.lobby.page.lobby_footer import LobbyFooter
from gui.impl.lobby.page.lobby_header import LobbyHeader
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult
    from gui.impl.pub.view_component import ViewComponent

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

    @classmethod
    def getHeaderType(cls):
        raise NotImplementedError

    @classmethod
    def getFooterType(cls):
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
    def getHeaderType(cls):
        return LobbyHeader

    @classmethod
    def getFooterType(cls):
        return LobbyFooter

    @classmethod
    def _getCommonFightTooltipData(cls, _, __):
        return ('', False)

    @classmethod
    def _getDisabledFightTooltipData(cls, prbValidation, isInSquad):
        return (getRandomTooltipData(prbValidation, isInSquad), False)

    @classmethod
    def _getInSquadTooltipData(cls, _):
        tooltip = R.strings.platoon.headerButton.tooltips.dyn(cls._IN_SQUAD_TOOLTIP_KEY)
        return (tooltip.header(), tooltip.body(), {})

    @classmethod
    def _getOutSquadTooltipData(cls, prbValidation):
        tooltip = R.strings.platoon.headerButton.tooltips.dyn(cls._OUT_SQUAD_TOOLTIP_KEY)
        return (tooltip.header(), tooltip.body(), {})


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
