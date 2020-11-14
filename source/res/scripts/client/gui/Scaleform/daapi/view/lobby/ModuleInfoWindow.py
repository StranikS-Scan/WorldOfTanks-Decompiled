# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ModuleInfoWindow.py
from gui.Scaleform.daapi.view.meta.ModuleInfoMeta import ModuleInfoMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import contexts
from gui.shared.tooltips.crew_book import CrewBookTooltipDataBlock
from gui.shared.tooltips.module import ModuleBlockTooltipData
from gui.shared.tooltips.shell import ShellBlockToolTipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class ModuleInfoWindow(ModuleInfoMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        super(ModuleInfoWindow, self).__init__()
        self.moduleCompactDescr = ctx.get('moduleCompactDescr')
        self.__vehicleDescr = ctx.get('vehicleDescr')

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(View, self)._populate()
        module = self.itemsCache.items.getItemByCD(self.moduleCompactDescr)
        itemTypeID = module.itemTypeID
        tooltipArgs = [self.moduleCompactDescr, self.__vehicleDescr]
        if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            dataProvider = ModuleBlockTooltipData(context=contexts.ModuleInfoContext())
        elif itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.BATTLE_ABILITY):
            dataProvider = ModuleBlockTooltipData(context=contexts.ModuleInfoContext())
        elif itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS:
            dataProvider = CrewBookTooltipDataBlock(context=contexts.CrewBookContext())
            tooltipArgs = [self.moduleCompactDescr]
        elif itemTypeID == GUI_ITEM_TYPE.SHELL:
            dataProvider = ShellBlockToolTipData(context=contexts.ModuleInfoContext())
        else:
            dataProvider = ModuleBlockTooltipData(context=contexts.ModuleInfoContext())
        data = dataProvider.buildToolTip(*tooltipArgs)
        if itemTypeID == GUI_ITEM_TYPE.SHELL:
            titleArr = [module.userType, module.longUserName, _ms(MENU.MODULEINFO_TITLE)]
        else:
            titleArr = [module.longUserName, _ms(MENU.MODULEINFO_TITLE)]
        data['windowTitle'] = ' '.join(titleArr)
        data['overlayType'] = module.getOverlayType()
        data['highlightType'] = module.getBigHighlightType()
        self._updateModuleInfo(data)

    def _updateModuleInfo(self, data):
        self.as_setModuleInfoS(data)
