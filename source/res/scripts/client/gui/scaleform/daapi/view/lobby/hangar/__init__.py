# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/__init__.py
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
from gui.Scaleform.daapi.view.lobby.hangar.Params import Params
from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
from gui.Scaleform.daapi.view.lobby.hangar.TankCarousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__all__ = ['Hangar',
 'AmmunitionPanel',
 'Crew',
 'Params',
 'ResearchPanel',
 'TankCarousel',
 'TechnicalMaintenance',
 'TmenXpPanel']
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CREW, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'CrewContextMenuHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.VEHICLE, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'VehicleContextMenuHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.TECHNICAL_MAINTENANCE, 'gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers', 'TechnicalMaintenanceCMHandler')
