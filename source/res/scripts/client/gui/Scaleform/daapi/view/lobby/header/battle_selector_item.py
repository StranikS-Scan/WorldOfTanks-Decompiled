# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_item.py
from __future__ import absolute_import
from builtins import object
from functools import total_ordering
import logging
from adisp import adisp_process
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.dispatcher import g_prbLoader
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from constants import PREBATTLE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
_logger = logging.getLogger(__name__)
_R_HEADER_BUTTONS = R.strings.menu.headerButtons
_R_ICONS = R.images.gui.maps.icons

@total_ordering
class SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_selectorType', '_isVisible', '_isExtra', '_isSelected', '_isNew', '_isDisabled', '_isLocked')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, label, data, order, selectorType=None, isVisible=True, isExtra=False):
        super(SelectorItem, self).__init__()
        self._label = label
        self._data = data
        self._order = order
        self._isSelected = False
        self._isNew = False
        self._isLocked = False
        self._isDisabled = True
        self._isVisible = isVisible
        self._isExtra = isExtra
        self._selectorType = selectorType

    def __hash__(self):
        return hash(self._order)

    def __eq__(self, other):
        return self._order == other.getOrder()

    def __lt__(self, other):
        return self._order < other.getOrder()

    def getLabel(self):
        return self._label

    def getData(self):
        return self._data

    def isSelected(self):
        return self._isSelected

    def getSelectorType(self):
        return self._selectorType

    def isDisabled(self):
        return self._isDisabled

    def isVisible(self):
        return self._isVisible

    def isExtra(self):
        return self._isExtra

    def getSmallIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.dyn(self._data)())

    def getLargerIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_64x64.dyn(self._data)())

    def getSpecialBGIcon(self):
        pass

    def getFightButtonLabel(self, state, playerInfo):
        label = _R_HEADER_BUTTONS.battle
        if not playerInfo.isCreator and state.isReadyActionSupported():
            label = _R_HEADER_BUTTONS.notReady if playerInfo.isReady else _R_HEADER_BUTTONS.ready
        return backport.text(label())

    def isLocked(self):
        return self._isLocked

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return any((state.isInUnit(prbType) for prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES))

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False
            self._isVisible = False

    def isSelectorBtnEnabled(self):
        return self._isLocked or not self._isDisabled

    def getVO(self):
        return {'label': self.getFormattedLabel(),
         'data': self._data,
         'disabled': self._isDisabled,
         'icon': self.getLargerIcon(),
         'active': self._isSelected,
         'isNew': self.isShowNewIndicator(),
         'specialBgIcon': self.getSpecialBGIcon()}

    def isShowNewIndicator(self):
        return self._isNew

    def getFormattedLabel(self):
        return text_styles.middleTitle(self._label)

    def getOrder(self):
        return self._order

    def update(self, state):
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        if not self.isLocked():
            self._update(state)
        return

    def select(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doSelect(dispatcher)
        else:
            _logger.error('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        raise NotImplementedError

    @adisp_process
    def _doSelect(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(self.getData()))
