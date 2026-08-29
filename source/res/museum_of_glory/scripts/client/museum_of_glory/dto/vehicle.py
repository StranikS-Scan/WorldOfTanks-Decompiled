# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/dto/vehicle.py
from museum_of_glory.dto.base import BaseDto

class VehicleDto(BaseDto):
    __slots__ = ('vehicle', 'name', 'intCD', 'strCD', 'year', 'descriptions', 'voiceoverLength')

    def __init__(self, vehicle, name, intCD, strCD, year, description, voiceoverLength):
        super(VehicleDto, self).__init__()
        self.vehicle = vehicle
        self.name = name
        self.intCD = intCD
        self.strCD = strCD
        self.year = year
        self.descriptions = description
        self.voiceoverLength = voiceoverLength
