# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/summer_sale_confirm_view.py
import logging
from adisp import adisp_process
from gui.game_control.summer_sale_controller import ProductsStates
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.footer.simple_text_footer import SimpleTextFooter
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_set_view_model import IconPositionLogicEnum
from gui.shared.gui_items.Vehicle import getTypeBigIconResource, getNationLessName, getIconResourceName
from helpers import dependency, int2roman
from skeletons.gui.game_control import ISummerSaleController
from tutorial.control.game_vars import getVehicleByIntCD
_logger = logging.getLogger(__name__)

class SummerSaleConfirmView(DialogTemplateView):
    __slots__ = ('_vehicle', '__products', '__productCode')
    __summerSale = dependency.descriptor(ISummerSaleController)

    def __init__(self, productCode, *args, **kwargs):
        self.__productCode = productCode
        self.__tryGetVehicle(productCode)
        self.__getProducts()
        super(SummerSaleConfirmView, self).__init__(*args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        imageContent = ImageSubstitution(R.images.gui.maps.icons.event.summerSale.main.alertIcon(), 'warning', 4, 0, 0, 0)
        self.setSubView(DefaultDialogPlaceHolders.ICON, self.__buildIcon())
        self.setSubView(DefaultDialogPlaceHolders.TITLE, self.__buildTitle())
        self.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(str(backport.text(R.strings.event.summerSales.confirm.content.placeHolder(), warning='%(warning)s')), imageSubstitutions=[imageContent]))
        self.setSubView(DefaultDialogPlaceHolders.FOOTER, self.__buildFooter())
        self.addButton(ConfirmButton(R.strings.dialogs.rentConfirmation.submit()))
        self.addButton(CancelButton(R.strings.dialogs.rentConfirmation.cancel()))
        self.setBackgroundDimmerAlpha(0.8)
        super(SummerSaleConfirmView, self)._onLoading(*args, **kwargs)

    def __tryGetVehicle(self, productCode):
        try:
            vehicleCD = int(productCode.split('_')[-1])
            self._vehicle = getVehicleByIntCD(vehicleCD)
        except ValueError:
            self._vehicle = None

        return

    def __buildIcon(self):
        if self._vehicle:
            imageRes = R.images.gui.maps.icons.event.summerSale.reward.vechicles.c_360x270.dyn(getIconResourceName(getNationLessName(self._vehicle.name)))()
            return IconSet(imageRes, backgroundResIDList=[R.images.gui.maps.icons.tankmen.skills.dialogs.bgGlow()], iconPositionLogic=IconPositionLogicEnum.MOVECONTENTBELOW.value)
        imageRes = R.images.gui.maps.icons.event.summerSale.reward.vechicles.c_360x270.reward_random_tank()
        return IconSet(imageRes, backgroundResIDList=[R.images.gui.maps.icons.tankmen.skills.dialogs.bgGlow()], iconPositionLogic=IconPositionLogicEnum.MOVECONTENTBELOW.value)

    def __buildTitle(self):
        if self._vehicle:
            imageTitel = ImageSubstitution(getTypeBigIconResource(self._vehicle.type, self._vehicle.isElite)(), 'icon', -11, -12, -13, -12)
            textTitle = str(backport.text(R.strings.event.summerSales.confirm.title.placeHolder(), tankLevel=int2roman(self._vehicle.level), icon='%(icon)s', tankName=self._vehicle.descriptor.type.shortUserString))
            return SimpleTextTitle(textTitle, imageSubstitutions=[imageTitel])
        return SimpleTextTitle(R.strings.event.summerSales.mainView.catalog.randomVehicle.label())

    @adisp_process
    def __getProducts(self):
        status, self.__products = yield self.__summerSale.fetchProducts()
        if status == ProductsStates.EMPTY or not self.__products:
            self.__products = {}
            _logger.error('No products available')

    def __buildFooter(self):
        price = self.__products.get(self.__productCode, {}).get('price', {}).get('amount', None)
        imageFooter = ImageSubstitution(R.images.gui.maps.icons.event.summerSale.main.icon_honey_24(), 'honeyCoin', 0, 0, 0, 0)
        return SimpleTextFooter(str(backport.text(R.strings.event.summerSales.confirm.footer.placeHolder(), honeyCoin='%(honeyCoin)s', price=int(price))), imageSubstitutions=[imageFooter])
