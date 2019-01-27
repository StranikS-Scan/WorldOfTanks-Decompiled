# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/frontline_vehicle_preview_20.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui import makeHtmlString
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from web_client_api.common import ItemPackEntry, ItemPackType

class FrontLineVehiclePreview20(VehiclePreview20):
    _frontLineCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx=None):
        super(FrontLineVehiclePreview20, self).__init__(ctx)
        self._heroInteractive = False

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(FrontLineVehiclePreview20, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.EPIC_BATTLE_PANEL_PY_ALIAS:
            price = self._frontLineCtrl.getRewardVehicles().get(self._vehicleCD, 0)
            title = makeHtmlString('html_templates:lobby/vehicle_preview', 'vehiclePreviewEpicBattleTitle', {'price': price})
            description = _ms(EPIC_BATTLE.VEHICLE_PREVIEW_DESCRIPTION)
            viewPy.setData(title, description)
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            viewPy.setVehicleCrews((ItemPackEntry(id=g_currentPreviewVehicle.item.intCD, groupID=1),), (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),))

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.EPIC_BATTLE_PANEL_LINKAGE)

    def _processBackClick(self, ctx=None):
        self._frontLineCtrl.openURL(self._backAlias)

    def _getBackBtnLabel(self):
        return VEHICLE_PREVIEW.getBackBtnLabel('frontline')
