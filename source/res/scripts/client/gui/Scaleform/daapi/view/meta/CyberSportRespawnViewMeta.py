# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnViewMeta.py
from gui.Scaleform.framework.entities.View import View

class CyberSportRespawnViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def as_setMapBGS(self, imgsource):
        return self.flashObject.as_setMapBG(imgsource) if self._isDAAPIInited() else None

    def as_changeAutoSearchStateS(self, value):
        return self.flashObject.as_changeAutoSearchState(value) if self._isDAAPIInited() else None

    def as_hideAutoSearchS(self):
        return self.flashObject.as_hideAutoSearch() if self._isDAAPIInited() else None
