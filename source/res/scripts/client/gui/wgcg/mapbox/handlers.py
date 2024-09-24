# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/mapbox/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class MapboxRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.MAPBOX_PROGRESSION: self.__getMapboxProgression,
         WebRequestDataType.MAPBOX_SURVEY_COMPLETE: self.__completeSurvey,
         WebRequestDataType.MAPBOX_SURVEY_URL: self.__requestAuthorizedSurveyURL}
        return handlers

    def __getMapboxProgression(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('mapbox', 'get_mapbox_progression'))

    def __completeSurvey(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('mapbox', 'complete_survey'), ctx.getSurveyData())

    def __requestAuthorizedSurveyURL(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('mapbox', 'request_authorized_survey_url'), ctx.getMapURL())
