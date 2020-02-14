# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_vehicle_preview_20.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import getDataOneVehicle, addBuiltInEquipment
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController, IEventProgressionController
from web.web_client_api.common import ItemPackEntry, ItemPackType
from gui.shared.utils.functions import makeTooltip
from gui.impl import backport
from gui.impl.gen import R

class EventProgressionVehiclePreview20(VehiclePreview20):
    __eventProgressionController = dependency.descriptor(IEventProgressionController)
    __epicMetaGameController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx=None):
        super(EventProgressionVehiclePreview20, self).__init__(ctx)
        self._heroInteractive = False
        self.__itemsPack = [ItemPackEntry(type=ItemPackType.CREW_100, count=1, groupID=1), ItemPackEntry(type=ItemPackType.CUSTOM_SLOT, count=1, groupID=1)]
        addBuiltInEquipment(self.__itemsPack, self.itemsCache, self._vehicleCD)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventProgressionVehiclePreview20, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.EVENT_PROGRESSION_BUYING_PANEL_PY_ALIAS:
            itemsData = getDataOneVehicle(itemsPack=self.__itemsPack, vehicle=g_currentPreviewVehicle.item, vehicleGroupId=1)
            itemsData.insert(0, self.__getDefaultCrewItemPackEntry())
            viewPy.setData(itemsPack=self.__itemsPack, panelDataVO=self._getBuyingPanelData(), packedItemsVO={'items': itemsData})
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            viewPy.setVehicleCrews((ItemPackEntry(id=g_currentPreviewVehicle.item.intCD, groupID=1),), (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),))

    def _getBuyingPanelData(self):
        vehiclePrice = self.__eventProgressionController.getRewardVehiclePrice(g_currentPreviewVehicle.item.intCD)
        storedPoints = self.__eventProgressionController.actualRewardPoints
        haveEnoughPoints = 0 < storedPoints >= vehiclePrice
        if not haveEnoughPoints:
            resID = R.strings.tooltips.vehiclePreview.buyButton.notEnoughPrestigePoints
            buyButtonTooltip = makeTooltip(body=backport.text(resID.header(), points=vehiclePrice))
        else:
            buyButtonTooltip = ''
        formatMoney = text_styles.superPromoTitleEm if storedPoints > 0 else text_styles.superPromoTitleErr
        formatPrice = text_styles.superPromoTitleEm if haveEnoughPoints else text_styles.superPromoTitleErr
        tokensIcon = icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.epicBattles.rewardPoints.c_32x32()), width=32, height=32, vSpace=-6, hSpace=3)
        return {'title': text_styles.superPromoTitle(backport.text(R.strings.event_progression.vehicle_preview.title())),
         'money': text_styles.concatStylesToSingleLine(formatMoney(str(storedPoints)), tokensIcon),
         'price': text_styles.concatStylesToSingleLine(formatPrice(str(vehiclePrice)), tokensIcon),
         'buyButtonEnabled': haveEnoughPoints and not buyButtonTooltip,
         'buyButtonLabel': backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buy()),
         'buyButtonTooltip': buyButtonTooltip}

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.EVENT_PROGRESSION_BUYING_PANEL_LINKAGE)

    def _processBackClick(self, ctx=None):
        self.__eventProgressionController.openURL(self._backAlias)

    def _getBackBtnLabel(self):
        pass

    @classmethod
    def __getDefaultCrewItemPackEntry(cls):
        return {'isEnabled': True,
         'topTitle': '',
         'topTitleSmall': '',
         'items': [{'count': '100%',
                    'hasCompensation': False,
                    'icon': backport.image(R.images.gui.maps.shop.rewards.c_48x48.prizeCrew()),
                    'iconAlt': backport.image(R.images.gui.maps.icons.artefact.notFound()),
                    'id': 'None',
                    'overlayType': '',
                    'rawData': None,
                    'slotIndex': 0,
                    'type': ItemPackType.CREW_100}]}
