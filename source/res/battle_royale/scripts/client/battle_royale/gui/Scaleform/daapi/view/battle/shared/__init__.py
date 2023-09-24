# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shared/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle import shared

def getContextMenuHandlers():
    return shared.getContextMenuHandlers()


def getViewSettings():
    from battle_royale.gui.Scaleform.daapi.view.battle.shared.br_ingame_menu import BRIngameMenu
    settingsList = list()
    for viewSetting in shared.getViewSettings():
        if viewSetting.alias == VIEW_ALIAS.INGAME_MENU:
            viewSetting = viewSetting._replace(clazz=BRIngameMenu)
        settingsList.append(viewSetting)

    return settingsList


def getBusinessHandlers():
    return shared.getBusinessHandlers()
