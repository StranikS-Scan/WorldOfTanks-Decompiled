# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/ingame_help/detailed_help_pages.py
from gui.impl.gen import R
from gui.impl import backport
from gui.ingame_help.detailed_help_pages import DetailedHelpPagesBuilder, addPage
from gui.shared.formatters import text_styles
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union, List, Any
    from gui.impl.gen_utils import DynAccessor, _InvalidDynAccessor
    Accessor = Union[DynAccessor, _InvalidDynAccessor]

class Comp7CorePagesBuilder(DetailedHelpPagesBuilder):
    _PAGE_NAMES = ('seasonModifiers', 'poi', 'roleSkills', 'rules')
    _CORE_RES_ROOT_TEXTS = R.strings.ingame_help.detailsHelp.comp7Core
    _CORE_RES_ROOT_IMAGES = R.images.comp7_core.gui.maps.icons.battleHelp
    _MODE_RES_ROOT_TEXTS = None
    _MODE_RES_ROOT_IMAGES = None

    @classmethod
    def priority(cls):
        raise NotImplementedError()

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        for pageName in cls._PAGE_NAMES:
            addPage(datailedList=pages, headerTitle=cls._getHeader(pageName), title=cls._getTitle(pageName), descr=cls._getDescr(pageName), keys=[], image=cls._getImage(pageName))

        return pages

    @classmethod
    def _getPageResBranchTexts(cls, pageName):
        corePageAccess = cls._CORE_RES_ROOT_TEXTS.dyn(pageName)
        return corePageAccess if corePageAccess.isValid() else cls._MODE_RES_ROOT_TEXTS.dyn(pageName)

    @classmethod
    def _getPageResBranchImages(cls, pageName):
        corePageAccess = cls._CORE_RES_ROOT_IMAGES.dyn(pageName)
        return corePageAccess if corePageAccess.isValid() else cls._MODE_RES_ROOT_IMAGES.dyn(pageName)

    @classmethod
    def _getHeader(cls, pageName):
        return backport.text(cls._MODE_RES_ROOT_TEXTS.mainTitle())

    @classmethod
    def _getTitle(cls, pageName):
        return backport.text(cls._getPageResBranchTexts(pageName).title())

    @classmethod
    def _getDescr(cls, pageName):
        return text_styles.mainBig(backport.text(cls._getPageResBranchTexts(pageName)()))

    @classmethod
    def _getImage(cls, pageName):
        return backport.image(cls._getPageResBranchImages(pageName)())
