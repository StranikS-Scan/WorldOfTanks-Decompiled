# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/backgrounds.py
import typing
from items import _xml
if typing.TYPE_CHECKING:
    import ResMgr

class Backgrounds(object):
    __slots__ = ('_page',)

    def __init__(self, xmlCtx, section):
        self._page = _xml.readString(xmlCtx, section, 'page')

    @property
    def page(self):
        return self._page
