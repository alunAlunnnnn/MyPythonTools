import arcpy
import datetime
import math


class ToolValidator(object):
    """Class for validating a tool's parameter values and controlling
    the behavior of the tool's dialog."""

    def __init__(self):
        """Setup arcpy and the list of tool parameters."""
        self.params = arcpy.GetParameterInfo()
        tzList = []
        tzDict = {}
        for tz in arcpy.time.ListTimeZones():
            tZone = arcpy.time.TimeZoneInfo(tz)
            if tZone.name not in tzList:
                tzDict[tZone.name] = tz
                tzList.append(tZone.name)
        self.tzNames = tzList
        self.tzDictionary = tzDict

    def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        self.params[0].datatype = ["GPFeatureLayer", "DEFeatureClass"]
        self.params[4].filter.list = self.tzNames
        # self.params[5].value = datetime.date.today().strftime('%m/%d/%y')
        self.params[9].category = 'Atmospheric Refraction'
        self.params[10].category = 'Atmospheric Refraction'
        self.params[11].category = 'Atmospheric Refraction'
        self.params[12].category = 'Atmospheric Refraction'
        self.params[1].category = '默认参数'
        self.params[2].category = '默认参数'
        self.params[16].category = '默认参数'
        self.params[17].category = '默认参数'
        return

    def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if self.params[0].value:
            desc = arcpy.Describe(self.params[0].value)
            extent = desc.extent
            zValues = desc.hasZ
            sr = extent.spatialReference
            zMin, horizon = 0, 250
            srUnit = 'Meters'
            if extent.ZMin:
                zMin += round(extent.ZMin, 1)

            if sr:
                if sr.type == 'Projected':
                    srUnit = extent.spatialReference.linearUnitName
                    if srUnit in ('Foot', 'Foot_US', 'Foot_Int'):
                        srUnit = 'Feet'
                        horizon = 30000
                    else:
                        srUnit += 's'
                        horizon = 10000
                    horizon += round(math.sqrt((extent.height / 2) ** 2
                                               + (extent.width / 2) ** 2), 1)
                else:
                    mExt = desc.extent.projectAs(arcpy.SpatialReference(54032))
                    horizon += math.sqrt((mExt.height / 2) ** 2 + (mExt.width / 2) ** 2)
            if not self.params[1].altered:
                if zValues:
                    if "nan" in str(zMin):
                        zMin = ""
                else:
                    zMin = 0

                if "nk" in str(srUnit):
                    srUnit = "Unknown"

                self.params[1].value = '{0} {1}'.format(zMin, srUnit)

            if not self.params[2].altered:
                if "nk" in str(srUnit):
                    srUnit = "Unknown"

                self.params[2].value = '{0} {1}'.format(horizon, srUnit)

        self.params[8].enabled = False
        if self.params[7].value and self.params[5].value:
            if self.params[7].value.date() > self.params[5].value.date():
                self.params[8].enabled = False
                self.params[8].filter.list = [1, (self.params[7].value.date() -
                                                  self.params[5].value.date()).days]
            else:
                self.params[8].enabled = False
        if self.params[9].value == True:
            self.params[10].enabled = True
            self.params[11].enabled = True
            self.params[12].enabled = True
        else:
            self.params[10].enabled = False
            self.params[11].enabled = False
            self.params[12].enabled = False

        if self.params[23].value == True:
            self.params[5].value = '2020/9/22 9:00:00'
            self.params[7].value = '2020/9/22 15:00:00'
        else:
            # self.params[5].value = datetime.date.today().strftime('%y/%m/%d')
            # self.params[5].value = '2020/12/07'
            self.params[7].value = ''

        return

    def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if self.params[0].value:
            desc = arcpy.Describe(self.params[0].value)
            if desc.spatialReference.name == 'Unknown':
                self.params[0].setErrorMessage('Reference data must have a '
                                               'spatial reference defined.')
        if self.params[1].value:
            if "Unknown" in str(self.params[1].value):
                self.params[1].setErrorMessage('Elevation units must be set.')

        if self.params[2].value:
            if "Unknown" in str(self.params[2].value):
                self.params[2].setErrorMessage('Distance units must be set.')

        if self.params[5].value and self.params[7].value:
            if self.params[7].value.time():
                if self.params[7].value.time() < self.params[5].value.time():
                    self.params[7].setErrorMessage('End time must be on the same day as the '
                                                   'start time.')
            if self.params[7].value.date() < self.params[5].value.date():
                self.params[7].setErrorMessage('End date must be equal to or '
                                               'greater than start date.')
            if self.params[7].value.date() > self.params[5].value.date():
                self.params[7].setErrorMessage('End date must be on the same day as the start date.')

        return