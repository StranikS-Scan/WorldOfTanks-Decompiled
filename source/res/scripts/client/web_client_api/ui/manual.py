# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/manual.py
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.doc_loaders.manual_xml_data_reader import getChaptersIndexesList
from gui.shared import event_dispatcher as shared_events
from web_client_api import W2CSchema, w2c, Field

def _chapterIndexValidator(key, _):
    settings = dependency.instance(ILobbyContext).getServerSettings()
    return key in getChaptersIndexesList(settings.isBootcampEnabled())


class _OpenManualWindowSchema(W2CSchema):
    chapter_index = Field(required=False, type=int, default=1, validator=_chapterIndexValidator)


class ManualPageWebApiMixin(object):

    @w2c(_OpenManualWindowSchema, 'manual')
    def openManualPage(self, cmd):
        shared_events.openManualPage(cmd.chapter_index)
