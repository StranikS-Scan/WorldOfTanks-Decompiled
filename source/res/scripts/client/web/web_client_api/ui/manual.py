# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/manual.py
from helpers import dependency
from skeletons.gui.game_control import IManualController
from gui.doc_loaders.manual_xml_data_reader import getPagesIndexesList
from web.web_client_api import W2CSchema, w2c, Field

def _chapterIndexValidator(key, _):
    manualController = dependency.instance(IManualController)
    return key in getPagesIndexesList(manualController.pageFilter)


class _OpenManualWindowSchema(W2CSchema):
    ignore_chapter = Field(type=bool, default=False)
    chapter_index = Field(required=False, type=int, default=1, validator=_chapterIndexValidator)


class ManualPageWebApiMixin(object):
    manualController = dependency.descriptor(IManualController)

    @w2c(_OpenManualWindowSchema, 'manual')
    def openManualPage(self, cmd):
        if self.manualController.isActivated():
            self.manualController.show(None if cmd.ignore_chapter else cmd.chapter_index)
        return
