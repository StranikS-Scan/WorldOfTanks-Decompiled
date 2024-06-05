# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/dog_tag_composer.py
from enum import Enum
import logging
import typing
from dog_tags_common.components_config import componentConfigAdapter as componentConfig
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.gen_utils import DynAccessor
    from dog_tags_common.config.dog_tag_framework import ComponentDefinition
_logger = logging.getLogger(__name__)

class AssetSize(Enum):
    BIG = 'big'
    SMALL = 'small'
    MINI = 'mini'


ViewTypeToImageFolderMap = {ComponentViewType.ENGRAVING: 'engravings',
 ComponentViewType.BACKGROUND: 'backgrounds'}

def getResourceRoot(component):
    resourceString = component.resourceRoot
    _, tail = resourceString.split(':', 1)
    path = tail.split('/')
    res = R.strings.dogtags
    for src in path:
        res = res.num(src) if src.isdigit() else res.dyn(src)

    return res


LANGUAGE_CODE = backport.text(R.strings.settings.LANGUAGE_CODE())
SUPPORTED_LANGUAGES = ['de',
 'es',
 'fr',
 'hu',
 'it',
 'pl',
 'pt_br',
 'ru',
 'tr',
 'uk',
 'zh_cn',
 'cs']

def getLocalizePostfix():
    return '_{}'.format(LANGUAGE_CODE) if LANGUAGE_CODE in SUPPORTED_LANGUAGES else ''


class DogTagComposerClient(object):
    MAX_NAME_LENGTH = 12

    @staticmethod
    def getComponentImage(componentId, grade=0, localized=False):
        if grade < 0:
            _logger.error('Tried loading an image with incorrect grade: %d for component %d', grade, componentId)
            grade = 0
        return '{}_{}_{}{}'.format(componentConfig.getComponentById(componentId).viewType.value.lower(), componentId, grade, getLocalizePostfix() if localized else '')

    @staticmethod
    def getBottomPlateImage(backgroundId):
        return '' if componentConfig.getComponentById(backgroundId).purpose != ComponentPurpose.COUPLED else 'bottom_plate_{}'.format(backgroundId)

    @classmethod
    def getComponentImageFullPath(cls, size, componentId, grade=0):
        imageRes = R.images.gui.maps.icons.dogtags.dyn(size.value.lower()).dyn(ViewTypeToImageFolderMap[componentConfig.getComponentById(componentId).viewType]).dyn(cls.getComponentImage(componentId, grade))
        if not imageRes.exists():
            _logger.error('Missing image for dogtag component %d, grade %d, size %s', componentId, grade, size.value)
            return cls.getDefaultBackgroundImageFullPath(size)
        return backport.image(imageRes())

    @staticmethod
    def getDefaultBackgroundImageFullPath(size):
        return backport.image(R.images.gui.maps.icons.dogtags.dyn(size.value.lower()).backgrounds.background_66_0())

    @classmethod
    def getComponentTitle(cls, componentId):
        return backport.text(cls.getComponentTitleRes(componentId))

    @staticmethod
    def getComponentTitleRes(componentId):
        comp = componentConfig.getComponentById(componentId)
        titleRes = getResourceRoot(comp).dyn('title' if comp.purpose != ComponentPurpose.COUPLED else 'counter')
        if not titleRes.exists():
            _logger.error('Missing title string for dogtag component %d', componentId)
            return -1
        return titleRes()

    @staticmethod
    def getComponentDescription(componentId):
        comp = componentConfig.getComponentById(componentId)
        descriptionRes = getResourceRoot(comp).dyn('description')
        if not descriptionRes.exists():
            _logger.error('Missing description string for dogtag component %d', componentId)
            descriptionRes = -1
        return backport.text(descriptionRes())

    @staticmethod
    def getComponentType(componentId):
        comp = componentConfig.getComponentById(componentId)
        return backport.text(R.strings.dogtags.customization.tab.dyn(comp.viewType.value.lower())())

    @staticmethod
    def getPurposeRes(purpose):
        return R.strings.dogtags.customization.category.dyn(purpose.value.lower())()

    @staticmethod
    def getPurposeGroupRes(purposeGroup):
        return R.strings.dogtags.component.purposeGroup.dyn(purposeGroup.lower())()

    @staticmethod
    def getPurposeTooltipRes(purposeGroup):
        return R.strings.dogtags.component.purposeTooltip.dyn(purposeGroup.lower())()

    @staticmethod
    def getAnimationSrc(animation):
        return '' if animation is None else 'animations/dogtags/{}.swf'.format(animation)


dogTagComposer = DogTagComposerClient()
