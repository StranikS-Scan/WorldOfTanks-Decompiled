# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/album/album_buy_collection_dialog_builder.py
from gui.impl import backport
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.lobby.new_year.dialogs.album.album_buy_dialog_base import AlbumBuyDialogBase
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from new_year.collection_presenters import getCollectionCost
from items.new_year import getCollectionByIntID

class AlbumCollectionDialogBuilder(AlbumBuyDialogBase):
    __slots__ = ('__collectionID',)

    def __init__(self, collectionID):
        super(AlbumCollectionDialogBuilder, self).__init__()
        self.__collectionID = collectionID

    def _setTitle(self, template):
        _, collectionName = getCollectionByIntID(self.__collectionID)
        title = backport.text(R.strings.ny.dialogs.buyFullCollection.title(), settingName=backport.text(R.strings.ny.settings.dyn(collectionName)()))
        template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(title))

    def _setPrice(self, template, price=None):
        year, collectionName = getCollectionByIntID(self.__collectionID)
        super(AlbumCollectionDialogBuilder, self)._setPrice(template, getCollectionCost(year, collectionName))
