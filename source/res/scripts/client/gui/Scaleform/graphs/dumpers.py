# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/dumpers.py
# Compiled at: 2011-10-20 18:37:36
from items import getTypeInfoByName, vehicles
from gui.Scaleform.graphs import custom_items

class VehicleComponentsGraphDumper(object):

    def dump(self, graph):
        return {'autounlocked': graph.autounlockedPoints,
         'processed': graph.points}


class VehicleComponentsGraphXMLDumper(VehicleComponentsGraphDumper):
    __xmlBody = '<?xml version="1.0" encoding="utf-8"?><graph><autounlocked>{0:>s}</autounlocked><processed>{1:>s}</processed></graph>'
    __pointFormat = '<point><id>%(compactDescr)r</id><type>%(type)s</type><typeString>%(typeString)s</typeString><nameString>%(nameString)s</nameString><tags>%(tags)s</tags><level>%(level)d</level><toolTip><![CDATA[%(toolTip)s]]></toolTip><experience>%(experience)d</experience><unlockIdx>%(unlockIdx)d</unlockIdx><unlocked>%(unlocked)d</unlocked><iconPath>%(iconPath)s</iconPath><smallIconPath>%(smallIconPath)s</smallIconPath><nation>%(nation)s</nation><relations>%(relations)s</relations><pickleDump><![CDATA[%(pickleDump)s]]></pickleDump><shopPrice>%(shopPrice)d</shopPrice></point>'

    def dump(self, graph):
        points = graph.points
        autounlockedPoints = graph.autounlockedPoints
        invItems = graph.invItems
        shopPrices = graph.shopPrices
        dump = self.__xmlBody.format(self.__buildAutounlockedPointsData(autounlockedPoints, invItems, shopPrices), self.__buildProcessedPointsData(points, invItems, graph.shopPrices))
        return dump

    def __buildAutounlockedPointsData(self, autounlockedPoints, invItems, shopPrices):
        pointsDump = []
        for point in autounlockedPoints:
            compactDescr = point.compactDescr
            data = self.__getVehicleComponentData(compactDescr, invItems)
            data.update({'tags': '',
             'experience': point.experience,
             'unlockIdx': point.unlockIdx,
             'unlocked': point.unlocked,
             'relations': '',
             'shopPrice': shopPrices.get(compactDescr, (0, 0))[0]})
            pointData = self.__pointFormat % data
            pointsDump.append(pointData)

        return ''.join(pointsDump)

    def __buildProcessedPointsData(self, points, invItems, shopPrices):
        pointsDump = []
        for point in points:
            compactDescr = point.compactDescr
            data = self.__getVehicleComponentData(compactDescr, invItems)
            tags = data['tags']
            itemTypeName = data['type']
            tagsDump = []
            for tag in tags:
                info = getTypeInfoByName(itemTypeName)['tags'][tag]
                if vehicles.VEHICLE_CLASS_TAGS & frozenset([info['name']]):
                    tagsDump.append('<tag><userString>%(userString)s</userString><name>%(name)s</name></tag>' % info)

            relationsDump = []
            for relation in point.relations:
                relationsDump.append('<relation>%r</relation>' % relation)

            data.update({'tags': ''.join(tagsDump),
             'experience': point.experience,
             'unlockIdx': point.unlockIdx,
             'unlocked': point.unlocked,
             'relations': ''.join(relationsDump),
             'shopPrice': shopPrices.get(compactDescr, (0, 0))[0]})
            pointData = self.__pointFormat % data
            pointsDump.append(pointData)

        return ''.join(pointsDump)

    def __getVehicleComponentData(self, compactDescr, invItems):
        item = invItems.get(compactDescr, custom_items._VehicleComponent(compactDescr))
        return {'compactDescr': compactDescr,
         'type': item.itemTypeName,
         'typeString': item.userType,
         'nameString': item.name,
         'tags': item.tags,
         'level': item.level,
         'toolTip': item.longName,
         'nation': item.nationName,
         'iconPath': item.icon,
         'smallIconPath': item.smallIcon,
         'pickleDump': item.pack()}


class VehiclesGraphXMLDumper(VehicleComponentsGraphDumper):
    __xmlBody = '<?xml version="1.0" encoding="utf-8"?><graph><points>{0:>s}</points></graph>'
    __pointFormat = '<point><id>%(compactDescr)r</id><nameString>%(nameString)s</nameString><tags>%(tags)s</tags><level>%(level)s</level><earnedExperience>%(earnedExperience)d</earnedExperience><unlocked>%(unlocked)d</unlocked><smallIconPath>%(smallIconPath)s</smallIconPath><elite>%(elite)d</elite><toolTip>%(toolTip)s</toolTip><pickleDump><![CDATA[%(pickleDump)s]]></pickleDump><shopPrice>%(shopPrice)d</shopPrice><displayInfo>%(displayInfo)s</displayInfo></point>'

    def dump(self, graph):
        return self.__xmlBody.format(self.__buildPointsData(graph.points, graph.invItems, graph.shopPrices))

    def __buildPointsData(self, points, invItems, shopPrices):
        pointsDump = []
        for point in points:
            compactDescr = point.compactDescr
            data = self.__getVehicleComponentData(compactDescr, invItems)
            tags = data['tags']
            itemTypeName = data['type']
            tagsDump = []
            for tag in tags:
                info = getTypeInfoByName(itemTypeName)['tags'][tag]
                if vehicles.VEHICLE_CLASS_TAGS & frozenset([info['name']]):
                    tagsDump.append('<tag><userString>%(userString)s</userString><name>%(name)s</name></tag>' % info)

            data.update({'tags': ''.join(tagsDump),
             'earnedExperience': point.earnedExperience,
             'unlocked': point.unlocked,
             'elite': point.elite,
             'shopPrice': shopPrices.get(compactDescr, (0, 0))[0],
             'displayInfo': point.displayInfo})
            pointData = self.__pointFormat % data
            pointsDump.append(pointData)

        return ''.join(pointsDump)

    def __getVehicleComponentData(self, compactDescr, invItems):
        item = invItems.get(compactDescr, custom_items._VehicleComponent(compactDescr))
        return {'compactDescr': compactDescr,
         'type': item.itemTypeName,
         'nameString': item.name,
         'tags': item.tags,
         'level': item.level,
         'toolTip': item.longName,
         'smallIconPath': item.smallIcon,
         'pickleDump': item.pack()}
