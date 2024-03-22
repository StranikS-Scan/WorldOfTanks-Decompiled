# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/manual_xml_data_reader.py
import itertools
import logging
from gui.impl import backport
from gui.impl.gen import R
from helpers.html import translation
import resource_helper
from gui.Scaleform.genConsts.MANUAL_TEMPLATES import MANUAL_TEMPLATES
from gui.shared.utils.functions import makeTooltip
_logger = logging.getLogger(__name__)
_CHAPTERS_DATA_PATH = 'gui/manual/'
_CHAPTERS_LIST_XML = 'chapters_list.xml'

class ManualPageTypes(object):
    HINTS_PAGE = 'hints_page'
    MAPS_TRAINING_PAGE = 'maps_training_page'
    VIDEO_PAGE = 'video_page'


_MANUAL_LESSON_TEMPLATES = {ManualPageTypes.HINTS_PAGE: MANUAL_TEMPLATES.HINTS,
 ManualPageTypes.MAPS_TRAINING_PAGE: MANUAL_TEMPLATES.MAPS_TRAINING,
 ManualPageTypes.VIDEO_PAGE: MANUAL_TEMPLATES.VIDEO}

def getChapters(filterFunction):
    chaptersListPath = _CHAPTERS_DATA_PATH + _CHAPTERS_LIST_XML
    with resource_helper.root_generator(chaptersListPath) as ctx, root:
        chapters = __readChapters(ctx, root, filterFunction)
    return chapters


def getPagesIndexesList(filterFunction):
    chaptersData = getChapters(filterFunction)
    return itertools.chain.from_iterable([ chapter['pageIDs'] for chapter in chaptersData ])


def getChaptersIndexesList(filterFunction):
    chaptersData = getChapters(filterFunction)
    return [ chapter['uiData']['index'] for chapter in chaptersData ]


def getChapterData(chapterFileName, filterFunction, chapterTitle=''):
    _logger.debug('ManualXMLDataReader: requested chapter data: %s', chapterFileName)
    chapterPath = _CHAPTERS_DATA_PATH + chapterFileName
    with resource_helper.root_generator(chapterPath) as ctx, root:
        chapter = __readChapter(ctx, root, filterFunction, chapterTitle)
    return chapter


def __isNew(lessonCtx, lessonSection):
    return bool(__getCustomSectionValue(lessonCtx, lessonSection, 'new', safe=True))


def __readChapter(ctx, root, filterFunction, chapterTitle=''):
    pages = []
    details = []
    index = 0
    ctx, section = resource_helper.getSubSection(ctx, root, 'lessons')
    for lessonCtx, lessonSection in resource_helper.getIterator(ctx, section):
        template = __getCustomSectionValue(lessonCtx, lessonSection, 'template')
        if not filterFunction(template):
            continue
        title = translation(__getCustomSectionValue(lessonCtx, lessonSection, 'title'))
        background = __getCustomSectionValue(lessonCtx, lessonSection, 'background')
        description = __getCustomSectionValue(lessonCtx, lessonSection, 'description', safe=True)
        pageId = __getCustomSectionValue(lessonCtx, lessonSection, 'id')
        if description is None:
            description = ''
        else:
            description = translation(description)
        contentRendererLinkage = ''
        if template == ManualPageTypes.MAPS_TRAINING_PAGE:
            contentRendererData = {'text': backport.text(R.strings.maps_training.manualPage.button())}
            contentRendererLinkage = _MANUAL_LESSON_TEMPLATES.get(template)
        elif template == ManualPageTypes.VIDEO_PAGE:
            contentRendererData = __getVideoRendererData(lessonCtx, lessonSection)
            contentRendererLinkage = _MANUAL_LESSON_TEMPLATES.get(template)
        else:
            contentRendererData, hintsCount = __getHintsRendererData(lessonCtx, lessonSection)
            if hintsCount > 0:
                contentRendererLinkage = _MANUAL_LESSON_TEMPLATES.get(template)
        pages.append({'buttonsGroup': 'ManualChapterGroup',
         'pageIndex': int(index),
         'selected': False,
         'hasNewContent': __isNew(lessonCtx, lessonSection),
         'label': str(int(index) + 1),
         'tooltip': {'tooltip': makeTooltip(title)}})
        details.append({'title': title,
         'chapterTitle': chapterTitle,
         'description': description,
         'background': background,
         'contentRendererLinkage': contentRendererLinkage,
         'contentRendererData': contentRendererData,
         'id': pageId,
         'pageType': template})
        index += 1

    chapterData = {'pages': pages,
     'details': details}
    _logger.debug('ManualXMLDataReader:  Read chapter: %s', chapterData)
    return chapterData


def __readChapters(ctx, root, filterFunction):
    ctx, section = resource_helper.getSubSection(ctx, root, 'chapters')
    chapters = []
    index = 0
    for chapterCtx, chapterSection in resource_helper.getIterator(ctx, section):
        filePath = __getCustomSectionValue(chapterCtx, chapterSection, 'file-path')
        title = __getCustomSectionValue(chapterCtx, chapterSection, 'title')
        background = __getCustomSectionValue(chapterCtx, chapterSection, 'background')
        attributes = __getChapterAttributes(filePath, filterFunction)
        ids = attributes.get('ids', [])
        if len(ids) != len(set(ids)):
            _logger.warning('chapter %s has duplicate page ids', title)
        chapter = {'filePath': filePath,
         'pageIDs': ids,
         'newPageIDs': attributes.get('newIds', []),
         'uiData': {'index': int(index),
                    'label': translation(title),
                    'image': background,
                    'tooltip': makeTooltip(translation(title), '\n'.join(attributes.get('chaptersTitles', [])))}}
        if any((ids in chapter['pageIDs'] for chapter in chapters)):
            _logger.warning('chapter %s has duplicate page ids from another chapters', title)
        _logger.debug('ManualXMLDataReader: Read chapters. Chapter: %s', chapter)
        chapters.append(chapter)
        index += 1

    return chapters


def __getChapterAttributes(chapterFileName, filterFunction):
    chaptersTitles = []
    ids = []
    newIds = []
    chapterPath = _CHAPTERS_DATA_PATH + chapterFileName
    with resource_helper.root_generator(chapterPath) as ctx, root:
        ctx, section = resource_helper.getSubSection(ctx, root, 'lessons')
        for lessonCtx, lessonSection in resource_helper.getIterator(ctx, section):
            template = __getCustomSectionValue(lessonCtx, lessonSection, 'template')
            if not filterFunction(template):
                continue
            lessonId = int(__getCustomSectionValue(lessonCtx, lessonSection, 'id'))
            ids.append(lessonId)
            if __getCustomSectionValue(lessonCtx, lessonSection, 'new', safe=True):
                newIds.append(lessonId)
            chaptersTitles.append(translation(__getCustomSectionValue(lessonCtx, lessonSection, 'title')))

    return {'ids': ids,
     'newIds': newIds,
     'chaptersTitles': chaptersTitles}


def __getCustomSectionValue(ctx, section, name, safe=False):
    valueCtx, valueSection = resource_helper.getSubSection(ctx, section, name, safe)
    result = None
    if valueSection is not None:
        item = resource_helper.readItem(valueCtx, valueSection, name)
        result = item.value
    return result


def __getVideoRendererData(lessonCtx, lessonSection):
    video = __getCustomSectionValue(lessonCtx, lessonSection, 'video', safe=True)
    if video is None:
        video = ''
    preview = __getCustomSectionValue(lessonCtx, lessonSection, 'preview', safe=True)
    if preview is None:
        preview = ''
    return {'previewImage': preview,
     'videoUrl': video}


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
