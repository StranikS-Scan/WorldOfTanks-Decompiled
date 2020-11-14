# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_vehicle_style_preview.py
import logging
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController
_logger = logging.getLogger(__name__)

class EventProgressionVehicleStylePreview(VehicleStylePreview):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.EVENT_PROGRESSION_STYLE_BUYING_PANEL_LINKAGE)
        super(EventProgressionVehicleStylePreview, self)._populate()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventProgressionVehicleStylePreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.EVENT_PROGRESSION_STYLE_BUYING_PANEL_PY_ALIAS:
            viewPy.setData(self._getBuyingPanelData(), style=self._style)

    def _getBuyingPanelData(self):
        stylePrice = self.__eventProgression.getRewardStylePrice(self._style.id)
        storedPoints = self.__eventProgression.actualRewardPoints
        haveEnoughPoints = 0 < storedPoints >= stylePrice
        if not haveEnoughPoints:
            resID = R.strings.tooltips.vehiclePreview.buyButton.notEnoughPrestigePoints
            buyButtonTooltip = makeTooltip(body=backport.text(resID.header(), points=stylePrice))
        else:
            buyButtonTooltip = ''
        formatMoney = text_styles.superPromoTitleEm if storedPoints > 0 else text_styles.superPromoTitleErr
        formatPrice = text_styles.superPromoTitleEm if haveEnoughPoints else text_styles.superPromoTitleErr
        tokensIcon = icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.epicBattles.rewardPoints.c_32x32()), width=32, height=32, vSpace=-6, hSpace=3)
        return {'title': text_styles.superPromoTitle(backport.text(R.strings.event_progression.vehicle_preview.style_title())),
         'money': text_styles.concatStylesToSingleLine(formatMoney(str(storedPoints)), tokensIcon),
         'price': text_styles.concatStylesToSingleLine(formatPrice(str(stylePrice)), tokensIcon),
         'priceTooltip': TOOLTIPS.VEHICLEPREVIEW_BUYINGPANEL_EVENTPROGRESSION_STYLE_PRICE,
         'buyButtonEnabled': haveEnoughPoints and not buyButtonTooltip,
         'buyButtonLabel': backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buy()),
         'buyButtonTooltip': buyButtonTooltip}
