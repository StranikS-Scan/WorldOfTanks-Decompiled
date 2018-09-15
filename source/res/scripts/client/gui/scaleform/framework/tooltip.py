# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/ToolTip.py
from gui import makeHtmlString
from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
from gui.shared import events
from helpers import i18n
from gui.app_loader import g_appLoader
from gui.Scaleform.daapi.settings.tooltips import TOOLTIPS, DYNAMIC_TOOLTIPS

class ToolTip(ToolTipMgrMeta):
    TOOLTIP_KIND = ['header',
     'body',
     'note',
     'attention']
    BLOCK_TAGS_MAP = {'HEADER': {'INFO': [makeHtmlString('html_templates:lobby/tooltips_complex', 'header_info_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'header_info_end')],
                'WARNING': [makeHtmlString('html_templates:lobby/tooltips_complex', 'header_warning_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'header_warning_end')]},
     'BODY': {'INFO': [makeHtmlString('html_templates:lobby/tooltips_complex', 'body_info_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'body_info_end')],
              'WARNING': [makeHtmlString('html_templates:lobby/tooltips_complex', 'body_warning_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'body_warning_end')]},
     'NOTE': {'INFO': [makeHtmlString('html_templates:lobby/tooltips_complex', 'note_info_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'note_info_end')],
              'WARNING': [makeHtmlString('html_templates:lobby/tooltips_complex', 'note_warning_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'note_warning_end')]},
     'ATTENTION': {'INFO': [makeHtmlString('html_templates:lobby/tooltips_complex', 'attention_info_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'attention_info_end')],
                   'WARNING': [makeHtmlString('html_templates:lobby/tooltips_complex', 'attention_warning_start'), makeHtmlString('html_templates:lobby/tooltips_complex', 'attention_warning_end')]}}

    def __init__(self, *noTooltipSpaceIDs):
        """
        Ctor for Tooltip manager
        :param noTooltipSpaceIDs: list of spaceIDs, for which tooltips should not be displayed
        """
        super(ToolTip, self).__init__()
        self._areTooltipsDisabled = False
        self._isAllowedTypedTooltip = True
        self._noTooltipSpaceIDs = noTooltipSpaceIDs

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        if self._areTooltipsDisabled:
            return
        elif not self._isAllowedTypedTooltip:
            return
        else:
            if tooltipType in TOOLTIPS:
                item = TOOLTIPS[tooltipType]
                getDataMethod = item['method']
                linkage = item['tooltip']
                if getDataMethod is not None:
                    tooltipData = getDataMethod(*args)
                    if tooltipData:
                        complexCondition = item['complex']
                        if complexCondition is not None:
                            if complexCondition(tooltipData['data']):
                                self.as_showS(tooltipData, linkage)
                            else:
                                self.__genComplexToolTipFromData(tooltipData['data'], stateType, self.__getDefaultTooltipType())
                        else:
                            self.as_showS(tooltipData, linkage)
                            self.__changeDynamicTooltipVisibility(tooltipType, True)
                elif linkage is not None:
                    self.as_showS(args, linkage)
            return

    def onCreateComplexTooltip(self, tooltipId, stateType):
        if self._areTooltipsDisabled:
            return
        self.__genComplexToolTip(tooltipId, stateType, self.__getDefaultTooltipType())

    def onHideTooltip(self, tooltipId):
        if not self._areTooltipsDisabled:
            self.__changeDynamicTooltipVisibility(tooltipId, False)

    def _populate(self):
        super(ToolTip, self)._populate()
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        self.addListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)

    def _dispose(self):
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        self.removeListener(events.AppLifeCycleEvent.CREATING, self.__onAppCreating)
        for tooltipId in DYNAMIC_TOOLTIPS:
            item = DYNAMIC_TOOLTIPS[tooltipId]
            item.stopUpdates()

        super(ToolTip, self)._dispose()

    @staticmethod
    def __changeDynamicTooltipVisibility(tooltipId, isVisible):
        if tooltipId in DYNAMIC_TOOLTIPS:
            item = DYNAMIC_TOOLTIPS[tooltipId]
            item.changeVisibility(isVisible)

    def __onGUISpaceEntered(self, spaceID):
        self._isAllowedTypedTooltip = spaceID not in self._noTooltipSpaceIDs

    def __onAppCreating(self, appNS):
        if self.app.appNS != appNS:
            self._areTooltipsDisabled = True

    def __getDefaultTooltipType(self):
        item = TOOLTIPS['default']
        return item['tooltip']

    def __genComplexToolTipFromData(self, tooltipData, stateType, tooltipType):
        result = []
        for kind in self.TOOLTIP_KIND:
            if kind in tooltipData and tooltipData[kind] is not None:
                result.append(self.__getFormattedText(tooltipData[kind], kind.upper(), stateType))

        if result:
            self.as_showS(''.join(result), tooltipType)
        return

    def __genComplexToolTip(self, tooltipId, stateType, tooltipType):
        if not tooltipId:
            return
        tooltipIsKey = tooltipId[0] == '#'
        if tooltipIsKey:
            tooltipData = self.__getToolTipFromKey(tooltipId, stateType)
        else:
            tooltipData = self.__getToolTipFromText(tooltipId, stateType)
        if tooltipData:
            self.as_showS(tooltipData, tooltipType)

    def __getToolTipFromKey(self, tooltipId, stateType):
        result = ''
        for kind in self.TOOLTIP_KIND:
            contentKey = tooltipId + '/' + kind
            content = i18n.makeString(contentKey)
            subkey = contentKey[1:].split(':', 1)
            if content and content != subkey[1]:
                result += self.__getFormattedText(content, kind.upper(), stateType)

        return result

    def __getToolTipFromText(self, tooltipId, stateType):
        result = ''
        for tooltipKind in self.TOOLTIP_KIND:
            tooltipBlock = tooltipKind.upper()
            tags = {'open': '{' + tooltipBlock + '}',
             'close': '{/' + tooltipBlock + '}'}
            indicies = {'start': tooltipId.find(tags['open']),
             'end': tooltipId.find(tags['close'])}
            if indicies['start'] != -1 and indicies['end'] != -1:
                indicies['start'] += len(tags['open'])
                result += self.__getFormattedText(tooltipId[indicies['start']:indicies['end']], tooltipBlock, stateType)

        return result

    def __getFormattedText(self, text, block_type, format_type):
        if format_type is None:
            format_type = 'INFO'
        tags = self.__getTags(block_type, format_type)
        return tags[0] + text + tags[1] + '\n' + "<font size='1' > </font>" + '\n'

    def __getTags(self, block_type, format_type):
        blockTag = self.BLOCK_TAGS_MAP[block_type]
        if format_type in blockTag:
            formatTag = blockTag[format_type]
            return [formatTag[0], formatTag[1]]
        return ['', '']
