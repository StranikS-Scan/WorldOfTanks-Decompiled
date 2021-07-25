# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialog_template_utils.py
import typing
import constants
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.impl import backport
from gui.impl.gen_utils import DynAccessor
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from typing import Union

def toString(value):
    if isinstance(value, DynAccessor):
        return backport.text(value())
    return backport.text(value) if isinstance(value, (long, int)) else value


def checkDialogTemplateIsOpened(uniqueID):
    from gui.impl.dialogs.dialog_template import DialogTemplateView
    guiLoader = dependency.instance(IGuiLoader)

    def predicate(view):
        return isinstance(view, DialogTemplateView) and view.uniqueID == uniqueID

    return len(guiLoader.windowsManager.findViews(predicate)) != 0


def getCurrencyTooltipAlias(currency):
    return currency + 'StatsFullScreen' if constants.IS_SINGAPORE and currency in CURRENCIES_CONSTANTS.SINGAPORE_ALTERNATIVE_CURRENCIES_SET else currency + 'InfoFullScreen'
