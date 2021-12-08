# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/album/album_buy_collection_item_dialog_builder.py
from gui.impl import backport
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.lobby.new_year.dialogs.album.album_buy_dialog_base import AlbumBuyDialogBase
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders

class AlbumCollectionItemDialogBuilder(AlbumBuyDialogBase):
    __slots__ = ('__toy',)

    def __init__(self, toy):
        super(AlbumCollectionItemDialogBuilder, self).__init__()
        self.__toy = toy

    def _setTitle(self, template):
        if self.__toy.getName():
            title = backport.text(R.strings.ny.dialogs.buyCollectionItem.title(), toyName=backport.text(self.__toy.getName()))
            template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(title))

    def _setPrice(self, template, price=None):
        super(AlbumCollectionItemDialogBuilder, self)._setPrice(template, self.__toy.getShards())
