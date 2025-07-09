# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.system_factory import registerBannerEntryPointValidator
from mt_birthday.gui.Scaleform.daapi.view.lobby.hangar.birthday_entry_point import isBirthdayAvailable
registerBannerEntryPointValidator(HANGAR_ALIASES.BIRTHDAY_BANNER_ENTRY_POINT, isBirthdayAvailable)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from mt_birthday.gui.Scaleform.daapi.view.lobby.hangar.birthday_entry_point import BirthdayBannerEntryPoint
    return (ComponentSettings(HANGAR_ALIASES.BIRTHDAY_BANNER_ENTRY_POINT, BirthdayBannerEntryPoint, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
