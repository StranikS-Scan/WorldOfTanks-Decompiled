# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Params.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.ParamsMeta import ParamsMeta
from CurrentVehicle import g_currentVehicle
from gui.shared import events
from gui.shared.utils import ItemsParameters
from gui.shared.event_bus import EVENT_BUS_SCOPE

class Params(ParamsMeta):

    def __init__(self):
        super(Params, self).__init__()

    def _populate(self):
        super(Params, self)._populate()
        self.addListener(events.LobbySimpleEvent.HIGHLIGHT_TANK_PARAMS, self.__onHighlightParams, EVENT_BUS_SCOPE.LOBBY)
        self.update()

    def _dispose(self):
        self.removeListener(events.LobbySimpleEvent.HIGHLIGHT_TANK_PARAMS, self.__onHighlightParams, EVENT_BUS_SCOPE.LOBBY)
        super(Params, self)._dispose()

    def update(self):
        self._update()

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
