# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_sack_rare_loot.py
from ny_notification import NyNotification
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_sack_rare_loot_model import NySackRareLootModel
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class NySackRareLoot(NyNotification):
    __slots__ = ('__styleItem',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, resId, *args, **kwargs):
        model = NySackRareLootModel()
        self.__styleItem = None
        super(NySackRareLoot, self).__init__(resId, model, *args, **kwargs)
        return

    @property
    def viewModel(self):
        return super(NySackRareLoot, self).getViewModel()

    def _getEvents(self):
        events = super(NySackRareLoot, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _canNavigate(self):
        return super(NySackRareLoot, self)._canNavigate() and self._canShowStyle()

    def _update(self):
        self.__styleItem = self.__getStyleItem()
        with self.viewModel.transaction() as model:
            model.setIsButtonDisabled(not self._canNavigate())
            model.setIsPopUp(self._isPopUp)
            model.setUserName(self.__styleItem.userName)
            model.setItemType(self.__styleItem.itemTypeName)

    def _finalize(self):
        self.__styleItem = None
        super(NySackRareLoot, self)._finalize()
        return

    def __onClick(self):
        self._showStylePreview(self.__styleItem)

    def __getStyleItem(self):
        itemType = self.linkageData.custType
        itemTypeID = self.__getItemTypeID(itemType)
        item = self.__c11n.getItemByID(itemTypeID, self.linkageData.id)
        style = self.__itemsCache.items.getItemByCD(item.intCD)
        return style

    @staticmethod
    def __getItemTypeID(itemTypeName):
        if itemTypeName == 'projection_decal':
            itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
        elif itemTypeName == 'personal_number':
            itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
        else:
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
        return itemTypeID
