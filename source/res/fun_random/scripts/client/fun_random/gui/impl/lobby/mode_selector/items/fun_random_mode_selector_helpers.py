# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/mode_selector/items/fun_random_mode_selector_helpers.py
import typing
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters.ranges import toRomanRangeString
from shared_utils import first
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode

class IModeSelectorHelper(object):
    __slots__ = ()

    def isDisabled(self):
        raise NotImplementedError

    def getConditionText(self, modeName):
        raise NotImplementedError

    def clear(self):
        pass


class _SingleModeSelectorHelper(IModeSelectorHelper, FunSubModesWatcher):
    __slots__ = ('__subMode',)

    def __init__(self, subMode):
        self.__subMode = subMode

    def isDisabled(self):
        isFrozen = self.__subMode.isBattlesPossible() and self.__subMode.isFrozen()
        self._funRandomCtrl.notifications.markSeenAsFrozen([self.__subMode.getSubModeID()] if isFrozen else [])
        return isFrozen

    def getConditionText(self, modeName):
        return backport.text(R.strings.mode_selector.mode.dyn(modeName).condition(), levels=toRomanRangeString(self.__subMode.getSettings().filtration.levels))

    def clear(self):
        self.__subMode = None
        return


class _MultiModesSelectorHelper(IModeSelectorHelper):
    __slots__ = ()

    def isDisabled(self):
        return False

    def getConditionText(self, modeName):
        pass


def createSelectorHelper(subModes):
    return _SingleModeSelectorHelper(first(subModes)) if len(subModes) == 1 else _MultiModesSelectorHelper()
