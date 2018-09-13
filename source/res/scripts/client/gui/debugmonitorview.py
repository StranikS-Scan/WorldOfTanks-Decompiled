# Embedded file name: scripts/client/gui/DebugMonitorView.py
import BigWorld
from gui.DebugView import DebugView
from gui.DebugView import DebugViewItem
from debug_utils import *

class DebugMonitorView(DebugView):

    def __init__(self, textureName = '', parentGUI = None):
        DebugView.__init__(self, textureName, parentGUI)
        self.__contentInfo = {}
        self.__newContentInfo = {}

    def destroy(self):
        DebugView.destroy(self)

    def setContent(self, content):
        if not self.getVisible():
            return
        else:
            contentItems = self.__buildContentItemsBy(content)
            if contentItems is None:
                self.__roolbackContentInfo()
                return
            self.__commitContentInfo()
            self.__updateViewByContentItems(contentItems)
            return

    def __setItem(self, nameStr, valueStr, dividerStr, item = None):
        if item is None:
            item = DebugViewItem()
            item.setFont(('system_small.font', 'system_small.font'))
            item.setColour(((255, 255, 255, 255), (255, 255, 255, 255)))
            newKeyname = 'key_' + str(self.getItemsCount())
            self.addItem(newKeyname, item)
        item.setName(nameStr)
        item.setValue(valueStr)
        item.setDivider(dividerStr)
        item.setVisible(True)
        return

    def __updateContentInfoItem(self, keyname, value):
        resultDelta = 0
        if keyname in self.__contentInfo:
            lastValue, resultDelta = self.__contentInfo[keyname]
            if lastValue != value:
                try:
                    resultDelta = value - lastValue
                except:
                    pass

        self.__newContentInfo[keyname] = (value, resultDelta)
        return resultDelta

    def __commitContentInfo(self):
        self.__contentInfo = self.__newContentInfo
        self.__newContentInfo = {}

    def __roolbackContentInfo(self):
        self.__newContentInfo = {}

    def __buildContentItemsBy(self, content, baseIndent = 0, baseKeyname = ''):
        result = []
        try:
            if isinstance(content, dict):
                for itemName, itemValue in sorted(content.items()):
                    itemName = str(itemName)
                    itemKeyname = baseKeyname + itemName
                    if isinstance(itemValue, dict):
                        result += [(' ' * baseIndent + itemName + ':', '', '')]
                        subResult = self.__buildContentItemsBy(itemValue, baseIndent + 1, itemKeyname)
                        if subResult is not None:
                            result += subResult
                    if isinstance(itemValue, int) or isinstance(itemValue, float) or isinstance(itemValue, bool) or isinstance(itemValue, str) or itemValue is None:
                        deltaValue = self.__updateContentInfoItem(itemKeyname, itemValue)
                        valueStr1 = '%0.3f' % itemValue if isinstance(itemValue, float) else str(itemValue)
                        valueStr2 = '%0.3f' % deltaValue if isinstance(deltaValue, float) else str(deltaValue)
                        itemValueStr = valueStr1 + ' (' + valueStr2 + ')'
                        result += [(' ' * baseIndent + itemName, itemValueStr, ' = ')]

        except:
            LOG_ERROR("<DebugMonitor>: can't build content items. Look exception:")
            LOG_CURRENT_EXCEPTION()
            return

        return result

    def __updateViewByContentItems(self, contentItems):
        curIndex = -1
        for curItemKeyname in self.getListKeynames():
            curItem = self.getItem(curItemKeyname)
            curIndex += 1
            if curIndex >= len(contentItems):
                curItem.setVisible(False)
                continue
            curNameStr, curValueStr, curDividerStr = contentItems[curIndex]
            self.__setItem(curNameStr, curValueStr, curDividerStr, curItem)

        processedItemsCount = curIndex + 1
        for curIndex in xrange(processedItemsCount, len(contentItems)):
            curNameStr, curValueStr, curDividerStr = contentItems[curIndex]
            self.__setItem(curNameStr, curValueStr, curDividerStr, None)

        self.update()
        return
