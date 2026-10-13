# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/shell_alt_key_data.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.advanced.data.advanced_constants import SHELL_MOVIES, MODERN_POSTFIX, STUN_POSTFIX
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.shared.gui_items.vehicle_modules import Shell

class ShellKeyData(DefaultAltKeyData):

    @classmethod
    def _getMechanicKeys(cls, shell):
        return (getPreparedShellItemType(shell),)

    @classmethod
    def _getSwfName(cls, shell, mechanicName):
        return SHELL_MOVIES.get(mechanicName, None)

    @staticmethod
    def _getHeader(shell, mechanicName):
        return backport.text(R.strings.tooltips.advanced.header.shellType.dyn(shell.kind, default=R.invalid)())


def getPreparedShellItemType(shell):
    shellKind = shell.kind
    if shell.isModernMechanics:
        shellKind += MODERN_POSTFIX
    elif shell.hasStun:
        shellKind += STUN_POSTFIX
    return shellKind
