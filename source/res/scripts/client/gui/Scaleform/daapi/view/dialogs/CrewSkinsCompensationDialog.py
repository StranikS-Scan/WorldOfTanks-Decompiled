# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/CrewSkinsCompensationDialog.py
from gui.Scaleform.daapi.view.meta.CrewSkinsCompensationDialogMeta import CrewSkinsCompensationDialogMeta
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items.Tankman import getCrewSkinIconSmall, getCrewSkinNationPath, getCrewSkinRolePath
from helpers import i18n

class CrewSkinsCompensationDialog(CrewSkinsCompensationDialogMeta):

    def __init__(self, meta, handler):
        super(CrewSkinsCompensationDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self.__meta = meta

    def _populate(self):
        super(CrewSkinsCompensationDialog, self)._populate()
        itemPrice = self.__meta.getMessagePrice()
        if itemPrice is not None:
            pricesVO = getItemPricesVO(itemPrice)
            self.as_setMessagePriceS({'itemPrices': pricesVO,
             'actionPrice': None})
            self.as_setPriceLabelS(i18n.makeString(self.__meta.getCompensationMessage()))
        itemsList = self.__meta.getItems()
        items = [ self.__convertCrewSkinData(item) for item in itemsList ]
        self.as_setListS(items)
        return

    def _dispose(self):
        self.__meta = None
        super(CrewSkinsCompensationDialog, self)._dispose()
        return

    @staticmethod
    def __convertCrewSkinData(crewSkin):
        return {'id': crewSkin.getID(),
         'iconID': getCrewSkinIconSmall(crewSkin.getIconID()),
         'roleIconID': getCrewSkinRolePath(crewSkin.getRoleID()),
         'nationFlagIconID': getCrewSkinNationPath(crewSkin.getNation()),
         'rarity': crewSkin.getRarity(),
         'soundSetID': crewSkin.getSoundSetID()}
