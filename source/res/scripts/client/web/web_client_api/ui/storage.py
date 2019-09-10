# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/storage.py
from gui.Scaleform.daapi.view.lobby.storage import getSectionsList
from gui.shared import event_dispatcher as shared_events
from web.web_client_api import w2c, W2CSchema, Field, WebCommandException

def _validateSection(value, _):
    if value in (section['id'] for section in getSectionsList()):
        return True
    raise WebCommandException(value)


class _OpenStorageSchema(W2CSchema):
    section_id = Field(required=False, type=basestring, validator=_validateSection)


class StorageWebApiMixin(object):

    @w2c(_OpenStorageSchema, 'storage')
    def openStorage(self, cmd):
        sectionId = cmd.section_id
        if sectionId is not None:
            shared_events.showStorage(sectionId)
        else:
            shared_events.showStorage()
        return
