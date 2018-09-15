# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_collections_groups.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.NYCollectionsGroupsMeta import NYCollectionsGroupsMeta
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.locale.NY import NY
from items.new_year_types import NATIONAL_SETTINGS
from new_year.new_year_sounds import NYSoundEvents
_DEF_DATA = {'title': NY.COLLECTIONSGROUP_TITLE}

class NYCollectionsGroups(NYHelperView, NYCollectionsGroupsMeta):

    def __init__(self, ctx=None):
        super(NYCollectionsGroups, self).__init__()

    def onWindowClose(self):
        self.__doClose()

    def onClose(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_COLLECTION_GROUPS)
        self._switchToNYMain(previewAlias=VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP)

    def onAlbumClick(self, settingsId):
        assert settingsId in NATIONAL_SETTINGS
        self._switchToCollection(previewAlias=VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP, settings=settingsId)

    def _populate(self):
        super(NYCollectionsGroups, self)._populate()
        NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_COLLECTION_GROUPS)
        NYSoundEvents.setState(NYSoundEvents.STATE_ON_COLLECTION_GROUPS)
        data = _DEF_DATA
        self.as_setDataS(data)

    def __doClose(self):
        self.destroy()
