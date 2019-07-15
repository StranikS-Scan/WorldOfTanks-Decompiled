# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/frontline_vehicle_preview_20.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getEpicGamePlayerPrestigePoints
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import getDataOneVehicle, addBuiltInEquipment
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.shared.formatters import text_styles, icons
from gui import makeHtmlString
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from web_client_api.common import ItemPackEntry, ItemPackType
from gui.shared.utils.functions import makeTooltip, makeString as _ms
from gui.impl import backport
from gui.impl.gen import R

class FrontLineVehiclePreview20(VehiclePreview20):
    __frontLineCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __VEH_LEVEL_WITH_PRESTIGE_RESTRICTION = 9

    def __init__(self, ctx=None):
        super(FrontLineVehiclePreview20, self).__init__(ctx)
        self._heroInteractive = False
        self.__itemsPack = [ItemPackEntry(type=ItemPackType.CREW_100, count=1, groupID=1), ItemPackEntry(type=ItemPackType.CUSTOM_SLOT, count=1, groupID=1)]
        addBuiltInEquipment(self.__itemsPack, self.itemsCache, self._vehicleCD)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(FrontLineVehiclePreview20, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.FRONTLINE_BUYING_PANEL_PY_ALIAS:
            itemsData = getDataOneVehicle(itemsPack=self.__itemsPack, vehicle=g_currentPreviewVehicle.item, vehicleGroupId=1)
            itemsData.insert(0, self.__getDefaultCrewItemPackEntry())
            viewPy.setData(itemsPack=self.__itemsPack, panelDataVO=self._getBuyingPanelData(), packedItemsVO={'items': itemsData})
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            viewPy.setVehicleCrews((ItemPackEntry(id=g_currentPreviewVehicle.item.intCD, groupID=1),), (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),))

    def _getBuyingPanelData(self):
        vehPrice = self.__frontLineCtrl.getRewardVehicles().get(self._vehicleCD, 0)
        vehLvl = g_currentPreviewVehicle.item.level
        prestigeLvl, _, _ = self.__frontLineCtrl.getPlayerLevelInfo()
        gotMaxPrestige = prestigeLvl == self.__frontLineCtrl.getMaxPlayerPrestigeLevel()
        storedPoints = getEpicGamePlayerPrestigePoints()
        if storedPoints:
            templateKey = 'vehiclePreviewEpicBattleTitle'
        else:
            templateKey = 'vehiclePreviewEpicBattleZeroBalanceTitle'
        title = makeHtmlString(path='html_templates:lobby/vehicle_preview', key=templateKey, ctx={'storedPoints': storedPoints})
        haveEnoughPoints = storedPoints >= vehPrice
        buyButtonTooltip = ''
        key = ''
        points = vehPrice
        if vehLvl < self.__VEH_LEVEL_WITH_PRESTIGE_RESTRICTION:
            if not haveEnoughPoints:
                key = 'notEnoughPrestigePoints'
        elif not haveEnoughPoints and not gotMaxPrestige:
            key = 'notEnoughPrestigeLevelAndPoints'
            points = vehPrice
        elif not haveEnoughPoints:
            key = 'notEnoughPrestigePoints'
        elif not gotMaxPrestige:
            key = 'notEnoughPrestigeLevel'
        if key:
            buyButtonTooltip = makeTooltip(None, _ms(TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), points=points))
        return {'title': title,
         'price': text_styles.concatStylesToSingleLine(text_styles.superPromoTitleEm(vehPrice), icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.epicBattles.prestigePoints.c_24x24()), width=24, height=24, vSpace=-3, hSpace=3)),
         'buyButtonEnabled': haveEnoughPoints and not buyButtonTooltip,
         'buyButtonLabel': backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buy()),
         'buyButtonTooltip': buyButtonTooltip}

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.FRONTLINE_BUYING_PANEL_LINKAGE)

    def _processBackClick(self, ctx=None):
        self.__frontLineCtrl.openURL(self._backAlias)

    def _getBackBtnLabel(self):
        return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.frontline())

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
