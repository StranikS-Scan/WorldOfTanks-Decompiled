# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/congrats/congrats_ctx.py
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getShopVehicleIconPath
from skeletons.gui.shared.congrats import ICongratsCtx

class CongratsCtx(ICongratsCtx):

    @property
    def background(self):
        return R.images.gui.maps.icons.store.shop_2_background_arsenal()

    @property
    def title(self):
        return R.strings.store.congratulationAnim.buyingLabel()

    @property
    def description(self):
        pass

    @property
    def image(self):
        return self.imageAlt

    @property
    def imageAlt(self):
        return getShopVehicleIconPath(STORE_CONSTANTS.ICON_SIZE_LARGE, 'empty_tank')

    @property
    def confirmLabel(self):
        return R.strings.store.congratulationAnim.confirmLabel()

    @property
    def backLabel(self):
        return R.invalid()

    def onConfirm(self):
        pass

    def onBack(self):
        pass


class GUIItemCongratsCtx(CongratsCtx):

    def __init__(self, item):
        self._item = item


class StyleCongratsCtx(GUIItemCongratsCtx):

    @property
    def description(self):
        return backport.text(R.strings.store.congratulationAnim.descriptionLabel.style(), name=self._item.userName)

    @property
    def image(self):
        size = STORE_CONSTANTS.ICON_SIZE_LARGE
        return RES_SHOP.getStyleIcon(size, self._item.id) if RES_SHOP.hasStyleIcon(size, self._item.id) else self._item.icon
