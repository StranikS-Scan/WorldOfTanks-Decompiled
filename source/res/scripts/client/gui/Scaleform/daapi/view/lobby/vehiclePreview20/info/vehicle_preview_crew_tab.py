# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_crew_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.VehiclePreviewCrewTabMeta import VehiclePreviewCrewTabMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles
from helpers import i18n
from web_client_api.common import ItemPackType, ItemPackTypeGroup

class VehiclePreviewCrewTab(VehiclePreviewCrewTabMeta):

    def __init__(self):
        super(VehiclePreviewCrewTab, self).__init__()
        self.__crewItems = []
        self.__vehicleItems = []

    def _populate(self):
        super(VehiclePreviewCrewTab, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        super(VehiclePreviewCrewTab, self)._dispose()

    def setActiveState(self, isActive):
        pass

    def setVehicleCrews(self, vehicleItems, crewItems):
        self.__vehicleItems = vehicleItems
        self.__crewItems = crewItems
        self._update()

    def update(self, *args):
        self._update()

    def _update(self):
        currentVehicle = g_currentPreviewVehicle.item
        if not currentVehicle:
            LOG_DEBUG('Current vehicle is None, avoid updating.')
            return
        else:
            crewData = []
            for _, tankman in currentVehicle.crew:
                role = tankman.descriptor.role
                crewData.append({'icon': RES_ICONS.getItemBonus42x42(role),
                 'name': text_styles.middleTitle(ITEM_TYPES.tankman_roles(role)),
                 'tooltip': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER,
                 'role': role})

            vehicleCrewComment = i18n.makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_NOCREW)
            if self.__vehicleItems and self.__crewItems:
                gID = None
                for item in self.__vehicleItems:
                    if item.id == currentVehicle.intCD:
                        gID = item.groupID
                        break

                try:
                    topCrewItem = sorted([ item for item in self.__crewItems if item.groupID == gID ], key=lambda item: ItemPackTypeGroup.CREW.index(item.type))[-1]
                except IndexError:
                    topCrewItem = None

                if topCrewItem is not None:
                    pctValue = {ItemPackType.CREW_50: 50,
                     ItemPackType.CREW_75: 75,
                     ItemPackType.CREW_100: 100}.get(topCrewItem.type)
                    if pctValue is not None:
                        vehicleCrewComment = i18n.makeString(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_HEADER_WITHCREW, pctValue)
            self.as_setDataS({'listDesc': text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_LISTDESC_TEXT),
             'vehicleCrewComment': text_styles.middleTitle(vehicleCrewComment),
             'crewList': crewData})
            return
