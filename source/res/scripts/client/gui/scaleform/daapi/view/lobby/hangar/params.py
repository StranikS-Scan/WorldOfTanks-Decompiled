# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Params.py
from constants import QUEUE_TYPE
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.ParamsMeta import ParamsMeta
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREQUEUE_SETTING_NAME
from gui.shared import events
from gui.server_events import g_eventsCache
from gui.shared.utils import ItemsParameters
from gui.shared.event_bus import EVENT_BUS_SCOPE

class Params(ParamsMeta, GlobalListener):

    def __init__(self):
        super(Params, self).__init__()

    def _populate(self):
        super(Params, self)._populate()
        self.addListener(events.LobbySimpleEvent.HIGHLIGHT_TANK_PARAMS, self.__onHighlightParams, EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()
        self.update()

    def _dispose(self):
        self.stopGlobalListening()
        self.removeListener(events.LobbySimpleEvent.HIGHLIGHT_TANK_PARAMS, self.__onHighlightParams, EVENT_BUS_SCOPE.LOBBY)
        super(Params, self)._dispose()

    def update(self):
        self._update(self._getHistoricalBattleData())

    def _update(self, vDescr = None):
        data = []
        if g_currentVehicle.isPresent():
            if vDescr is None:
                vDescr = g_currentVehicle.item.descriptor
            params = ItemsParameters.g_instance.getParameters(vDescr)
            if params is not None:
                for p in params:
                    attr = p[0]
                    textHtml = makeHtmlString('html_templates:lobby/tank_params', attr)
                    data.append({'text': textHtml,
                     'param': p[1],
                     'selected': False})

        outcome = {'params': data}
        self.as_setValuesS(outcome)
        return

    def __onHighlightParams(self, event):
        self.as_highlightParamsS(event.ctx.get('type', 'empty'))

    def clearHistorical(self):
        self._update()

    def _getHistoricalBattleData(self):
        vDescr = None
        if self.preQueueFunctional.getQueueType() == QUEUE_TYPE.HISTORICAL:
            battleId = self.preQueueFunctional.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
            battle = g_eventsCache.getHistoricalBattles().get(battleId)
            if battle is not None:
                vDescr = battle.getVehicleModifiedDescr(g_currentVehicle.item)
        return vDescr
