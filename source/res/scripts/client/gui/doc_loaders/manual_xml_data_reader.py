# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/manual_xml_data_reader.py
import logging
from helpers.html import translation
import resource_helper
from gui.Scaleform.genConsts.MANUAL_TEMPLATES import MANUAL_TEMPLATES
from gui.shared.utils.functions import makeTooltip
_logger = logging.getLogger(__name__)
_CHAPTERS_DATA_PATH = 'gui/manual/'
_CHAPTERS_LIST_XML = 'chapters_list.xml'
_HINTS_PAGE = 'hints_page'
_BOOTCAMP_PAGE = 'bootcamp_page'
_MANUAL_LESSON_TEMPLATES = {_HINTS_PAGE: MANUAL_TEMPLATES.HINTS,
 _BOOTCAMP_PAGE: MANUAL_TEMPLATES.BOOTCAMP}

def getChapters(isBootcampEnabled):
    chaptersListPath = _CHAPTERS_DATA_PATH + _CHAPTERS_LIST_XML
    with resource_helper.root_generator(chaptersListPath) as ctx, root:
        chapters = __readChapters(ctx, root, isBootcampEnabled)
    return chapters


def getChaptersIndexesList(isBootcampEnabled):
    chaptersData = getChapters(isBootcampEnabled)
    return [ chapter['uiData']['index'] for chapter in chaptersData ]


def getChapterData(chapterFileName, isBootcampEnabled, bootcampRunCount):
    _logger.debug('ManualXMLDataReader: requested chapter data: %s', chapterFileName)
    chapterPath = _CHAPTERS_DATA_PATH + chapterFileName
    with resource_helper.root_generator(chapterPath) as ctx, root:
        chapter = __readChapter(ctx, root, isBootcampEnabled, bootcampRunCount)
    return chapter


def __readChapter(ctx, root, isBootcampEnabled, bootcampRunCount):
    pages = []
    details = []
    index = 0
    ctx, section = resource_helper.getSubSection(ctx, root, 'lessons')
    for lessonCtx, lessonSection in resource_helper.getIterator(ctx, section):
        template = __getCustomSectionValue(lessonCtx, lessonSection, 'template')
        title = translation(__getCustomSectionValue(lessonCtx, lessonSection, 'title'))
        background = __getCustomSectionValue(lessonCtx, lessonSection, 'background')
        description = __getCustomSectionValue(lessonCtx, lessonSection, 'description', safe=True)
        if description is None:
            description = ''
        else:
            description = translation(description)
        contentRendererData = None
        contentRendererLinkage = ''
        hintsCount = 0
        if template is _BOOTCAMP_PAGE:
            if not isBootcampEnabled:
                continue
            contentRendererData = __getBootcampRendererData(bootcampRunCount)
            contentRendererLinkage = _MANUAL_LESSON_TEMPLATES.get(template)
        else:
            contentRendererData, hintsCount = __getHintsRendererData(lessonCtx, lessonSection)
            if hintsCount > 0:
                contentRendererLinkage = _MANUAL_LESSON_TEMPLATES.get(template)
        pages.append({'buttonsGroup': 'ManualChapterGroup',
         'pageIndex': int(index),
         'selected': False,
         'label': str(int(index) + 1),
         'tooltip': {'tooltip': makeTooltip(title)}})
        details.append({'title': title,
         'description': description,
         'background': background,
         'contentRendererLinkage': contentRendererLinkage,
         'contentRendererData': contentRendererData})
        index += 1

    chapterData = {'pages': pages,
     'details': details}
    _logger.debug('ManualXMLDataReader:  Read chapter: %s', chapterData)
    return chapterData


def __readChapters(ctx, root, isBootcampEnabled):
    ctx, section = resource_helper.getSubSection(ctx, root, 'chapters')
    chapters = []
    index = 0
    for chapterCtx, chapterSection in resource_helper.getIterator(ctx, section):
        filePath = __getCustomSectionValue(chapterCtx, chapterSection, 'file-path')
        title = __getCustomSectionValue(chapterCtx, chapterSection, 'title')
        background = __getCustomSectionValue(chapterCtx, chapterSection, 'background')
        lessonsTitlesList = __getChaptersTitlesList(filePath, isBootcampEnabled)
        chapter = {'filePath': filePath,
         'uiData': {'index': int(index),
                    'label': translation(title),
                    'image': background,
                    'tooltip': makeTooltip(translation(title), '\n'.join(lessonsTitlesList))}}
        _logger.debug('ManualXMLDataReader: Read chapters. Chapter: %s', chapter)
        chapters.append(chapter)
        index += 1

    return chapters


def __getChaptersTitlesList(chapterFileName, isBootcampEnabled):
    chaptersTitles = []
    chapterPath = _CHAPTERS_DATA_PATH + chapterFileName
    with resource_helper.root_generator(chapterPath) as ctx, root:
        ctx, section = resource_helper.getSubSection(ctx, root, 'lessons')
        for lessonCtx, lessonSection in resource_helper.getIterator(ctx, section):
            title = translation(__getCustomSectionValue(lessonCtx, lessonSection, 'title'))
            template = __getCustomSectionValue(lessonCtx, lessonSection, 'template')
            if template is _BOOTCAMP_PAGE and not isBootcampEnabled:
                continue
            chaptersTitles.append(title)

    return chaptersTitles


def __getCustomSectionValue(ctx, section, name, safe=False):
    valueCtx, valueSection = resource_helper.getSubSection(ctx, section, name, safe)
    result = None
    if valueSection is not None:
        item = resource_helper.readItem(valueCtx, valueSection, name)
        result = item.value
    return result


def __getBootcampRendererData(bootcampRunCount):
    if bootcampRunCount == 0:
        bootcampText = translation('#bootcamp:request/bootcamp/start')
    else:
        bootcampText = translation('#bootcamp:request/bootcamp/return')
    return {'text': bootcampText}


def __getHintsRendererData(lessonCtx, lessonSection):
    hints = []
    contentRendererData = None
    hintsCtx, hintsSection = resource_helper.getSubSection(lessonCtx, lessonSection, 'hints', safe=True)
    if hintsSection is not None:
        for hintCtx, hintSection in resource_helper.getIterator(hintsCtx, hintsSection):
            hintText = translation(__getCustomSectionValue(hintCtx, hintSection, 'text'))
            hintIcon = __getCustomSectionValue(hintCtx, hintSection, 'icon')
            hints.append({'text': hintText,
             'icon': hintIcon})

        contentRendererData = {'hints': hints}
    return (contentRendererData, len(hints))
