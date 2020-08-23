import arcpy as  ARCPY
import arcpy.na as  NET
import os as OS
import sys as SYS
import SSDataObject as SSDO
import SSUtilities as UTILS
import WeightsUtilities as WU

swapType = {'POLYGON_CONTIGUITY_(FIRST_ORDER)': "CONTIGUITY_EDGES_ONLY",
            'MANHATTAN_DISTANCE': "MANHATTAN_DISTANCE",
            'EUCLIDEAN_DISTANCE': "EUCLIDEAN_DISTANCE",
            'MANHATTAN': "MANHATTAN_DISTANCE",
            'EUCLIDEAN': "EUCLIDEAN_DISTANCE"
            }

supportDist = ["Feet", "Meters", "Kilometers", "Miles"]
pathLayers = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                          "Layers")

convertFamilyType = {'CONTINUOUS': 'GAUSSIAN',
                     'BINARY': 'LOGIT',
                     'COUNT': 'POISSON'}


def createField(name, outPath, type=None, aliasName=None):
    """ Method for conveniently creating Field Object
    :param name:
    :param type:
    :return:
    """
    newField = ARCPY.Field()
    newField.name = name
    if type:
        if type.upper() == "INTEGER":
            type = "Long"
        if type.upper() in ["FLOAT", "SINGLE"]:
            type = "Double"
        newField.type = type
    if aliasName:
        newField.aliasName = aliasName
    return newField


def makeDerivedRasterLayers(indVarNames, outputFC):
    outRasterLayers = []

    #### Get Output FC Prefix ####
    outPath, outName = OS.path.split(outputFC)
    outputPref, ext = OS.path.splitext(outName)

    #### Add Intercept ####
    interName = outputPref + "_" + "INTERCEPT"
    outRasterLayers.append(interName)

    #### Create Slope Rasters ####
    for varName in indVarNames:
        varNameOut = outputPref + "_" + varName
        outRasterLayers.append(varNameOut)

    return outRasterLayers


def baseDistanceMatchList(distanceFCs):
    pairs = []
    for fc in distanceFCs:
        pairs.append([fc, fc])

    return pairs


def matchVariables(inputVariables, describePred):
    predNames = [i.name for i in describePred.fields]
    pairs = []
    for indOut in inputVariables:
        predOut = ""
        if indOut in predNames:
            predOut = indOut
        pairs.append([predOut, indOut])

    return pairs


def returnTravelModes(param):
    try:
        return NET.GetTravelModes(param.value.value)
    except:
        d = ARCPY.Describe(param.value)
        return NET.GetTravelModes(d.catalogPath)


def returnRenderLayerFile(numResults, renderFile):
    if numResults < 6:
        fileName, fileExt = OS.path.splitext(renderFile)
        fileName = fileName + "{0}"
        fileName = fileName.format(numResults)
        return fileName + fileExt
    else:
        return renderFile


def checkLicense():
    productInfo = ARCPY.ProductInfo()
    pro = productInfo in ["ArcInfo", "ArcServer"]
    return pro


def paramChanged(param, checkValue=False):
    changed = param.altered and not param.hasBeenValidated
    if checkValue:
        if param.value:
            return changed
        else:
            return False
    else:
        return changed


def enableParameters(enable=[], disable=[]):
    """ enable and disable list of parameters
    """
    for i in enable:
        if i is not None:
            i.enabled = True
    for j in disable:
        if j is not None:
            j.enabled = False


def enableParametersBy(parameters, enable=[], disable=[]):
    """ enable and disable list of parameters
    """
    for i in enable:
        parameters[i].enabled = True
    for j in disable:
        parameters[j].enabled = False


def clearParameter(parameter):
    parameter.enabled = False
    parameter.value = None


def isThree():
    """Returns boolean indicating whether Python 3."""
    return SYS.version_info.major == 3


def canMakeGraph():
    """Returns boolean indicating whether DM.MakeGraph will work.
    False for ProApp and 64-bit Background.
    """
    #### Can't be Linux ####
    if "WIN" not in SYS.platform.upper():
        return False

    #### Can't be Pro App ####
    if isThree():
        return False

    #### Can't be 64-Bit Background ####
    arcInfo = ARCPY.GetInstallInfo()
    isDesktop = arcInfo['ProductName'].upper() == "DESKTOP"
    is64 = SYS.version.upper().count("64 BIT")
    if isDesktop and is64:
        return False
    else:
        return True


###### HL Clustering
def setEnvSpatialReference(inputSpatialRef):
    """Returns a spatial reference object of Env Setting if exists.

    INPUTS:
    inputSpatialRef (obj): input spatial reference object

    OUTPUT:
    spatialRef (class): spatial reference object
    """

    envSetting = ARCPY.env.outputCoordinateSystem
    if envSetting != None:
        #### Set to Environment Setting ####
        spatialRef = envSetting
    else:
        spatialRef = inputSpatialRef

    return spatialRef


def returnOutputSpatialRef(inputSpatialRef, outputFC=None):
    """Returns a spatial reference object for output and analysis based
    on the hierarchical setting. (1)

    INPUTS:
    inputSpatialRef (obj): input spatial reference object
    outputFC (str): catalog path to the output feature class (2)

    OUTPUT:
    spatialRef (class): spatial reference object

    NOTES:
    (1) Hierarchy for Spatial Reference:
        Feature Data Set --> Environment Settings --> Input Feature Class
    (2) The outputFC can be an input feature for models with no feature
        class output.
    """

    if outputFC == None or outputFC == "":
        spatialRef = setEnvSpatialReference(inputSpatialRef)
    else:
        dirName = OS.path.dirname(outputFC)
        descDir = ARCPY.Describe(dirName)
        dirType = descDir.DataType
        if dirType == "FeatureDataset":
            #### Set to FeatureDataset if True ####
            spatialRef = descDir.SpatialReference
        else:
            spatialRef = setEnvSpatialReference(inputSpatialRef)

    return spatialRef


def getLinearUnitFloat(paramValue):
    import locale as LOCALE
    value, unit = str(paramValue).split()
    return LOCALE.atof(value)


def tableCheck(parameter):
    """ Check and update the Table Extension (dbf)
    INPUT:
        parameter (Parameter Object): Parameter Output Table
    """
    if parameter.altered:
        valueTemp = str(parameter.value)

        #### Get Output Table Name With Extension if Appropriate ####
        if valueTemp.upper().startswith("IN_MEMORY"):

            if ".DBF" in valueTemp.upper():
                valueTemp = valueTemp.upper().replace(".DBF", "").lower()
                parameter.value = valueTemp
                return

        if not UTILS.isGDB(valueTemp):

            if ".DBF" not in valueTemp.upper():
                parameter.value = valueTemp + ".dbf"
        else:

            if ".DBF" in valueTemp.upper():
                parameter.value = valueTemp.replace(".dbf", "").replace(".DBF", "")

        parameter.value = valueTemp


class Toolbox(object):
    def __init__(self):
        self.label = "Spatial Statistics Tools"
        self.alias = "stats"
        self.helpContext = 50
        self.tools = [HighLowClustering, SpatialAutocorrelation, ClustersOutliers, HotSpots,
                      CentralFeature, DirectionalMean, CalculateAreas, ExportXYv,
                      MultiDistanceSpatialClustering, CalculateDistanceBand,
                      AverageNearestNeighbor, DirectionalDistribution, MeanCenter,
                      StandardDistance, CollectEvents, GeographicallyWeightedRegression,
                      OrdinaryLeastSquares, GWR, GeneralizedLinearRegression, ConvertSpatialWeightsMatrixtoTable,
                      MedianCenter, GroupingAnalysis, ExploratoryRegression,
                      IncrementalSpatialAutocorrelation, OptimizedHotSpotAnalysis,
                      SimilaritySearch, GenerateNetworkSpatialWeights, OptimizedOutlierAnalysis,
                      GenerateSpatialWeightsMatrix, DensityBasedClustering,
                      SpatiallyConstrainedMultivariateClustering, MultivariateClustering, Forest,
                      LocalBivariateRelationships, BuildBalancedZones]

        self.tools.append(ColocationAnalysis)


class HighLowClustering(object):
    def __init__(self):
        self.label = "High/Low Clustering (Getis-Ord General G)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Analyzing Patterns"
        self.helpContext = 9010001
        self.params = None
        #### Set Lists of Spatial Concepts ####
        self.baseConcepts = ["INVERSE_DISTANCE",
                             "INVERSE_DISTANCE_SQUARED",
                             "FIXED_DISTANCE_BAND",
                             "ZONE_OF_INDIFFERENCE",
                             "K_NEAREST_NEIGHBORS",
                             "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.allConcepts = ["INVERSE_DISTANCE",
                            "INVERSE_DISTANCE_SQUARED",
                            "FIXED_DISTANCE_BAND",
                            "ZONE_OF_INDIFFERENCE",
                            "K_NEAREST_NEIGHBORS",
                            "CONTIGUITY_EDGES_ONLY",
                            "CONTIGUITY_EDGES_CORNERS",
                            "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.distanceConcepts = self.baseConcepts[0:4]
        self.currentConcepts = [i for i in self.baseConcepts]
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]
        self.rowTypes = ["ROW", "NONE"]

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Input Field",
                                 name="Input_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Generate Report",
                                 name="Generate_Report",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['GENERATE_REPORT', 'NO_REPORT']

        param3 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                 name="Conceptualization_of_Spatial_Relationships",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['INVERSE_DISTANCE', 'INVERSE_DISTANCE_SQUARED',
                              'FIXED_DISTANCE_BAND', 'ZONE_OF_INDIFFERENCE',
                              'K_NEAREST_NEIGHBORS',
                              'CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE']

        param3.value = 'INVERSE_DISTANCE'

        param4 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']

        param4.value = 'EUCLIDEAN_DISTANCE'

        param5 = ARCPY.Parameter(displayName="Standardization",
                                 name="Standardization",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"

        param5.filter.list = ['NONE', 'ROW']

        param5.value = 'ROW'

        param6 = ARCPY.Parameter(displayName="Distance Band or Threshold Distance",
                                 name="Distance_Band_or_Threshold_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0.0, 999999999999999.0]

        param7 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['swm', 'gwt', 'txt']
        param7.enabled = False

        param8 = ARCPY.Parameter(displayName="Observed General G",
                                 name="Observed_General_G",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param9 = ARCPY.Parameter(displayName="ZScore",
                                 name="ZScore",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param10 = ARCPY.Parameter(displayName="PValue",
                                  name="PValue",
                                  datatype="GPDouble",
                                  parameterType="Derived",
                                  direction="Output")

        param11 = ARCPY.Parameter(displayName="Report File",
                                  name="Report_File",
                                  datatype="DEFile",
                                  parameterType="Derived",
                                  direction="Output")
        # param11.filter.list = ['html'] ##issue
        param11.enabled = False

        #### User Defined with Number of Neighbors Parameters (Required) ####
        param12 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param12.filter.type = "Range"
        param12.filter.list = [2, 1000]
        param12.enabled = False

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9, param10, param11, param12]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.checkContiguity(self.params[0].value)

        if self.params[4].altered:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in swapType:
                self.params[4].value = swapType[value4]

        #### Enable Type of Distance Measure if Appropriate ####
        if self.params[3].altered:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 == "POLYGON_CONTIGUITY_(FIRST_ORDER)":
                value3 = "CONTIGUITY_EDGES_ONLY"
                self.params[3].value = value3
            if value3 in self.distanceConcepts:
                self.params[4].enabled = 1
                self.params[6].enabled = 1
            else:
                self.params[4].enabled = 0
                self.params[6].enabled = 0

            if value3 == "GET_SPATIAL_WEIGHTS_FROM_FILE":
                self.params[7].enabled = 1
                self.params[5].enabled = 0
            else:
                self.params[7].enabled = 0
                self.params[5].enabled = 1

            if value3 == "K_NEAREST_NEIGHBORS":
                self.params[12].enabled = 1
                if not self.params[12].value:
                    self.params[12].value = 8
            else:
                clearParameter(self.params[12])

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[3].hasError():
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in self.currentConcepts:
                self.params[3].clearMessage()
            if value3.count("CONTIGUITY"):
                self.params[3].clearMessage()

        #### Required SWM or KNN ####
        if self.params[3].value:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 == 'GET_SPATIAL_WEIGHTS_FROM_FILE':
                if self.params[7].value in ["", "#", None]:
                    self.params[7].setIDMessage("ERROR", 930)
            if value3 == "K_NEAREST_NEIGHBORS":
                if not self.params[12].value:
                    self.params[12].setIDMessage("ERROR", 976)

        if self.params[4].hasError():
            if self.params[4].value.upper().replace(" ", "_") in self.distanceTypes:
                self.params[4].clearMessage()

        if self.params[5].hasError():
            if self.params[5].value.upper() in self.rowTypes:
                self.params[5].clearMessage()

    def checkContiguity(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            outSpatRef = setEnvSpatialReference(desc.SpatialReference)
            if outSpatRef.type.upper() == "GEOGRAPHIC":
                self.params[4].enabled = False
            else:
                self.params[4].enabled = True
            if desc.ShapeType.upper() == "POLYGON":
                self.params[3].filter.list = self.allConcepts
            else:
                self.params[3].filter.list = self.baseConcepts
        except:
            self.params[3].filter.list = self.baseConcepts
        self.currentConcepts = self.params[3].filter.list

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import GeneralG as GG
        inputFC = parameters[0].valueAsText
        varName = parameters[1].valueAsText.upper()
        displayIt = parameters[2].value

        #### Parse Space Concept ####
        spaceConcept = parameters[3].valueAsText.upper().replace(" ", "_")
        if spaceConcept == "INVERSE_DISTANCE_SQUARED":
            exponent = 2.0
        else:
            exponent = 1.0
        try:
            spaceConcept = WU.convertConcept[spaceConcept]
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = parameters[4].valueAsText.upper().replace(" ", "_")
        concept = WU.conceptDispatch[distanceConcept]

        #### Row Standardized ####
        rowStandard = parameters[5].valueAsText.upper()
        if rowStandard == 'ROW':
            rowStandard = True
        else:
            rowStandard = False

        #### Distance Threshold ####
        threshold = UTILS.getNumericParameter(6, parameters)

        #### Spatial Weights File ####
        weightsFile = parameters[7].valueAsText
        if weightsFile is None and wType == 8:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and wType != 8:
            ARCPY.AddIDMessage("WARNING", 925)
            weightsFile = None

        #### Number of Neighbors ####
        numNeighs = UTILS.getNumericParameter(12, parameters)
        if numNeighs is None:
            numNeighs = 0

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, useChordal=True)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### Populate SSDO with Data ####
        if WU.gaTypes[spaceConcept]:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            warnNumObs=30)

        #### Run High-Low Clustering ####
        gg = GG.GeneralG(ssdo, varName, wType, weightsFile=weightsFile,
                         concept=concept, rowStandard=rowStandard,
                         threshold=threshold, exponent=exponent,
                         numNeighs=numNeighs)

        #### Report and Set Parameters ####
        ggString, zgString, pvString = gg.report()
        try:
            parameters[8].value = ggString
            parameters[9].value = zgString
            parameters[10].value = pvString
        except:
            ARCPY.AddIDMessage("WARNING", 902)

        #### Create HTML Output ####
        if displayIt:
            htmlOutFile = gg.reportHTML(htmlFile=None)
            parameters[11].value = htmlOutFile
            # ARCPY.SetParameterAsText(11, htmlOutFile)
        return


class SpatialAutocorrelation(object):
    def __init__(self):
        self.label = "Spatial Autocorrelation (Morans I)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Analyzing Patterns"
        self.helpContext = 9010002
        self.params = None

        #### Set Lists of Spatial Concepts ####
        self.baseConcepts = ["INVERSE_DISTANCE",
                             "INVERSE_DISTANCE_SQUARED",
                             "FIXED_DISTANCE_BAND",
                             "ZONE_OF_INDIFFERENCE",
                             "K_NEAREST_NEIGHBORS",
                             "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.allConcepts = ["INVERSE_DISTANCE",
                            "INVERSE_DISTANCE_SQUARED",
                            "FIXED_DISTANCE_BAND",
                            "ZONE_OF_INDIFFERENCE",
                            "K_NEAREST_NEIGHBORS",
                            "CONTIGUITY_EDGES_ONLY",
                            "CONTIGUITY_EDGES_CORNERS",
                            "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.distanceConcepts = self.baseConcepts[0:4]
        self.currentConcepts = [i for i in self.baseConcepts]
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]
        self.rowTypes = ["ROW", "NONE"]

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Input Field",
                                 name="Input_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Generate Report",
                                 name="Generate_Report",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['GENERATE_REPORT', 'NO_REPORT']

        param3 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                 name="Conceptualization_of_Spatial_Relationships",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['INVERSE_DISTANCE', 'INVERSE_DISTANCE_SQUARED',
                              'FIXED_DISTANCE_BAND', 'ZONE_OF_INDIFFERENCE',
                              'K_NEAREST_NEIGHBORS',
                              'CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE']

        param3.value = 'INVERSE_DISTANCE'

        param4 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']

        param4.value = 'EUCLIDEAN_DISTANCE'

        param5 = ARCPY.Parameter(displayName="Standardization",
                                 name="Standardization",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"

        param5.filter.list = ['NONE', 'ROW']

        param5.value = 'ROW'

        param6 = ARCPY.Parameter(displayName="Distance Band or Threshold Distance",
                                 name="Distance_Band_or_Threshold_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0.0, 999999999999999.0]

        param7 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['swm', 'gwt', 'txt']
        param7.enabled = False

        param8 = ARCPY.Parameter(displayName="Index",
                                 name="Index",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param9 = ARCPY.Parameter(displayName="ZScore",
                                 name="ZScore",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param10 = ARCPY.Parameter(displayName="PValue",
                                  name="PValue",
                                  datatype="GPDouble",
                                  parameterType="Derived",
                                  direction="Output")

        param11 = ARCPY.Parameter(displayName="Report File",
                                  name="Report_File",
                                  datatype="DEFile",
                                  parameterType="Derived",
                                  direction="Output")
        # param11.filter.list = ['html'] #issue
        param11.enabled = False

        #### User Defined with Number of Neighbors Parameters (Required) ####
        param12 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param12.filter.type = "Range"
        param12.filter.list = [2, 1000]
        param12.enabled = False

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9, param10, param11, param12]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.checkContiguity(self.params[0].value)

        if self.params[4].altered:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in swapType:
                self.params[4].value = swapType[value4]

        #### Enable Type of Distance Measure if Appropriate ####
        if self.params[3].altered:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 == "POLYGON_CONTIGUITY_(FIRST_ORDER)":
                value3 = "CONTIGUITY_EDGES_ONLY"
                self.params[3].value = value3
            if value3 in self.distanceConcepts:
                self.params[4].enabled = 1
                self.params[6].enabled = 1
            else:
                self.params[4].enabled = 0
                self.params[6].enabled = 0

            if value3 == "GET_SPATIAL_WEIGHTS_FROM_FILE":
                self.params[7].enabled = 1
                self.params[5].enabled = 0
            else:
                self.params[7].enabled = 0
                self.params[5].enabled = 1

            if value3 == "K_NEAREST_NEIGHBORS":
                self.params[12].enabled = 1
                if not self.params[12].value:
                    self.params[12].value = 8
            else:
                clearParameter(self.params[12])

        return

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[3].hasError():
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in self.currentConcepts:
                self.params[3].clearMessage()
            if value3.count("CONTIGUITY"):
                self.params[3].clearMessage()

        #### Required SWM or KNN ####
        if self.params[3].value:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 == 'GET_SPATIAL_WEIGHTS_FROM_FILE':
                if self.params[7].value in ["", "#", None]:
                    self.params[7].setIDMessage("ERROR", 930)
            if value3 == "K_NEAREST_NEIGHBORS":
                if not self.params[12].value:
                    self.params[12].setIDMessage("ERROR", 976)

        if self.params[4].hasError():
            if self.params[4].value.upper().replace(" ", "_") in self.distanceTypes:
                self.params[4].clearMessage()

        if self.params[5].hasError():
            if self.params[5].value.upper() in self.rowTypes:
                self.params[5].clearMessage()
        return

    def checkContiguity(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            outSpatRef = setEnvSpatialReference(desc.SpatialReference)
            if outSpatRef.type.upper() == "GEOGRAPHIC":
                self.params[4].enabled = False
            else:
                self.params[4].enabled = True
            if desc.ShapeType.upper() == "POLYGON":
                self.params[3].filter.list = self.allConcepts
            else:
                self.params[3].filter.list = self.baseConcepts
        except:
            self.params[3].filter.list = self.baseConcepts
        self.currentConcepts = self.params[3].filter.list

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import MoransI as MI
        import SSUtilities as UTILS
        import WeightsUtilities as WU
        import SSDataObject as SSDO

        inputFC = UTILS.getTextParameter(0, parameters)
        varName = UTILS.getTextParameter(1, parameters).upper()
        displayIt = parameters[2].value

        #### Parse Space Concept ####
        spaceConcept = UTILS.getTextParameter(3, parameters).upper().replace(" ", "_")
        if spaceConcept == "INVERSE_DISTANCE_SQUARED":
            exponent = 2.0
        else:
            exponent = 1.0
        try:
            spaceConcept = WU.convertConcept[spaceConcept]
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = UTILS.getTextParameter(4, parameters).upper().replace(" ", "_")
        concept = WU.conceptDispatch[distanceConcept]

        #### Row Standardized ####
        rowStandard = UTILS.getTextParameter(5, parameters).upper()
        if rowStandard == 'ROW':
            rowStandard = True
        else:
            rowStandard = False

        #### Distance Threshold ####
        threshold = UTILS.getNumericParameter(6, parameters)

        #### Spatial Weights File ####
        weightsFile = UTILS.getTextParameter(7, parameters)
        if weightsFile is None and wType == 8:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and wType != 8:
            ARCPY.AddIDMessage("WARNING", 925)
            weightsFile = None

        #### Number of Neighbors ####
        numNeighs = UTILS.getNumericParameter(12, parameters)
        if numNeighs is None:
            numNeighs = 0

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, useChordal=True)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### Populate SSDO with Data ####
        if WU.gaTypes[spaceConcept]:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            warnNumObs=30)

        #### Run Spatial Autocorrelation ####
        gi = MI.GlobalI(ssdo, varName, wType, weightsFile=weightsFile,
                        concept=concept, rowStandard=rowStandard,
                        threshold=threshold, exponent=exponent,
                        numNeighs=numNeighs)

        #### Report and Set Parameters ####
        giString, ziString, pvString = gi.report()
        try:
            UTILS.setParameterAsText(8, giString, parameters)
            UTILS.setParameterAsText(9, ziString, parameters)
            UTILS.setParameterAsText(10, pvString, parameters)
        except:
            ARCPY.AddIDMessage("WARNING", 902)

        #### Create HTML Output ####
        if displayIt:
            htmlOutFile = gi.reportHTML(htmlFile=None)
            UTILS.setParameterAsText(11, htmlOutFile, parameters)
            return


class ClustersOutliers(object):
    def __init__(self):
        self.label = "Cluster and Outlier Analysis (Anselin Local Morans I)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030003
        #### Set Rendering Scheme Dict ####
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}

        #### Set Lists of Spatial Concepts ####
        self.baseConcepts = ["INVERSE_DISTANCE",
                             "INVERSE_DISTANCE_SQUARED",
                             "FIXED_DISTANCE_BAND",
                             "ZONE_OF_INDIFFERENCE",
                             "K_NEAREST_NEIGHBORS",
                             "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.allConcepts = ["INVERSE_DISTANCE",
                            "INVERSE_DISTANCE_SQUARED",
                            "FIXED_DISTANCE_BAND",
                            "ZONE_OF_INDIFFERENCE",
                            "K_NEAREST_NEIGHBORS",
                            "CONTIGUITY_EDGES_ONLY",
                            "CONTIGUITY_EDGES_CORNERS",
                            "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.distanceConcepts = self.baseConcepts[0:4]
        self.currentConcepts = [i for i in self.baseConcepts]
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]
        self.rowTypes = ["ROW", "NONE"]
        self.params = None
        self.ssdo = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Input Field",
                                 name="Input_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']
        param1.parameterDependencies = ["Input_Feature_Class"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")
        param2.displayOrder = 2

        param3 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                 name="Conceptualization_of_Spatial_Relationships",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "ValueList"
        param3.filter.list = ['INVERSE_DISTANCE', 'INVERSE_DISTANCE_SQUARED',
                              'FIXED_DISTANCE_BAND', 'ZONE_OF_INDIFFERENCE',
                              'K_NEAREST_NEIGHBORS',
                              'CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE']
        param3.value = 'INVERSE_DISTANCE'
        param3.displayOrder = 3

        param4 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"
        param4.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']
        param4.value = 'EUCLIDEAN_DISTANCE'
        param4.displayOrder = 4

        param5 = ARCPY.Parameter(displayName="Standardization",
                                 name="Standardization",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"
        param5.filter.list = ['NONE', 'ROW']
        param5.value = 'ROW'
        param5.displayOrder = 5

        param6 = ARCPY.Parameter(displayName="Distance Band or Threshold Distance",
                                 name="Distance_Band_or_Threshold_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0, 999999999999999]
        param6.displayOrder = 6

        param7 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['swm', 'gwt']
        param7.enabled = False
        param7.displayOrder = 7

        param8 = ARCPY.Parameter(displayName="Apply False Discovery Rate (FDR) Correction",
                                 name="Apply_False_Discovery_Rate__FDR__Correction",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['APPLY_FDR', 'NO_FDR']
        param8.value = False
        param8.displayOrder = 9

        param9 = ARCPY.Parameter(displayName="Index Field Name",
                                 name="Index_Field_Name",
                                 datatype="Field",
                                 parameterType="Derived",
                                 direction="Output")

        param9.value = 'LMiIndex'

        param10 = ARCPY.Parameter(displayName="ZScore Field Name",
                                  name="ZScore_Field_Name",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param10.value = 'LMiZScore'

        param11 = ARCPY.Parameter(displayName="Probability Field",
                                  name="Probability_Field",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param11.value = 'LMiPValue'

        param12 = ARCPY.Parameter(displayName="Cluster-Outlier Type",
                                  name="Cluster_Outlier_Type",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param12.value = 'CO_Type'

        param13 = ARCPY.Parameter(displayName="Source_ID",
                                  name="Source_ID",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param13.value = 'SOURCE_ID'

        param14 = ARCPY.Parameter(displayName="Number of Permutations",
                                  name="Number_of_Permutations",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param14.filter.list = [0, 99, 199, 499, 999, 9999]
        param14.value = 499
        param14.displayOrder = 10

        #### User Defined with Number of Neighbors Parameters (Required) ####
        param15 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param15.filter.type = "Range"
        param15.filter.list = [2, 1000]
        param15.enabled = False
        param15.displayOrder = 8

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9, param10, param11, param12,
                param13, param14, param15]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.ssdo = None
        self.fieldObjects = {}

        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.setParameterInfo(self.params[0].value)

        if self.params[0].altered or self.params[2].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                if self.params[2].value:
                    output = self.params[2].value.value
                else:
                    output = None
                outSpatRef = returnOutputSpatialRef(desc.SpatialReference,
                                                    output)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[4].enabled = False
                else:
                    self.params[4].enabled = True
            except:
                pass

        if self.params[4].altered:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in swapType:
                self.params[4].value = swapType[value4]

        #### Enable Type of Distance Measure if Appropriate ####
        if self.params[3].altered:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in swapType:
                self.params[3].value = swapType[value3]

            if value3 in self.distanceConcepts:
                self.params[4].enabled = 1
                self.params[6].enabled = 1
            else:
                self.params[4].enabled = 0
                self.params[6].enabled = 0

            if value3 == "GET_SPATIAL_WEIGHTS_FROM_FILE":
                self.params[7].enabled = 1
                self.params[5].enabled = 0
            else:
                self.params[7].enabled = 0
                self.params[5].enabled = 1

            if value3 == "K_NEAREST_NEIGHBORS":
                self.params[15].enabled = 1
                if not self.params[15].value:
                    self.params[15].value = 8
            else:
                clearParameter(self.params[15])

        #### Add Fields ####
        addFields = []

        #### Analysis Field ####
        if self.params[1].value:
            fieldName = self.params[1].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName].fieldObject)

        #### Add Master Field ####
        if self.params[0].value:
            if self.params[7].value and self.ssdo:
                try:
                    weightsFile = self.params[7].value.value
                    weightSuffix = weightsFile.split(".")[-1].lower()
                    swmFileBool = (weightSuffix == "swm")
                    masterField, sr = WU.returnHeader(self.ssdo, weightsFile,
                                                      swmFileBool=swmFileBool)
                    masterFieldObj = self.fieldObjects[masterField].fieldObject
                    addFields.append(masterFieldObj)
                except:
                    #### Weights Do Not Exist ####
                    pass
            else:
                masterFieldObj = ARCPY.Field()
                masterFieldObj.name = "SOURCE_ID"
                masterFieldObj.type = "LONG"
                addFields.append(masterFieldObj)

        #### Result Fields ####
        fieldNames = ["LMiIndex", "LMiZScore", "LMiPValue", "COType"]

        for fieldInd, fieldName in enumerate(fieldNames):
            newField = ARCPY.Field()
            newField.name = fieldName
            if fieldName == "COType":
                newField.type = "TEXT"
                newField.length = 2
            else:
                newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[2].schema.additionalFields = addFields

        return

    def updateMessages(self, parameters):
        self.params = parameters

        if self.params[4].value:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in swapType:
                self.params[4].value = swapType[value4]

        if self.params[3].value:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in swapType:
                self.params[3].value = swapType[value3]

        if self.params[3].value:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in self.currentConcepts:
                self.params[3].clearMessage()
            if value3.count("CONTIGUITY"):
                self.params[3].clearMessage()

            #### Required SWM ####
            if value3 == 'GET_SPATIAL_WEIGHTS_FROM_FILE':
                if self.params[7].value in ["", "#", None]:
                    self.params[7].setIDMessage("ERROR", 930)

            #### Require KNN ####
            if value3 == "K_NEAREST_NEIGHBORS":
                if not self.params[15].value:
                    self.params[15].setIDMessage("ERROR", 976)

        if self.params[4].value:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in self.distanceTypes:
                self.params[4].clearMessage()

        if self.params[5].hasError():
            if self.params[5].value.upper() in self.rowTypes:
                self.params[5].clearMessage()
        return

    def setParameterInfo(self, inputFC):
        try:
            self.ssdo = SSDO.SSDataObject(inputFC)
            shapeType = self.ssdo.shapeType.upper()
            self.oidName = self.ssdo.oidName
            if shapeType == "POLYGON":
                self.params[3].filter.list = self.allConcepts
            else:
                self.params[3].filter.list = self.baseConcepts
            self.setOutputSymbology(shapeType)
            self.fieldObjects = self.ssdo.allFields
            self.currentConcepts = self.params[3].filter.list
        except:
            pass

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        if renderOut == 0:
            renderLayerFile = "LocalIPoints.lyr"
        elif renderOut == 1:
            renderLayerFile = "LocalIPolylines.lyr"
        else:
            renderLayerFile = "LocalIPolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[2].symbology = fullRLF

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import LocalMoran as LM
        import WeightsUtilities as WU

        inputFC = UTILS.getTextParameter(0, parameters)
        varName = UTILS.getTextParameter(1, parameters).upper()
        outputFC = UTILS.getTextParameter(2, parameters)

        #### Parse Space Concept ####
        spaceConcept = UTILS.getTextParameter(3, parameters).upper().replace(" ", "_")
        if spaceConcept == "INVERSE_DISTANCE_SQUARED":
            exponent = 2.0
        else:
            exponent = 1.0
        try:
            spaceConcept = WU.convertConcept[spaceConcept]
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = UTILS.getTextParameter(4, parameters).upper().replace(" ", "_")
        concept = WU.conceptDispatch[distanceConcept]

        #### Row Standardized ####
        rowStandard = UTILS.getTextParameter(5, parameters).upper()
        if rowStandard == 'ROW':
            rowStandard = True
        else:
            rowStandard = False

        #### Distance Threshold ####
        threshold = UTILS.getNumericParameter(6, parameters)

        #### Spatial Weights File ####
        weightsFile = UTILS.getTextParameter(7, parameters)
        if weightsFile is None and wType == 8:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and wType != 8:
            ARCPY.AddIDMessage("WARNING", 925)
            weightsFile = None

        #### Number of Neighbors ####
        numNeighs = UTILS.getNumericParameter(15, parameters)
        if numNeighs is None:
            numNeighs = 0

        #### FDR ####
        applyFDR = parameters[8].value

        #### Permutations ####
        permutations = UTILS.getNumericParameter(14, parameters)

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=True)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### Populate SSDO with Data ####
        if WU.gaTypes[spaceConcept]:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, [varName], minNumObs=3,
                            warnNumObs=30)

        #### Run Cluster-Outlier Analysis ####
        li = LM.LocalI(ssdo, varName, outputFC, wType,
                       weightsFile=weightsFile, concept=concept,
                       rowStandard=rowStandard, threshold=threshold,
                       exponent=exponent, numNeighs=numNeighs,
                       applyFDR=applyFDR, permutations=permutations)

        #### Report and Set Parameters ####
        liField, ziField, pvField, coField = li.outputResults()
        try:
            UTILS.setParameterAsText(9, liField, parameters)
            UTILS.setParameterAsText(10, ziField, parameters)
            UTILS.setParameterAsText(11, pvField, parameters)
            UTILS.setParameterAsText(12, coField, parameters)
            UTILS.setParameterAsText(13, li.ssdo.masterField, parameters)
        except:
            ARCPY.AddIDMessage("WARNING", 902)

        li.renderResults(parameters)
        return


class HotSpots(object):
    def __init__(self):
        self.label = "Hot Spot Analysis (Getis-Ord Gi*)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030001
        #### Set Rendering Scheme Dict ####
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}

        #### Set Lists of Spatial Concepts ####
        self.baseConcepts = ["INVERSE_DISTANCE",
                             "INVERSE_DISTANCE_SQUARED",
                             "FIXED_DISTANCE_BAND",
                             "ZONE_OF_INDIFFERENCE",
                             "K_NEAREST_NEIGHBORS",
                             "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.allConcepts = ["INVERSE_DISTANCE",
                            "INVERSE_DISTANCE_SQUARED",
                            "FIXED_DISTANCE_BAND",
                            "ZONE_OF_INDIFFERENCE",
                            "K_NEAREST_NEIGHBORS",
                            "CONTIGUITY_EDGES_ONLY",
                            "CONTIGUITY_EDGES_CORNERS",
                            "GET_SPATIAL_WEIGHTS_FROM_FILE"]

        self.distanceConcepts = self.baseConcepts[0:4]
        self.currentConcepts = [i for i in self.baseConcepts]
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]
        self.rowTypes = ["ROW", "NONE"]
        self.params = None
        self.fieldObjects = {}
        self.ssdo = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Input Field",
                                 name="Input_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']
        param1.parameterDependencies = ["Input_Feature_Class"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2.parameterDependencies = ["Input_Feature_Class"]
        param2.displayOrder = 2

        param3 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                 name="Conceptualization_of_Spatial_Relationships",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "ValueList"
        param3.filter.list = ['INVERSE_DISTANCE', 'INVERSE_DISTANCE_SQUARED',
                              'FIXED_DISTANCE_BAND', 'ZONE_OF_INDIFFERENCE',
                              'K_NEAREST_NEIGHBORS',
                              'CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE']
        param3.value = 'FIXED_DISTANCE_BAND'
        param3.displayOrder = 3

        param4 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"
        param4.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']
        param4.value = 'EUCLIDEAN_DISTANCE'
        param4.displayOrder = 4

        param5 = ARCPY.Parameter(displayName="Standardization",
                                 name="Standardization",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"
        param5.filter.list = ['NONE', 'ROW']
        param5.value = 'ROW'
        param5.enabled = False
        param5.displayOrder = 5

        param6 = ARCPY.Parameter(displayName="Distance Band or Threshold Distance",
                                 name="Distance_Band_or_Threshold_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0, 999999999999999]
        param6.displayOrder = 6

        param7 = ARCPY.Parameter(displayName="Self Potential Field",
                                 name="Self_Potential_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['Short', 'Long', 'Float', 'Double']
        param7.parameterDependencies = ["Input_Feature_Class"]
        param7.displayOrder = 7

        param8 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['swm', 'gwt']
        param8.enabled = False
        param8.displayOrder = 8

        param9 = ARCPY.Parameter(displayName="Apply False Discovery Rate (FDR) Correction",
                                 name="Apply_False_Discovery_Rate__FDR__Correction",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param9.filter.list = ['APPLY_FDR', 'NO_FDR']
        param9.value = False
        param9.displayOrder = 10

        param10 = ARCPY.Parameter(displayName="Results Field",
                                  name="Results_Field",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param10.value = 'GiZScore'

        param11 = ARCPY.Parameter(displayName="Probability Field",
                                  name="Probability_Field",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param11.value = 'GiPValue'

        param12 = ARCPY.Parameter(displayName="Source_ID",
                                  name="Source_ID",
                                  datatype="Field",
                                  parameterType="Derived",
                                  direction="Output")

        param12.value = 'SOURCE_ID'

        #### User Defined with Number of Neighbors Parameters (Required) ####
        param13 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param13.filter.type = "Range"
        param13.filter.list = [2, 1000]
        param13.enabled = False
        param13.displayOrder = 9

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9, param10, param11, param12, param13]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        self.ssdo = None
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.setParameterInfo(self.params[0].value)

        if self.params[0].altered or self.params[2].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                if self.params[2].value:
                    output = self.params[2].value.value
                else:
                    output = None
                outSpatRef = returnOutputSpatialRef(desc.SpatialReference,
                                                    output)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[4].enabled = False
                else:
                    self.params[4].enabled = True
            except:
                pass

        if self.params[3].altered:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in swapType:
                self.params[3].value = swapType[value3]

        if self.params[4].altered:
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in swapType:
                self.params[4].value = swapType[value4]

        #### Enable Type of Distance Measure if Appropriate ####
        if self.params[3].altered:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in self.distanceConcepts:
                self.params[4].enabled = 1
                self.params[6].enabled = 1
            else:
                self.params[4].enabled = 0
                self.params[6].enabled = 0

            if value3 == "GET_SPATIAL_WEIGHTS_FROM_FILE":
                self.params[8].enabled = 1
            else:
                self.params[8].enabled = 0

            if value3 == "K_NEAREST_NEIGHBORS":
                self.params[13].enabled = 1
                if not self.params[13].value:
                    self.params[13].value = 8
            else:
                clearParameter(self.params[13])

        #### Add Fields ####
        addFields = []

        #### Analysis Field ####
        if self.params[1].value:
            fieldName = self.params[1].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName].fieldObject)

        #### Potential Field ####
        if self.params[7].value:
            fieldName = self.params[7].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName].fieldObject)

        #### Add Master Field ####
        if self.params[0].value:
            if self.params[8].value and self.ssdo:
                try:
                    weightsFile = self.params[8].value.value
                    weightSuffix = weightsFile.split(".")[-1].lower()
                    swmFileBool = (weightSuffix == "swm")
                    masterField, sr = WU.returnHeader(self.ssdo, weightsFile,
                                                      swmFileBool=swmFileBool)
                    masterFieldObj = self.fieldObjects[masterField].fieldObject
                    addFields.append(masterFieldObj)
                except:
                    #### Weights Do Not Exist ####
                    pass
            else:
                masterFieldObj = ARCPY.Field()
                masterFieldObj.name = "SOURCE_ID"
                masterFieldObj.type = "LONG"
                addFields.append(masterFieldObj)

        #### Result Fields ####
        fieldNames = ["GiZScore", "GiPValue", "Gi_Bin"]
        fieldTypes = ["DOUBLE", "DOUBLE", "LONG"]

        for fieldInd, fieldName in enumerate(fieldNames):
            fieldType = fieldTypes[fieldInd]
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = fieldType
            addFields.append(newField)
        self.params[2].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[3].hasError():
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 in self.currentConcepts:
                self.params[3].clearMessage()
            if value3.count("CONTIGUITY"):
                self.params[3].clearMessage()

        #### Required SWM or KNN ####
        if self.params[3].value:
            value3 = self.params[3].value.upper().replace(" ", "_")
            if value3 == 'GET_SPATIAL_WEIGHTS_FROM_FILE':
                if self.params[8].value in ["", "#", None]:
                    self.params[8].setIDMessage("ERROR", 930)
            #### Require KNN ####
            if value3 == "K_NEAREST_NEIGHBORS":
                if not self.params[13].value:
                    self.params[13].setIDMessage("ERROR", 976)

        if self.params[4].hasError():
            value4 = self.params[4].value.upper().replace(" ", "_")
            if value4 in self.distanceTypes:
                self.params[4].clearMessage()

        if self.params[5].hasError():
            if self.params[5].value.upper() in self.rowTypes:
                self.params[5].clearMessage()

    def setParameterInfo(self, inputFC):
        try:
            self.ssdo = SSDO.SSDataObject(inputFC)
            shapeType = self.ssdo.shapeType.upper()
            self.oidName = self.ssdo.oidName
            if shapeType == "POLYGON":
                self.params[3].filter.list = self.allConcepts
            else:
                self.params[3].filter.list = self.baseConcepts
            self.setOutputSymbology(shapeType)
            self.fieldObjects = self.ssdo.allFields
            self.currentConcepts = self.params[3].filter.list
        except:
            pass

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        if renderOut == 0:
            renderLayerFile = "LocalGPoints.lyr"
        elif renderOut == 1:
            renderLayerFile = "LocalGPolylines.lyr"
        else:
            renderLayerFile = "LocalGPolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[2].symbology = fullRLF

    def execute(self, parameters, messages):

        inputFC = UTILS.getTextParameter(0, parameters)
        varName = UTILS.getTextParameter(1, parameters).upper()
        varNameList = [varName]
        outputFC = UTILS.getTextParameter(2, parameters)

        #### Parse Space Concept ####
        spaceConcept = UTILS.getTextParameter(3, parameters).upper().replace(" ", "_")
        if spaceConcept == "INVERSE_DISTANCE_SQUARED":
            exponent = 2.0
        else:
            exponent = 1.0
        try:
            spaceConcept = WU.convertConcept[spaceConcept]
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("ERROR", 723)
            raise SystemExit()

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = UTILS.getTextParameter(4, parameters).upper().replace(" ", "_")
        concept = WU.conceptDispatch[distanceConcept]

        #### Row Standardized Not Used in Hot Spot Analysis ####
        #### Results Are Identical With or Without ####
        #### Remains in UI for Backwards Compatibility ####
        rowStandard = UTILS.getTextParameter(5, parameters).upper()

        #### Distance Threshold ####
        threshold = UTILS.getNumericParameter(6, parameters)

        #### Self Potential Field ####
        potentialField = UTILS.getTextParameter(7, parameters, fieldName=True)
        if potentialField:
            varNameList.append(potentialField)

        #### Spatial Weights File ####
        weightsFile = UTILS.getTextParameter(8, parameters)
        if weightsFile is None and wType == 8:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and wType != 8:
            ARCPY.AddIDMessage("WARNING", 925)
            weightsFile = None

        #### Number of Neighbors ####
        numNeighs = UTILS.getNumericParameter(13, parameters)
        if numNeighs is None:
            numNeighs = 0

        #### FDR ####
        applyFDR = parameters[9].value

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=True)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### Populate SSDO with Data ####
        if WU.gaTypes[spaceConcept]:
            ssdo.obtainData(masterField, varNameList, minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, varNameList, minNumObs=3,
                            warnNumObs=30)

        import Gi as GI
        import warnings as WARNINGS
        #### Report and Set Parameters ####
        with WARNINGS.catch_warnings():
            WARNINGS.simplefilter("ignore")
            #### Run Hot-Spot Analysis ####
            gi = GI.LocalG(ssdo, varName, outputFC, wType, weightsFile=weightsFile,
                           concept=concept, threshold=threshold,
                           exponent=exponent, numNeighs=numNeighs,
                           potentialField=potentialField, applyFDR=applyFDR)

            giField, pvField = gi.outputResults()
            try:
                UTILS.setParameterAsText(10, giField, parameters)
                UTILS.setParameterAsText(11, pvField, parameters)
                UTILS.setParameterAsText(12, gi.ssdo.masterField, parameters)
            except:
                ARCPY.AddIDMessage("WARNING", 902)
            gi.renderResults(parameters)


class CentralFeature(object):
    def __init__(self):
        self.label = "Central Feature"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040001
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]

        #### Set Rendering Scheme Dict ####
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']

        param2.value = 'EUCLIDEAN_DISTANCE'

        param3 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Float', 'Double']
        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Self Potential Weight Field",
                                 name="Self_Potential_Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Short', 'Long', 'Float', 'Double']
        param4.parameterDependencies = ["Input_Feature_Class"]

        param5 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param5.filter.list = ['Short', 'Long', 'Text', 'Date']
        param5.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3, param4, param5]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}

        if self.params[2].altered:
            value2 = self.params[2].value.upper().replace(" ", "_")
            if value2 in swapType:
                self.params[2].value = swapType[value2]

        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                    shapeType = desc.ShapeType.upper()
                    self.setOutputSymbology(shapeType)
                except:
                    pass
            else:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    pass

        #### Add Fields ####
        addFields = []

        #### Weight Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Potential Field ####
        if self.params[4].value:
            fieldName = self.params[4].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Case Field ####
        if self.params[5].value:
            fieldName = self.params[5].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        self.params[1].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[2].hasError():
            if self.params[2].value.upper().replace(" ", "_") in self.distanceTypes:
                self.params[2].clearMessage()

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        if renderOut == 0:
            renderLayerFile = "CentralFeaturePoints.lyr"
        elif renderOut == 1:
            renderLayerFile = "CentralFeaturePolylines.lyr"
        else:
            renderLayerFile = "CentralFeaturePolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[1].symbology = fullRLF

    def execute(self, parameters, messages):
        import CentralFeature as CF

        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        distanceMethod = UTILS.getTextParameter(2, parameters).upper().replace(" ", "_")
        weightField = UTILS.getTextParameter(3, parameters, fieldName=True)
        potentialField = UTILS.getTextParameter(4, parameters, fieldName=True)
        caseField = UTILS.getTextParameter(5, parameters, fieldName=True)

        distanceMethod = distanceMethod.split("_")[0]
        fieldList = []
        if weightField:
            fieldList.append(weightField)

        if potentialField:
            fieldList.append(potentialField)

        if caseField:
            fieldList.append(caseField)

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=1,
                        requireGeometry=ssdo.complexFeature)

        #### Run Analysis ####
        cf = CF.CentralFeature(ssdo, distanceMethod=distanceMethod,
                               weightField=weightField,
                               potentialField=potentialField,
                               caseField=caseField)

        #### Create Output ####
        cf.createOutput(outputFC, parameters)


class DirectionalMean(object):
    def __init__(self):
        self.label = "Linear Directional Mean"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040003
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Polyline']

        param1 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Orientation Only",
                                 name="Orientation_Only",
                                 datatype="GPBoolean",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.list = ['ORIENTATION_ONLY', 'DIRECTION']
        param2.value = False
        param3 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Text', 'Date']
        param3.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            # if not self.params[0].isInputValueDerived():
            try:
                desc = ARCPY.Describe(self.params[0].value)
                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                pass

        #### Reset Symbology ####
        if not self.params[2].hasBeenValidated:
            self.setOutputSymbology()

        #### Add Fields ####
        addFields = []

        #### Case Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["CompassA", "DirMean", "CirVar", "AveX", "AveY", "AveLen"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        return

    def setOutputSymbology(self):
        """Sets Output FC Symbology."""

        value2 = self.params[2].value
        if value2:
            renderLayerFile = "LinearMeanTwoWay.lyr"
        else:
            renderLayerFile = "LinearMeanOneWay.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[1].symbology = fullRLF

    def execute(self, parameters, messages):
        import DirectionalMean as DIRMEAN
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        orientationOnly = parameters[2].value
        caseField = UTILS.getTextParameter(3, parameters, fieldName=True)
        dm = DIRMEAN.DirectionalMean(inputFC, outputFC=outputFC, caseField=caseField,
                                     orientationOnly=orientationOnly)
        dm.createOutput(outputFC, parameters)


class CalculateAreas(object):
    def __init__(self):
        self.label = "Calculate Areas"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Utilities"
        self.helpContext = 9050006

    def getParameterInfo(self):
        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Polygon']

        param1 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param1.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        return


class ExportXYv(object):
    def __init__(self):
        self.label = "Export Feature Attribute to ASCII"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Utilities"
        self.helpContext = 9050007
        self.delimTypes = ["SPACE", "COMMA", "SEMI-COLON"]

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Value Field",
                                 name="Value_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param1.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param1.filter.list = ['Short', 'Long', 'Float', 'Double', 'Text', 'Date', 'OID', 'GlobalID']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Delimiter",
                                 name="Delimiter",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['SPACE', 'COMMA', 'SEMI-COLON']

        param2.value = 'SPACE'

        param3 = ARCPY.Parameter(displayName="Output ASCII File",
                                 name="Output_ASCII_File",
                                 datatype="DEFile",
                                 parameterType="Required",
                                 direction="Output")

        param4 = ARCPY.Parameter(displayName="Add Field Names to Output",
                                 name="Add_Field_Names_to_Output",
                                 datatype="GPBoolean",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.list = ['ADD_FIELD_NAMES', 'NO_FIELD_NAMES']
        param4.value = False
        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[2].hasError():
            if self.params[2].value.upper().replace(" ", "_") in self.delimTypes:
                self.params[2].clearMessage()

        if self.params[3].altered:
            if self.params[3].value:
                #### Check Path to Output Exists ####
                outPath, outName = OS.path.split(self.params[3].value.value)
                if not OS.path.exists(outPath):
                    self.params[3].setIDMessage("ERROR", 436, outPath)

    def execute(self, parameters, messages):
        import ExportXYV as EXYV
        #### Get User Provided Inputs ####
        inputFC = UTILS.getTextParameter(0, parameters)
        outFields = UTILS.getTextParameter(1, parameters).upper()
        fieldList = outFields.split(";")
        delimiter = UTILS.getTextParameter(2, parameters).upper().replace(" ", "_")
        outFile = UTILS.getTextParameter(3, parameters)
        outFieldNames = parameters[4].value
        delimDict = {"SPACE": " ", "COMMA": ",", "SEMI-COLON": ";"}
        #### Set Delimiter ####
        try:
            delimiter = delimDict[delimiter]
        except:
            delimiter = " "

        #### Execute Function ####
        EXYV.exportXYV(inputFC, fieldList, delimiter, outFile,
                       outFieldNames=outFieldNames)


class MultiDistanceSpatialClustering(object):
    def __init__(self):
        self.label = "Multi-Distance Spatial Cluster Analysis (Ripleys K Function)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Analyzing Patterns"
        self.helpContext = 9010003
        self.params = None

        self.regularFields = ["ExpectedK", "ObservedK", "DiffK"]
        self.allFields = self.regularFields + ["LwConfEnv", "HiConfEnv"]

        #### Upper Param Lists ####
        self.permTypes = ["0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE",
                          "9_PERMUTATIONS", "99_PERMUTATIONS",
                          "999_PERMUTATIONS"]
        self.correctTypes = ["NONE", "SIMULATE_OUTER_BOUNDARY_VALUES",
                             "REDUCE_ANALYSIS_AREA",
                             "RIPLEY_EDGE_CORRECTION_FORMULA"]
        self.studyAreaTypes = ["MINIMUM_ENCLOSING_RECTANGLE",
                               "USER_PROVIDED_STUDY_AREA_FEATURE_CLASS"]

        self.canMakeGraph = canMakeGraph()

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Table",
                                 name="Output_Table",
                                 datatype="DETable",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Number of Distance Bands",
                                 name="Number_of_Distance_Bands",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "Range"

        param2.filter.list = [1, 100]

        param2.value = 10

        param3 = ARCPY.Parameter(displayName="Compute Confidence Envelope",
                                 name="Compute_Confidence_Envelope",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE', '9_PERMUTATIONS', '99_PERMUTATIONS',
                              '999_PERMUTATIONS']

        param3.value = '0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE'

        param4 = ARCPY.Parameter(displayName="Display Results Graphically",
                                 name="Display_Results_Graphically",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['DISPLAY_IT', 'NO_DISPLAY']

        if not self.canMakeGraph:
            param4.enabled = False

        param5 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param5.filter.list = ['Short', 'Long', 'Float', 'Double']
        param5.parameterDependencies = ["Input_Feature_Class"]

        param6 = ARCPY.Parameter(displayName="Beginning Distance",
                                 name="Beginning_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0.0, 9999999.0]

        param7 = ARCPY.Parameter(displayName="Distance Increment",
                                 name="Distance_Increment",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.type = "Range"
        param7.filter.list = [0.0, 9999999.0]

        param8 = ARCPY.Parameter(displayName="Boundary Correction Method",
                                 name="Boundary_Correction_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param8.filter.type = "ValueList"

        param8.filter.list = ['NONE', 'SIMULATE_OUTER_BOUNDARY_VALUES', 'REDUCE_ANALYSIS_AREA',
                              'RIPLEY_EDGE_CORRECTION_FORMULA']

        param8.value = 'NONE'

        param9 = ARCPY.Parameter(displayName="Study Area Method",
                                 name="Study_Area_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param9.filter.type = "ValueList"

        param9.filter.list = ['MINIMUM_ENCLOSING_RECTANGLE', 'USER_PROVIDED_STUDY_AREA_FEATURE_CLASS']

        param9.value = 'MINIMUM_ENCLOSING_RECTANGLE'

        param10 = ARCPY.Parameter(displayName="Study Area Feature Class",
                                  name="Study_Area_Feature_Class",
                                  datatype="GPFeatureLayer",
                                  parameterType="Optional",
                                  direction="Input")

        param10.enabled = False

        param11 = ARCPY.Parameter(displayName="Result Image",
                                  name="Result_Image",
                                  datatype="GPGraph",
                                  parameterType="Derived",
                                  direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        studyArea = "USER_PROVIDED_STUDY_AREA_FEATURE_CLASS"
        if self.params[9].value == studyArea:
            self.params[10].enabled = 1
        else:
            self.params[10].enabled = 0

        #### Set Output Table Schema For Graphics ####
        if self.params[1].value != None:
            addFields = []
            if self.params[3].value == "0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE":
                fieldNames = self.regularFields
            else:
                fieldNames = self.allFields
            for fieldName in fieldNames:
                newField = ARCPY.Field()
                newField.name = fieldName
                newField.type = "DOUBLE"
                addFields.append(newField)
            self.params[1].schema.additionalFields = addFields
        return

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[0].value:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                outSpatRef = setEnvSpatialReference(desc.SpatialReference)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[0].setIDMessage("ERROR", 1606)
            except:
                pass

        if self.params[3].hasError():
            if self.params[3].value.upper().replace(" ", "_") in self.permTypes:
                self.params[3].clearMessage()

        if self.params[8].hasError():
            value8 = self.params[8].value.upper().replace(" ", "_")
            if value8 in self.correctTypes:
                self.params[8].clearMessage()
            if value8.split("_")[-1] == "FORMULA":
                self.params[8].clearMessage()

        if self.params[9].hasError():
            if self.params[9].value.upper().replace(" ", "_") in self.studyAreaTypes:
                self.params[9].clearMessage()

        if not self.canMakeGraph and self.params[4].value:
            self.params[4].setIDMessage("WARNING", 110038)
        return

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import SSUtilities as UTILS
        import KFunction as KF

        inputFC = UTILS.getTextParameter(0, parameters)
        outputTable = UTILS.getTextParameter(1, parameters)
        nIncrements = parameters[2].value
        permutations = UTILS.getTextParameter(3, parameters).upper().replace(" ", "_")
        displayIt = parameters[4].value
        weightField = UTILS.getTextParameter(5, parameters, fieldName=True)
        begDist = UTILS.getNumericParameter(6, parameters)
        dIncrement = UTILS.getNumericParameter(7, parameters)
        edgeCorrection = UTILS.getTextParameter(8, parameters).upper().replace(" ", "_")
        studyAreaMethod = UTILS.getTextParameter(9, parameters).upper().replace(" ", "_")
        studyAreaFC = UTILS.getTextParameter(10, parameters)

        #### Resolve Table Extension ####
        if ".dbf" not in OS.path.basename(outputTable):
            dirInfo = ARCPY.Describe(OS.path.dirname(outputTable))
            if dirInfo == "FileSystem":
                outputTable = outputTable + ".dbf"

        #### Resolve Remaining Parameters ####
        if nIncrements > 100:
            nIncrements = 100

        if edgeCorrection == "NONE" or edgeCorrection == "#":
            edgeCorrection = None
        elif edgeCorrection == "SIMULATE_OUTER_BOUNDARY_VALUES":
            edgeCorrection = "Simulate"
        elif edgeCorrection == "REDUCE_ANALYSIS_AREA":
            edgeCorrection = "Reduce"
        else:
            edgeCorrection = "Ripley"

        if permutations == "0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE":
            permutations = 0
        elif permutations == "99_PERMUTATIONS":
            permutations = 99
        elif permutations == "999_PERMUTATIONS":
            permutations = 999
        else:
            permutations = 9

        if studyAreaMethod == "USER_PROVIDED_STUDY_AREA_FEATURE_CLASS":
            studyAreaMethod = 1
        else:
            studyAreaMethod = 0

        k = KF.KFunction(inputFC, outputTable=outputTable,
                         nIncrements=nIncrements, permutations=permutations,
                         weightField=weightField, begDist=begDist,
                         dIncrement=dIncrement, edgeCorrection=edgeCorrection,
                         studyAreaMethod=studyAreaMethod, studyAreaFC=studyAreaFC)

        k.report()
        k.createOutput(outputTable, displayIt=displayIt, parameters=parameters)

        return


class CalculateDistanceBand(object):
    def __init__(self):
        self.label = "Calculate Distance Band from Neighbor Count"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Utilities"
        self.helpContext = 9050008
        self.params = None
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Neighbors",
                                 name="Neighbors",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.type = "Range"
        param1.filter.list = [1, 9999]
        param1.value = 1

        param2 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']

        param2.value = 'EUCLIDEAN_DISTANCE'

        param3 = ARCPY.Parameter(displayName="Minimum Distance",
                                 name="Minimum_Distance",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param4 = ARCPY.Parameter(displayName="Average Distance",
                                 name="Average_Distance",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param5 = ARCPY.Parameter(displayName="Maximum Distance",
                                 name="Maximum_Distance",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        return [param0, param1, param2, param3, param4, param5]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters

        if self.params[2].altered:
            value2 = self.params[2].value.upper().replace(" ", "_")
            if value2 in swapType:
                self.params[2].value = swapType[value2]

        if self.params[0].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                outSpatRef = setEnvSpatialReference(desc.SpatialReference)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[2].enabled = False
                else:
                    self.params[2].enabled = True
            except:
                pass

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[2].hasError():
            if self.params[2].value.upper().replace(" ", "_") in self.distanceTypes:
                self.params[2].clearMessage()

    def execute(self, parameters, messages):
        import CalculateDistanceBand as CDB
        inputFC = UTILS.getTextParameter(0, parameters)
        kNeighs = UTILS.getNumericParameter(1, parameters)
        if not kNeighs:
            kNeighs = 0

        distanceConcept = UTILS.getTextParameter(2, parameters).upper().replace(" ", "_")
        concept = distanceConcept.split("_")[0]
        cdb = CDB.calculateDistanceBand(inputFC, kNeighs, concept)


class AverageNearestNeighbor(object):
    def __init__(self):
        self.label = "Average Nearest Neighbor"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Analyzing Patterns"
        self.helpContext = 9010004
        self.distanceTypes = ["EUCLIDEAN_DISTANCE", "MANHATTAN_DISTANCE"]
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.type = "ValueList"
        param1.filter.list = ['EUCLIDEAN_DISTANCE', 'MANHATTAN_DISTANCE']
        param1.value = 'EUCLIDEAN_DISTANCE'

        param2 = ARCPY.Parameter(displayName="Generate Report",
                                 name="Generate_Report",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['GENERATE_REPORT', 'NO_REPORT']
        param2.value = False

        param3 = ARCPY.Parameter(displayName="Area",
                                 name="Area",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.type = "Range"
        param3.filter.list = [0.0, 999999999999999.0]

        param4 = ARCPY.Parameter(displayName="NNRatio",
                                 name="NNRatio",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")
        param4.value = 0
        param5 = ARCPY.Parameter(displayName="NNZScore",
                                 name="NNZScore",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")
        param5.value = 0
        param6 = ARCPY.Parameter(displayName="PValue",
                                 name="PValue",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")
        param6.value = 0
        param7 = ARCPY.Parameter(displayName="NNExpected",
                                 name="NNExpected",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")
        param7.value = 0
        param8 = ARCPY.Parameter(displayName="NNObserved",
                                 name="NNObserved",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")
        param8.value = 0
        param9 = ARCPY.Parameter(displayName="Report File",
                                 name="Report_File",
                                 datatype="DEFile",
                                 parameterType="Derived",
                                 direction="Output")
        # param9.filter.list = ['html'] #issue
        param9.enabled = False

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        if self.params[0].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                outSpatRef = setEnvSpatialReference(desc.SpatialReference)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[1].enabled = False
                else:
                    self.params[1].enabled = True
            except:
                pass

        if self.params[1].altered:
            value1 = self.params[1].value.upper().replace(" ", "_")
            if value1 in swapType:
                self.params[1].value = swapType[value1]

        if not self.params[1].value:
            self.params[1].value = "EUCLIDEAN_DISTANCE"

        return

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[1].hasError():
            if self.params[1].value.upper().replace(" ", "_") in self.distanceTypes:
                self.params[1].clearMessage()
        return

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import SSDataObject as SSDO
        import WeightsUtilities as WU
        import NearestNeighbor as NN

        inputFC = UTILS.getTextParameter(0, parameters)
        distanceConcept = UTILS.getTextParameter(1, parameters).upper().replace(" ", "_")
        displayIt = parameters[2].value
        studyArea = UTILS.getNumericParameter(3, parameters)
        concept = WU.conceptDispatch[distanceConcept]

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, useChordal=True)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, minNumObs=2,
                        requireSearch=True)

        #### Calculate ####
        nn = NN.NearestNeighbor(ssdo, concept=concept, studyArea=studyArea)

        #### Report and Set Parameters ####
        nn.report()

        try:
            UTILS.setParameterAsText(4, nn.ratioString, parameters)
            UTILS.setParameterAsText(5, nn.znString, parameters)
            UTILS.setParameterAsText(6, nn.pvString, parameters)
            UTILS.setParameterAsText(7, nn.enString, parameters)
            UTILS.setParameterAsText(8, nn.nnString, parameters)
        except:
            ARCPY.AddIDMessage("WARNING", 902)

        #### Create HTML Output ####
        if displayIt:
            htmlOutFile = nn.reportHTML(htmlFile=None)
            UTILS.setParameterAsText(9, htmlOutFile, parameters)

        return


class DirectionalDistribution(object):
    def __init__(self):
        self.label = "Directional Distribution (Standard Deviational Ellipse)"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040004
        self.circTypes = {"1_STANDARD_DEVIATION": 1, "2_STANDARD_DEVIATIONS": 2,
                          "3_STANDARD_DEVIATIONS": 3}
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Ellipse Feature Class",
                                 name="Output_Ellipse_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Ellipse Size",
                                 name="Ellipse_Size",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['1_STANDARD_DEVIATION', '2_STANDARD_DEVIATIONS', '3_STANDARD_DEVIATIONS']

        param2.value = '1_STANDARD_DEVIATION'

        param3 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Float', 'Double']
        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Short', 'Long', 'Text', 'Date']
        param4.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            # if not self.params[0].isInputValueDerived():
            try:
                desc = ARCPY.Describe(self.params[0].value)
                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                pass

        if not self.params[2].value:
            self.params[2].value = "1_STANDARD_DEVIATION"

        #### Add Fields ####
        addFields = []

        #### Weight Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Case Field ####
        if self.params[4].value:
            fieldName = self.params[4].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["CenterX", "CenterY", "XStdDist", "YStdDist", "Rotation"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields

        #### Set Symbology ####
        renderLayerFile = "StandardDeviationalEllipse.lyr"
        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[1].symbology = fullRLF

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[2].hasError():
            if self.params[2].value.upper().replace(" ", "_") in self.circTypes:
                self.params[2].clearMessage()

    def execute(self, parameters, messages):
        import StandardEllipse as SE

        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        stdDeviations = UTILS.getTextParameter(2, parameters).upper().replace(" ", "_")
        weightField = UTILS.getTextParameter(3, parameters, fieldName=True)
        caseField = UTILS.getTextParameter(4, parameters, fieldName=True)

        fieldList = []
        if weightField:
            fieldList.append(weightField)
        if caseField:
            fieldList.append(caseField)

        #### Get Standard deviation value ####
        stdDeviations = self.circTypes[stdDeviations]

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=3,
                        requireGeometry=ssdo.complexFeature)

        #### Run Analysis ####
        se = SE.StandardEllipse(ssdo, weightField=weightField,
                                caseField=caseField,
                                stdDeviations=stdDeviations)

        #### Create Output ####
        se.createOutput(outputFC, parameters)


class MeanCenter(object):
    def __init__(self):
        self.label = "Mean Center"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040002
        self.hasZ = False
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']
        param2.parameterDependencies = ["Input_Feature_Class"]

        param3 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Text', 'Date']
        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Dimension Field",
                                 name="Dimension_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Short', 'Long', 'Float', 'Double']
        param4.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        #### Check for Z Geometry and Fields ####
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    if desc.HasZ:
                        self.hasZ = True
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    pass
            else:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    pass

                    #### Add Fields ####
        addFields = []

        #### Weight Field ####
        if self.params[2].value:
            fieldName = self.params[2].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Case Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Dim Field ####
        if self.params[4].value:
            fieldName = self.params[4].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["XCoord", "YCoord"]
        if self.hasZ:
            fieldNames.append("ZCoord")

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields
        self.params[1].schema.featureTypeRule = "AsSpecified"
        self.params[1].schema.featureType = "Simple"
        self.params[1].schema.geometryTypeRule = "AsSpecified"
        self.params[1].schema.geometryType = "Point"

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        import MeanCenter as MC
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        weightField = UTILS.getTextParameter(2, parameters, fieldName=True)
        caseField = UTILS.getTextParameter(3, parameters, fieldName=True)
        dimField = UTILS.getTextParameter(4, parameters, fieldName=True)

        fieldList = []
        if weightField:
            fieldList.append(weightField)

        if caseField:
            fieldList.append(caseField)

        if dimField:
            fieldList.append(dimField)

        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=1)

        mc = MC.MeanCenter(ssdo, weightField=weightField,
                           caseField=caseField, dimField=dimField)

        mc.createOutput(outputFC, parameters)


class StandardDistance(object):
    def __init__(self):
        self.label = "Standard Distance"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040005
        self.circTypes = {"1_STANDARD_DEVIATION": 1, "2_STANDARD_DEVIATIONS": 2,
                          "3_STANDARD_DEVIATIONS": 3}
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Standard Distance Feature Class",
                                 name="Output_Standard_Distance_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Circle Size",
                                 name="Circle_Size",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['1_STANDARD_DEVIATION', '2_STANDARD_DEVIATIONS', '3_STANDARD_DEVIATIONS']

        param2.value = '1_STANDARD_DEVIATION'

        param3 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Float', 'Double']
        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Short', 'Long', 'Text', 'Date']
        param4.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            # if not self.params[0].isInputValueDerived():
            try:
                desc = ARCPY.Describe(self.params[0].value)
                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                pass

        #### Add Fields ####
        addFields = []

        #### Weight Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Case Field ####
        if self.params[4].value:
            fieldName = self.params[4].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["CenterX", "CenterY", "StdDist"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[2].hasError():
            if self.params[2].value.upper().replace(" ", "_") in self.circTypes:
                self.params[2].clearMessage()

    def execute(self, parameters, messages):
        import StandardDistance as SD

        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        stdDeviations = UTILS.getTextParameter(2, parameters).upper().replace(" ", "_")
        weightField = UTILS.getTextParameter(3, parameters, fieldName=True)
        caseField = UTILS.getTextParameter(4, parameters, fieldName=True)

        fieldList = []
        if weightField:
            fieldList.append(weightField)
        if caseField:
            fieldList.append(caseField)

        stdDeviations = self.circTypes[stdDeviations]

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=2,
                        requireGeometry=ssdo.complexFeature)

        #### Run Analysis ####
        sd = SD.StandardDistance(ssdo, weightField=weightField,
                                 caseField=caseField,
                                 stdDeviations=stdDeviations)

        #### Create Output ####
        sd.createOutput(outputFC, parameters)


class CollectEvents(object):
    def __init__(self):
        self.label = "Collect Events"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Utilities"
        self.helpContext = 9050001
        self.params = None

    def getParameterInfo(self):
        param0 = ARCPY.Parameter(displayName="Input Incident Features",
                                 name="Input_Incident_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Weighted Point Feature Class",
                                 name="Output_Weighted_Point_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Results Field",
                                 name="Results_Field",
                                 datatype="Field",
                                 parameterType="Derived",
                                 direction="Output")

        param2.value = 'Count'

        param3 = ARCPY.Parameter(displayName="Z Max Value",
                                 name="Z_Max_Value",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        return [param0, param1, param2, param3]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        newField = ARCPY.Field()
        newField.name = "ICOUNT"
        newField.type = "LONG"
        self.params[1].schema.additionalFields = [newField]
        self.params[1].schema.featureTypeRule = "AsSpecified"
        self.params[1].schema.featureType = "Simple"
        self.params[1].schema.geometryTypeRule = "AsSpecified"
        self.params[1].schema.geometryType = "Point"

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        import CollectEvents as CE
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC)

        countFieldNameOut, maxCount, N, numUnique = CE.collectEvents(ssdo, outputFC)
        CE.setDerivedOutput(countFieldNameOut, maxCount, parameters)
        CE.renderResults(parameters)


class GeographicallyWeightedRegression(object):
    def __init__(self):
        self.label = "Geographically Weighted Regression"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060002
        self.shapeType = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Dependent variable",
                                 name="dependent_field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']

        param1.parameterDependencies = ["in_features"]

        param2 = ARCPY.Parameter(displayName="Explanatory variable(s)",
                                 name="explanatory_field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)

        param2.filter.list = ['Short', 'Long', 'Float', 'Double']

        param2.parameterDependencies = ["in_features"]

        param3 = ARCPY.Parameter(displayName="Output feature class",
                                 name="out_featureclass",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param4 = ARCPY.Parameter(displayName="Kernel type",
                                 name="kernel_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['FIXED', 'ADAPTIVE']

        param4.value = 'FIXED'

        param5 = ARCPY.Parameter(displayName="Bandwidth method",
                                 name="bandwidth_method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"

        param5.filter.list = ['AICc', 'CV', 'BANDWIDTH_PARAMETER']

        param5.value = 'AICc'

        param6 = ARCPY.Parameter(displayName="Distance",
                                 name="distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0.0, 1.79769e+308]
        param6.enabled = False
        param7 = ARCPY.Parameter(displayName="Number of neighbors",
                                 name="number_of_neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.type = "Range"
        param7.filter.list = [1, 1000]
        param7.value = 30

        param7.enabled = False
        param8 = ARCPY.Parameter(displayName="Weights",
                                 name="weight_field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['Short', 'Long', 'Float', 'Double']
        param8.parameterDependencies = ["in_features"]

        param9 = ARCPY.Parameter(displayName="Coefficient raster workspace",
                                 name="coefficient_raster_workspace",
                                 datatype="DEWorkspace",
                                 parameterType="Optional",
                                 direction="Input")
        param9.category = "Additional Parameters (Optional)"
        param10 = ARCPY.Parameter(displayName="Output cell size",
                                  name="cell_size",
                                  datatype="analysis_cell_size",
                                  parameterType="Optional",
                                  direction="Input")

        param10.category = "Additional Parameters (Optional)"
        param11 = ARCPY.Parameter(displayName="Prediction locations",
                                  name="in_prediction_locations",
                                  datatype="GPFeatureLayer",
                                  parameterType="Optional",
                                  direction="Input")
        param11.filter.list = ['Point', 'Polygon']
        param11.category = "Additional Parameters (Optional)"
        param12 = ARCPY.Parameter(displayName="Prediction explanatory variable(s)",
                                  name="prediction_explanatory_field",
                                  datatype="Field",
                                  parameterType="Optional",
                                  direction="Input",
                                  multiValue=True)
        param12.filter.list = ['Short', 'Long', 'Float', 'Double']
        param12.category = "Additional Parameters (Optional)"
        param12.parameterDependencies = ["in_prediction_locations"]

        param13 = ARCPY.Parameter(displayName="Output prediction feature class",
                                  name="out_prediction_featureclass",
                                  datatype="DEFeatureClass",
                                  parameterType="Optional",
                                  direction="Output")
        param13.category = "Additional Parameters (Optional)"
        param14 = ARCPY.Parameter(displayName="Output table",
                                  name="out_table",
                                  datatype="DETable",
                                  parameterType="Derived",
                                  direction="Output")
        param14.enabled = False
        param15 = ARCPY.Parameter(displayName="Output regression rasters",
                                  name="out_regression_rasters",
                                  datatype="GPRasterLayer",
                                  parameterType="Derived",
                                  direction="Output")
        param15.enabled = False
        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11,
                param12, param13, param14, param15]

    def isLicensed(self):
        try:
            t = ARCPY.CheckOutExtension("Spatial")
            if t != 'CheckedOut':
                return False
        except:
            return False

        return True

    def updateParameters(self, parameters):
        size = 0
        desc = None
        if parameters[0].altered:
            try:
                desc = ARCPY.Describe(parameters[0].value)
                size = min(desc.extent.width, desc.extent.height) / 250.0
                shapeType = desc.ShapeType.upper()
                if shapeType == "POINT":
                    parameters[3].symbology = OS.path.join(pathLayers, "GWR_Points.lyrx")
                if shapeType == "POLYGON":
                    parameters[3].symbology = OS.path.join(pathLayers, "GWR_Polygons.lyrx")
            except:
                pass

        if not parameters[10].altered:
            if size > 0:
                parameters[10].value = size

        if parameters[5].altered:
            value5 = parameters[5].value.upper().replace(' ', '_')
            parameters[5].value = value5

        if parameters[4].value:
            if parameters[4].value == 'FIXED' and parameters[5].value == 'BANDWIDTH_PARAMETER':
                parameters[6].enabled = True
                parameters[7].enabled = False
            if parameters[4].value == 'ADAPTIVE' and parameters[5].value == 'BANDWIDTH_PARAMETER':
                parameters[6].enabled = False
                parameters[7].enabled = True

        return

    def updateMessages(self, parameters):

        return

    def execute(self, parameters, messages):
        ### Get parameter values ####
        in_features = UTILS.getTextParameter(0, parameters)
        dependent_field = UTILS.getTextParameter(1, parameters, fieldName=True)
        explanatory_field = UTILS.getTextParameter(2, parameters)
        out_feature = UTILS.getTextParameter(3, parameters)
        kernel_type = UTILS.getTextParameter(4, parameters)
        band_width = UTILS.getTextParameter(5, parameters)
        distance = UTILS.getNumericParameter(6, parameters, defualt="FLOAT")
        nn = UTILS.getNumericParameter(7, parameters)
        weight_field = UTILS.getTextParameter(8, parameters, fieldName=True)
        crw = UTILS.getTextParameter(9, parameters)
        anaCellSize = UTILS.getTextParameter(10, parameters)
        in_pred = UTILS.getTextParameter(11, parameters)
        pred_field = UTILS.getTextParameter(12, parameters)
        out_pred = UTILS.getTextParameter(13, parameters)
        gwr = UTILS.getTextParameter(14, parameters)
        coe = UTILS.getTextParameter(15, parameters)
        import warnings as WARNINGS
        with WARNINGS.catch_warnings():
            WARNINGS.simplefilter("ignore")

            try:
                ARCPY.GeographicallyWeightedRegression_analysis(
                    in_features, dependent_field, explanatory_field, out_feature,
                    kernel_type, band_width, distance, nn, weight_field, crw,
                    anaCellSize, in_pred, pred_field, out_pred)
            except:
                pass

            ####Wrapping messages ####
            errors = ARCPY.GetMessages(2)
            warnings = ARCPY.GetMessages(1)
            output = ARCPY.GetMessages(0)
            if len(warnings):
                ARCPY.AddWarning(str(warnings))
            if len(output):
                n = output.find("Bandwidth")
                if n > -1:
                    output = output[n:]
                    ARCPY.AddMessage(str(output))
            if len(errors):
                ARCPY.AddError(str(errors))

        return


class GWR(object):
    def __init__(self):
        self.label = "Geographically Weighted Regression"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060007
        self.shapeType = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ['Point', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Dependent Variable",
                                 name="dependent_variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.list = ['Short', 'Long', 'Float', 'Double']
        param1.parameterDependencies = ["in_features"]

        param2 = ARCPY.Parameter(displayName="Model Type",
                                 name="model_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param2.filter.type = "ValueList"
        param2.filter.list = ["CONTINUOUS", "BINARY", "COUNT"]
        param2.value = "CONTINUOUS"

        param3 = ARCPY.Parameter(displayName="Explanatory Variable(s)",
                                 name="explanatory_variables",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)

        param3.filter.list = ['Short', 'Long', 'Float', 'Double']
        param3.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param3.parameterDependencies = ["in_features"]

        param4 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param5 = ARCPY.Parameter(displayName="Neighborhood Type",
                                 name="neighborhood_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param5.filter.type = "ValueList"
        param5.filter.list = ["NUMBER_OF_NEIGHBORS", "DISTANCE_BAND"]

        param6 = ARCPY.Parameter(displayName="Neighborhood Selection Method",
                                 name="neighborhood_selection_method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param6.filter.type = "ValueList"
        param6.filter.list = ["GOLDEN_SEARCH", "MANUAL_INTERVALS",
                              "USER_DEFINED"]

        #### Optimized (Optional) / Manual (Required) ####
        param7 = ARCPY.Parameter(displayName="Minimum Number of Neighbors",
                                 name="minimum_number_of_neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.type = "Range"
        param7.filter.list = [2, 999]
        param7.enabled = False

        #### Optimized (Optional) ####
        param8 = ARCPY.Parameter(displayName="Maximum Number of Neighbors",
                                 name="maximum_number_of_neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.type = "Range"
        param8.filter.list = [3, 1000]
        param8.enabled = False

        #### Optimized (Optional) / Manual (Required) ####
        param9 = ARCPY.Parameter(displayName="Minimum Search Distance",
                                 name="minimum_search_distance",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param9.filter.list = supportDist
        param9.enabled = False

        #### Optimized (Optional) ####
        param10 = ARCPY.Parameter(displayName="Maximum Search Distance",
                                  name="maximum_search_distance",
                                  datatype="GPLinearUnit",
                                  parameterType="Optional",
                                  direction="Input")
        param10.filter.list = supportDist
        param10.enabled = False

        #### Manual (Required) ####
        param11 = ARCPY.Parameter(displayName="Number of Neighbors Increment",
                                  name="number_of_neighbors_increment",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param11.filter.type = "Range"
        param11.filter.list = [1, 500]
        param11.enabled = False

        #### Manual (Required) ####
        param12 = ARCPY.Parameter(displayName="Search Distance Increment",
                                  name="search_distance_increment",
                                  datatype="GPLinearUnit",
                                  parameterType="Optional",
                                  direction="Input")
        param12.filter.list = supportDist
        param12.enabled = False

        #### Manual (Required) ####
        param13 = ARCPY.Parameter(displayName="Number of Increments",
                                  name="number_of_increments",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param13.filter.type = "Range"
        param13.filter.list = [2, 20]
        param13.enabled = False

        #### User Defined with Number of Neighbors Parameters (Required) ####
        param14 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param14.filter.type = "Range"
        param14.filter.list = [2, 1000]
        param14.enabled = False

        #### User Defined with Distance Band Parameters (Required) ####
        param15 = ARCPY.Parameter(displayName="Distance Band",
                                  name="distance_band",
                                  datatype="GPLinearUnit",
                                  parameterType="Optional",
                                  direction="Input")
        param15.filter.list = supportDist
        param15.enabled = False

        #### Prediction ####
        param16 = ARCPY.Parameter(displayName="Prediction Locations",
                                  name="prediction_locations",
                                  datatype="GPFeatureLayer",
                                  parameterType="Optional",
                                  direction="Input")
        param16.filter.list = ['Point', 'Polygon']
        param16.category = "Prediction Options"

        param17 = ARCPY.Parameter(displayName="Explanatory Variables to Match",
                                  name="explanatory_variables_to_match",
                                  datatype="GPValueTable",
                                  parameterType="Optional",
                                  direction="Input")
        param17.parameterDependencies = [param16.name]
        param17.columns = [['GPString', 'Field From Input Features'],
                           ['Field', 'Field From Prediction Locations']]
        param17.columns = [['Field', 'Field From Prediction Locations'],
                           ['GPString', 'Field From Input Features']]
        param17.filters[1].type = "ValueList"
        param17.filters[0].list = ["Double", "Float", "Short", "Long"]
        param17.category = "Prediction Options"

        param18 = ARCPY.Parameter(displayName="Output Predicted Features",
                                  name="output_predicted_features",
                                  datatype="DEFeatureClass",
                                  parameterType="Optional",
                                  direction="Output")
        param18.category = "Prediction Options"

        param19 = ARCPY.Parameter(displayName="Robust Prediction",
                                  name="robust_prediction",
                                  datatype='GPBoolean',
                                  parameterType="Optional",
                                  direction="Input")
        param19.filter.list = ['ROBUST', 'NON_ROBUST']
        param19.value = True
        param19.category = "Prediction Options"

        #### Additional Options ####
        param20 = ARCPY.Parameter(displayName="Local Weighting Scheme",
                                  name="local_weighting_scheme",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")
        param20.filter.type = "ValueList"
        param20.filter.list = ['GAUSSIAN', 'BISQUARE']
        param20.value = 'BISQUARE'
        param20.category = "Additional Options"

        param21 = ARCPY.Parameter(displayName="Coefficient Raster Workspace",
                                  name="coefficient_raster_workspace",
                                  datatype="DEWorkspace",
                                  parameterType="Optional",
                                  direction="Input")
        param21.category = "Additional Options"
        #### Must Have Advanced License for Coef Rasters ####
        if not checkLicense():
            param21.enabled = False

        param22 = ARCPY.Parameter(displayName="Coefficient Raster Layers",
                                  name="coefficient_raster_layers",
                                  datatype="GPRasterLayer",
                                  parameterType="Derived",
                                  direction="Output",
                                  multiValue=True)

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9, param10, param11, param12,
                param13, param14, param15, param16, param17, param18,
                param19, param20, param21, param22]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        import GWR

        desc = None
        if parameters[0].altered or parameters[2].altered:
            modelType = parameters[2].value
            try:
                desc = ARCPY.Describe(parameters[0].value)
                shapeType = desc.ShapeType.upper()
                outLYR = ""
                if modelType == "CONTINUOUS":
                    if shapeType == "POINT":
                        outLYR = "GWR_Points.lyrx"
                    if shapeType == "POLYGON":
                        outLYR = "GWR_Polygons.lyrx"
                else:
                    if shapeType == "POINT":
                        outLYR = "GGWR_Points.lyrx"
                    if shapeType == "POLYGON":
                        outLYR = "GGWR_Polygons.lyrx"
                parameters[4].symbology = OS.path.join(pathLayers, outLYR)
            except:
                pass

        #### Linear Unit Filters ####
        if parameters[9].value:
            try:
                linearUnit = parameters[9].valueAsText.split(" ")[-1]
                parameters[10].filter.list = [linearUnit]
                parameters[12].filter.list = [linearUnit]
            except:
                parameters[10].filter.list = supportDist
                parameters[12].filter.list = supportDist
        else:
            parameters[10].filter.list = supportDist
            parameters[12].filter.list = supportDist

        if parameters[9].value and parameters[10].value:
            param9, unit9 = parameters[9].valueAsText.split(" ")
            param10, unit10 = parameters[10].valueAsText.split(" ")
            if not unit9.upper() == unit10.upper():
                parameters[10].value = " ".join([param10, unit9])

        if parameters[9].value and parameters[12].value:
            param9, unit9 = parameters[9].valueAsText.split(" ")
            param12, unit12 = parameters[12].valueAsText.split(" ")
            if not unit9.upper() == unit12.upper():
                parameters[12].value = " ".join([param12, unit9])

        #### Neighborhood Search Options ####
        param5 = parameters[5].value
        param6 = parameters[6].value

        if param5 and param6:
            if param5 == "NUMBER_OF_NEIGHBORS":
                parameters[6].filter.list = ["GOLDEN_SEARCH", "MANUAL_INTERVALS", "USER_DEFINED"]

                #### Min/Max Distance ####
                clearParameter(parameters[9])
                clearParameter(parameters[10])
                clearParameter(parameters[12])

                #### User Dist/SWM ####
                clearParameter(parameters[15])

                if param6 in ["GOLDEN_SEARCH", "MANUAL_INTERVALS"]:
                    #### User Provided ####
                    clearParameter(parameters[14])

                    #### Min KNN ####
                    parameters[7].enabled = True

                    if param6 == "MANUAL_INTERVALS":
                        #### Max KNN ####
                        clearParameter(parameters[8])

                        #### Number of KNN/Increments ####
                        parameters[11].enabled = True
                        parameters[13].enabled = True
                    else:
                        #### Max KNN ####
                        parameters[8].enabled = True

                        #### Number of KNN/Increments ####
                        clearParameter(parameters[11])
                        clearParameter(parameters[13])

                else:
                    #### User Provided ####
                    parameters[14].enabled = True
                    clearParameter(parameters[7])
                    clearParameter(parameters[8])
                    clearParameter(parameters[11])
                    clearParameter(parameters[13])

            if param5 == "DISTANCE_BAND":
                parameters[6].filter.list = ["GOLDEN_SEARCH", "MANUAL_INTERVALS", "USER_DEFINED"]

                #### Min/Max KNN ####
                clearParameter(parameters[7])
                clearParameter(parameters[8])
                clearParameter(parameters[11])

                #### User KNN/SWM ####
                clearParameter(parameters[14])

                if param6 in ["GOLDEN_SEARCH", "MANUAL_INTERVALS"]:
                    #### User Provided ####
                    clearParameter(parameters[15])

                    #### Min Distance ####
                    parameters[9].enabled = True

                    if param6 == "MANUAL_INTERVALS":
                        #### Max Distance ####
                        clearParameter(parameters[10])

                        #### Number of Distance/Increments ####
                        parameters[12].enabled = True
                        parameters[13].enabled = True
                    else:
                        #### Max Distance ####
                        parameters[10].enabled = True

                        #### Number of Distance/Increments ####
                        clearParameter(parameters[12])
                        clearParameter(parameters[13])

                else:
                    #### User Provided ####
                    parameters[15].enabled = True
                    clearParameter(parameters[9])
                    clearParameter(parameters[10])
                    clearParameter(parameters[12])
                    clearParameter(parameters[13])

        if not parameters[3].value or not parameters[16].value:
            # remove all the items in the predict items
            parameters[17].value = None

        #### Match Input / Prediction Fields ####
        if paramChanged(parameters[3]) or paramChanged(parameters[16]):
            param16 = parameters[16].value
            param3 = parameters[3].value
            if param3 and param16:
                #### Set Default Matches (Only on First Attempt) ####
                indVars = parameters[3].valueAsText.split(";")

                try:
                    desc = ARCPY.Describe(param16)
                    shapeType = desc.ShapeType.upper()
                    predLYR = ""
                    if modelType == "BINARY":
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points_Binary.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons_Binary.lyrx"
                    elif modelType == "COUNT":
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points_Count.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons_Count.lyrx"
                    else:
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons.lyrx"
                    parameters[18].symbology = OS.path.join(pathLayers, predLYR)

                    nameAliasMapPredFC = dict()
                    for fieldObj in desc.fields:
                        nameAliasMapPredFC[fieldObj.name] = fieldObj.aliasName
                    vtList = matchVariables(indVars, desc)
                    nameAliasMapInputFC = dict()
                    desc = ARCPY.Describe(parameters[0].value)
                    for fieldObj in desc.fields:
                        nameAliasMapInputFC[fieldObj.name] = fieldObj.aliasName
                    for pair in vtList:
                        pair[1] = nameAliasMapInputFC[pair[1]]
                    if parameters[17].value:
                        #### Keep the Already Existing Fields Selected by User ####
                        existingMatchPairs = dict()
                        for vtRow in parameters[17].value:
                            predField = vtRow[0].value
                            indFieldAlias = vtRow[1]
                            if predField in nameAliasMapPredFC and indFieldAlias not in existingMatchPairs:
                                existingMatchPairs[indFieldAlias] = predField
                        for pair in vtList:
                            if pair[1] in existingMatchPairs:
                                pair[0] = existingMatchPairs[pair[1]]
                    parameters[17].value = vtList
                except:
                    pass

        #### Robust Prediction ####
        if paramChanged(parameters[2]):
            if parameters[2].value != "CONTINUOUS":
                parameters[19].enabled = False
                parameters[19].value = False
            else:
                parameters[19].enabled = True

        #### Attach the Field Names to Output FC and Prediction FC for Model Builder####
        if parameters[0].value and parameters[1].value and \
                parameters[3].value and parameters[4].value and \
                parameters[5].value and parameters[6].value:
            try:
                outPath, outName = OS.path.split(UTILS.getTextParameter(4, parameters))
                if ARCPY.Exists(outPath):
                    outputFCFields = GWR.getOutputFCFields(parameters)
                    parameters[4].schema.additionalFields = outputFCFields
                else:
                    parameters[4].schema.additionalFields = []
            except:
                parameters[4].schema.additionalFields = []
        else:
            parameters[4].schema.additionalFields = []
        if parameters[0].value and parameters[1].value and \
                parameters[3].value and parameters[4].value and \
                parameters[5].value and parameters[6].value and \
                parameters[16].value and parameters[17].value and \
                parameters[18].value:
            try:
                outPath, outName = OS.path.split(UTILS.getTextParameter(18, parameters))
                if ARCPY.Exists(outPath):
                    predictFCFields = GWR.getPredictFCFields(parameters)
                    parameters[18].schema.additionalFields = predictFCFields
            except:
                parameters[18].schema.additionalFields = []
        else:
            parameters[18].schema.additionalFields = []

        #### Add Dervied Raster Layers for Model Builder ####
        if parameters[21].value:
            if parameters[3].value and parameters[4].value:
                indVars = parameters[3].valueAsText.split(";")
                outputFC = parameters[4].value.value
                outPath, outName = OS.path.split(UTILS.getTextParameter(4, parameters))
                try:
                    if ARCPY.Exists(outPath):
                        rasterNames = makeDerivedRasterLayers(indVars, outputFC)
                        parameters[22].value = rasterNames
                    else:
                        parameters[22].value = None
                except:
                    parameters[22].value = None
        else:
            parameters[22].value = None

        return

    def updateMessages(self, parameters):
        #### Optional to Required Parameter Messages ####
        import locale as LOCALE

        param5 = parameters[5].value
        param6 = parameters[6].value
        if param5 and param6:
            if param6 == "MANUAL_INTERVALS":
                if param5 == "NUMBER_OF_NEIGHBORS":
                    #### Minimum Number of Neighs ####
                    if not parameters[7].value:
                        if not parameters[7].hasError():
                            parameters[7].setIDMessage("ERROR", 110161)

                    #### Number of Neighs Increment ####
                    if not parameters[11].value:
                        parameters[11].setIDMessage("ERROR", 110162)

                else:
                    #### Minimum Distance ####
                    if not parameters[9].value:
                        parameters[9].setIDMessage("ERROR", 110163)
                    else:
                        positiveParam = parameters[9]
                        positiveParamValue, positiveParamUnit = positiveParam.valueAsText.split(" ")
                        if LOCALE.atof(positiveParamValue) <= 0:
                            positiveParam.setIDMessage("ERROR", 531)

                    #### Distance Increment ####
                    if not parameters[12].value:
                        parameters[12].setIDMessage("ERROR", 110164)
                    else:
                        positiveParam = parameters[12]
                        positiveParamValue, positiveParamUnit = positiveParam.valueAsText.split(" ")
                        if LOCALE.atof(positiveParamValue) <= 0:
                            positiveParam.setIDMessage("ERROR", 531)

                #### Number of Increments ####
                if not parameters[13].value:
                    parameters[13].setIDMessage("ERROR", 110165)

            if param6 == "USER_DEFINED":
                if param5 == "NUMBER_OF_NEIGHBORS":
                    #### Number of Neighs ####
                    if not parameters[14].value:
                        if not parameters[14].hasError():
                            parameters[14].setIDMessage("ERROR", 110166)

                else:
                    #### Distance Band ####
                    if not parameters[15].value:
                        parameters[15].setIDMessage("ERROR", 110167)
                    else:
                        positiveParam = parameters[15]
                        positiveParamValue, positiveParamUnit = positiveParam.valueAsText.split(" ")
                        if LOCALE.atof(positiveParamValue) <= 0:
                            positiveParam.setIDMessage("ERROR", 531)

            if param6 == "GOLDEN_SEARCH":
                if param5 == "NUMBER_OF_NEIGHBORS":
                    #### Minimum Number of Neighs < Maximum ####
                    if parameters[7].value and parameters[8].value:
                        if parameters[7].value >= parameters[8].value:
                            parameters[7].setIDMessage("ERROR", 110223)

                else:
                    #### Minimum Distance < Maximum ####
                    if parameters[9].value and parameters[10].value:
                        param9, unit9 = parameters[9].valueAsText.split(" ")
                        param10, unit10 = parameters[10].valueAsText.split(" ")
                        if LOCALE.atof(param9) >= LOCALE.atof(param10):
                            parameters[9].setIDMessage("ERROR", 110224)

                        #### Linear Unit Must be the Same ####
                        if unit9.upper() != unit10.upper():
                            parameters[9].setIDMessage("ERROR", 110226)

                    positiveParam = parameters[9]
                    if positiveParam.value:
                        positiveParamValue, positiveParamUnit = positiveParam.valueAsText.split(" ")
                        if LOCALE.atof(positiveParamValue) <= 0:
                            positiveParam.setIDMessage("ERROR", 531)

                    positiveParam = parameters[10]
                    if positiveParam.value:
                        positiveParamValue, positiveParamUnit = positiveParam.valueAsText.split(" ")
                        if LOCALE.atof(positiveParamValue) <= 0:
                            positiveParam.setIDMessage("ERROR", 531)

        #### Matching VT Errors ####
        if parameters[16].value and parameters[3].value and parameters[0].value:
            createVT = False
            try:
                descInputFC = ARCPY.Describe(parameters[0].value)
                fields = descInputFC.fields
                createVT = True
            except:
                pass

            if createVT:
                aliasNameMapInputFC = dict()
                nameAliasMapInputFC = dict()
                for fieldObj in fields:
                    aliasNameMapInputFC[fieldObj.aliasName] = fieldObj.name
                    nameAliasMapInputFC[fieldObj.name] = fieldObj.aliasName
                predFields = []
                inFieldAliases = []
                missingMatch = []
                if parameters[17].value:
                    for vtRow in parameters[17].value:
                        predField = vtRow[0].value
                        indFieldAlias = vtRow[1]
                        predFields.append(predField)
                        inFieldAliases.append(indFieldAlias)
                        if predField in ["#", ""]:
                            missingMatch.append(indFieldAlias)

                #### Missing Match ####
                if len(missingMatch):
                    missingMatch = ", ".join([i for i in missingMatch])
                    parameters[17].setIDMessage("ERROR", 110158, missingMatch)

                #### Check for Unique Prediction Fields ####
                predFieldsSet = set(predFields)
                if len(predFieldsSet) != len(predFields):
                    duplicate = []
                    for fieldName in predFieldsSet:
                        if predFields.count(fieldName) != 1 and fieldName not in ['', '#']:
                            duplicate.append(fieldName)
                    if len(duplicate) > 0:
                        duplicate = ", ".join(duplicate)
                        parameters[17].setIDMessage("ERROR", 110160, duplicate)

                #### Check for Unique Input Fields ####
                inFieldsAliasSet = set(inFieldAliases)
                if len(inFieldsAliasSet) != len(inFieldAliases):
                    duplicate = []
                    for inFieldAlias in inFieldsAliasSet:
                        if inFieldAliases.count(inFieldAlias) != 1 and inFieldAlias not in ['', '#']:
                            duplicate.append(inFieldAlias)
                    if len(duplicate) > 0:
                        duplicate = ", ".join(duplicate)
                        parameters[17].setIDMessage("ERROR", 110159, duplicate)

                #### Report Any Input Fields Left Unmatched From Ind Vars ####
                indVarAliases = set([nameAliasMapInputFC[indVar] for indVar in parameters[3].valueAsText.split(";") if
                                     indVar in nameAliasMapInputFC])
                missingVars = indVarAliases.difference(inFieldsAliasSet)
                if len(missingVars):
                    missingVars = ", ".join([i for i in missingVars])
                    parameters[17].setIDMessage("ERROR", 110157, missingVars)
                unexpectedVars = inFieldsAliasSet.difference(indVarAliases)
                hasEmptyField = False
                if '' in unexpectedVars or "#" in unexpectedVars:
                    hasEmptyField = True
                unexpectedVars = [v for v in unexpectedVars if v not in ['', '#']]
                if hasEmptyField:
                    unexpectedVars.append("''")
                if len(unexpectedVars):
                    unexpectedVars = ", ".join(unexpectedVars)
                    parameters[17].setIDMessage("ERROR", 110247, unexpectedVars)

                #### Must Provide Output Prediction Features ####
                if not parameters[18].value:
                    parameters[18].setIDMessage("ERROR", 110241)

        return

    def execute(self, parameters, messages):
        import os as OS
        import SSUtilities as UTILS
        import SSDataObject as SSDO
        import GWR

        ### Get parameter values ####
        inputFC = UTILS.getTextParameter(0, parameters)
        depVarName = UTILS.getTextParameter(1, parameters).upper()
        modelType = UTILS.getTextParameter(2, parameters).upper()
        indVarNames = UTILS.getTextParameter(3, parameters).upper()
        indVarNames = indVarNames.split(";")
        outputFC = UTILS.getTextParameter(4, parameters)
        outPath, outName = OS.path.split(outputFC)
        neighborType = UTILS.getTextParameter(5, parameters)
        neighborMethod = UTILS.getTextParameter(6, parameters)
        minNumNeighs = UTILS.getNumericParameter(7, parameters)
        maxNumNeighs = UTILS.getNumericParameter(8, parameters)
        minDistance = UTILS.getTextParameter(9, parameters)
        maxDistance = UTILS.getTextParameter(10, parameters)
        numNeighsInc = UTILS.getNumericParameter(11, parameters)
        distanceInc = UTILS.getTextParameter(12, parameters)
        numIncrements = UTILS.getNumericParameter(13, parameters)
        numNeighs = UTILS.getNumericParameter(14, parameters)
        bandwidth = UTILS.getTextParameter(15, parameters)
        predictInputFC = UTILS.getTextParameter(16, parameters)
        predictVT = parameters[17].value
        predictOutputFC = UTILS.getTextParameter(18, parameters)
        robust = parameters[19].value
        kernel = UTILS.getTextParameter(20, parameters)
        if kernel is None:
            kernel = "BISQUARE"
        rasterDir = UTILS.getTextParameter(21, parameters)
        #### Check If User Has the Advanced License to Conduct This Analysis ####
        if not checkLicense() and rasterDir is not None:
            ARCPY.AddIDMessage("ERROR", 110257)
            raise SystemExit()

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC)
        allVars = [depVarName] + indVarNames
        ssdo.obtainData(ssdo.oidName, allVars, minNumObs=20)

        #### Get Family ####
        family = convertFamilyType[modelType]

        #### Core Calculation ####
        if neighborMethod == "MANUAL_INTERVALS":
            #### Manual Search for AICc ####
            manualGWR = GWR.ManualGWR(ssdo, depVarName, indVarNames,
                                      numIncrements,
                                      minNumNeighs=minNumNeighs,
                                      numNeighsInc=numNeighsInc,
                                      minDistance=minDistance,
                                      distanceInc=distanceInc,
                                      kernel=kernel, family=family)
            if manualGWR.useKNN:
                numNeighs = manualGWR.searchCriteria
                bandwidth = None
            else:
                bandwidth = manualGWR.finalBandwidth
                numNeighs = None

                #### Run Core Calculation ####
            gwr = GWR.GWR(ssdo, depVarName, indVarNames,
                          bandwidth=bandwidth,
                          numNeighs=numNeighs, kernel=kernel,
                          family=family, silentMessages=True)

        elif neighborMethod == "USER_DEFINED":
            #### Basic ####
            gwr = GWR.GWR(ssdo, depVarName, indVarNames,
                          bandwidth=bandwidth, numNeighs=numNeighs,
                          kernel=kernel, family=family)
        else:
            gwr = GWR.OptimizedGWR(ssdo, depVarName, indVarNames,
                                   minNumNeighs=minNumNeighs,
                                   maxNumNeighs=maxNumNeighs,
                                   minDistance=minDistance,
                                   maxDistance=maxDistance,
                                   kernel=kernel, family=family,
                                   neighborType=neighborType)

        #### Create Report ####
        report = GWR.createGWRReport(gwr)
        ARCPY.AddMessage(report)

        #### Create Output ####
        GWR.createGWROutputFC(gwr, outputFC)

        #### Render Results ####
        if gwr.family != "GAUSSIAN":
            if ssdo.shapeType.upper() == "POINT":
                parameters[4].symbology = OS.path.join(pathLayers,
                                                       "GGWR_Points.lyrx")
            else:
                parameters[4].symbology = OS.path.join(pathLayers,
                                                       "GGWR_Polygons.lyrx")
        else:
            if ssdo.shapeType.upper() == "POINT":
                parameters[4].symbology = OS.path.join(pathLayers,
                                                       "GWR_Points.lyrx")
            else:
                parameters[4].symbology = OS.path.join(pathLayers,
                                                       "GWR_Polygons.lyrx")

        #### Prediction ####
        if predictInputFC is not None:
            varEntry = [vRow[0].value for vRow in predictVT]
            predVarNames = [i.upper() for i in varEntry]
            predictGWR = GWR.PredictGWR(gwr, robust=robust)
            predictGWR.createPredictionFC(predictInputFC, predictOutputFC,
                                          indVarNames=predVarNames)
            d = ARCPY.Describe(predictInputFC)
            if gwr.family == "LOGIT":
                if d.ShapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points_Binary.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons_Binary.lyrx"
            elif gwr.family == "POISSON":
                if d.ShapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points_Count.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons_Count.lyrx"
            else:
                if d.ShapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons.lyrx"
            parameters[18].symbology = OS.path.join(pathLayers,
                                                    predLYR)
        else:
            predictGWR = None

        #### Coefficient Rasters ####
        if rasterDir is not None:
            if predictGWR is None:
                predictGWR = GWR.PredictGWR(gwr, robust=robust)
            try:
                cellSize = UTILS.strToFloat(ARCPY.env.cellSize)
            except:
                if ssdo.useChordal:
                    envelope = UTILS.Envelope(ssdo.extent)
                    maxExtent = envelope.maxExtent
                    cellSize = envelope.maxExtent / 100
                else:
                    cellSize = ssdo.envelope.maxExtent / 100

            #### Get Output FC Prefix ####
            outputPref, ext = OS.path.splitext(outName)
            outRasterLayers = predictGWR.createPredictionRasters(ssdo, cellSize, rasterDir,
                                                                 outputPref=outputPref)
            ARCPY.SetParameter(22, outRasterLayers)

        #### Add Charts To The Results ####
        chartList = list()
        depVarNameOrigin = UTILS.getTextParameter(1, parameters)
        indVarNamesOrigin = UTILS.getTextParameter(3, parameters).split(";")
        appendVarNames = UTILS.createAppendFieldNames([depVarNameOrigin] + indVarNamesOrigin, outPath)
        chartTitle = ""

        #### Create Scatter Plot Matrix for Xs and Y ####
        smChartFields = []
        if modelType == 'CONTINUOUS' or modelType == 'COUNT':
            smChartFields = [appendVarNames[0]]
        smChartFields.extend(appendVarNames[1:])

        if len(smChartFields) < 3:
            if len(smChartFields) == 2:
                chartTitle = ARCPY.GetIDMessage(84888).format("Relationship")
                sChart1 = ARCPY.Chart(chartTitle)
                sChart1.type = 'scatter'
                sChart1.title = chartTitle
                # sChart1.description = 'desc'
                sChart1.xAxis.field = smChartFields[1]
                sChart1.yAxis.field = [smChartFields[0]]
                sChart1.xAxis.title = smChartFields[1]
                sChart1.yAxis.title = smChartFields[0]
                sChart1.scatter.showTrendLine = True
                chartList.append(sChart1)
        else:
            if len(smChartFields) > 10:
                ARCPY.AddIDMessage("WARNING", 110249, len(smChartFields))
                smChartFields = smChartFields[:10]
            chartTitle = ARCPY.GetIDMessage(84888).format("Relationships")
            smChart = ARCPY.Chart(chartTitle)
            smChart.type = 'scatterMatrix'
            smChart.title = chartTitle
            smChart.scatterMatrix.fields = smChartFields
            smChart.scatterMatrix.showTrendLine = True
            smChart.scatterMatrix.showHistograms = True
            # smChart.scatterMatrix.showAsRSquared = True
            chartList.append(smChart)

        if modelType == 'BINARY':
            #### Create Box Plot for Xs split By Y####
            chartTitle = ARCPY.GetIDMessage(84896)
            bpChart = ARCPY.Chart(chartTitle)
            bpChart.type = 'boxPlot'
            bpChart.title = chartTitle
            # bpChart.description = 'desc'
            bpChart.xAxis.field = ""
            bpChart.yAxis.field = appendVarNames[1:]
            # bpChart.xAxis.title = 'Predicted'
            bpChart.yAxis.title = ARCPY.GetIDMessage(84897)
            #### Set Box Plot Properties ####
            bpChart.boxPlot.splitCategory = appendVarNames[0]
            bpChart.boxPlot.splitCategoryAsMeanLine = False
            bpChart.boxPlot.standardizeValues = True
            chartList.append(bpChart)

        #### Create Histograms for Residuals/Deviance Residuals ####
        histChartShowComparisonDistribution = True
        histChartShowMean = True
        histChartXfield = ''
        histChartXTitle = ''
        if modelType == 'CONTINUOUS':
            chartTitle = ARCPY.GetIDMessage(84889)
            histChartXfield = 'STDRESID'
            histChartXTitle = ARCPY.GetIDMessage(84891)
            histChartShowComparisonDistribution = True
            histChartShowMean = True
        elif modelType == 'COUNT':
            chartTitle = ARCPY.GetIDMessage(84890)
            histChartXfield = 'DEV_RESID'
            histChartXTitle = ARCPY.GetIDMessage(84892)
            histChartShowComparisonDistribution = True
            histChartShowMean = True
        elif modelType == 'BINARY':
            chartTitle = ARCPY.GetIDMessage(84890)
            histChartXfield = 'DEV_RESID'
            histChartXTitle = ARCPY.GetIDMessage(84892)
            histChartShowComparisonDistribution = False
            histChartShowMean = False

        histChart = ARCPY.Chart(chartTitle)
        histChart.type = 'histogram'
        histChart.title = chartTitle
        histChart.xAxis.field = histChartXfield
        histChart.xAxis.title = histChartXTitle
        histChart.histogram.showComparisonDistribution = histChartShowComparisonDistribution
        histChart.histogram.showMean = histChartShowMean
        chartList.append(histChart)

        if modelType == 'CONTINUOUS' or modelType == 'COUNT':
            #### Create Scatter Plot for Residuals in CONTINUOUS and COUNT Model ####
            yAxisField = []
            yAxisTitle = ''
            if modelType == 'CONTINUOUS':
                chartTitle = ARCPY.GetIDMessage(84893)
                yAxisField = ['STDRESID']
                yAxisTitle = ARCPY.GetIDMessage(84891)
            elif modelType == 'COUNT':
                chartTitle = ARCPY.GetIDMessage(84894)
                yAxisField = ['DEV_RESID']
                yAxisTitle = ARCPY.GetIDMessage(84892)
            sChart = ARCPY.Chart(chartTitle)
            sChart.type = 'scatter'
            sChart.title = chartTitle
            # sChart.description = 'desc'
            sChart.xAxis.field = 'PREDICTED'
            sChart.yAxis.field = yAxisField
            sChart.xAxis.title = ARCPY.GetIDMessage(84895)
            sChart.yAxis.title = yAxisTitle
            sChart.scatter.showTrendLine = False
            chartList.append(sChart)
        elif modelType == 'BINARY':
            #### Create Bar Chart for Y and Predicted Y ####
            chartTitle = ARCPY.GetIDMessage(84898)
            barChart = ARCPY.Chart(chartTitle)
            barChart.type = "bar"
            barChart.title = chartTitle
            barChart.xAxis.field = "PREDICTED"
            barChart.yAxis.field = ""
            barChart.xAxis.sort = "asc"
            barChart.bar.aggregation = "COUNT"
            barChart.bar.splitCategory = appendVarNames[0]
            chartList.append(barChart)

        parameters[4].charts = chartList
        return


class GeneralizedLinearRegression(object):
    def __init__(self):
        self.label = "Generalized Linear Regression"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060008
        self.shapeType = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ['Point', 'Polygon']
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Dependent Variable",
                                 name="dependent_variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.list = ['Short', 'Long', 'Float', 'Double']
        param1.parameterDependencies = ["in_features"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Model Type",
                                 name="model_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param2.filter.type = "ValueList"
        param2.filter.list = ["CONTINUOUS", "BINARY", "COUNT"]
        param2.value = "CONTINUOUS"
        param2.displayOrder = 2

        hasAdvancedLicense = checkLicense()
        indVarsRequired = "Required"
        if hasAdvancedLicense:
            indVarsRequired = "Optional"

        param3 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")
        param3.displayOrder = 5

        param4 = ARCPY.Parameter(displayName="Explanatory Variable(s)",
                                 name="explanatory_variables",
                                 datatype="Field",
                                 parameterType=indVarsRequired,
                                 direction="Input",
                                 multiValue=True)

        param4.filter.list = ['Short', 'Long', 'Float', 'Double']
        param4.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param4.parameterDependencies = ["in_features"]
        param4.displayOrder = 3

        param5 = ARCPY.Parameter(displayName="Explanatory Distance Features",
                                 name="distance_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param5.filter.list = ["Polygon", "Point", "Polyline"]
        param5.displayOrder = 4
        param5.enabled = hasAdvancedLicense

        #### Prediction ####
        param6 = ARCPY.Parameter(displayName="Prediction Locations",
                                 name="prediction_locations",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.list = ['Point', 'Polygon']
        param6.category = "Prediction Options"
        param6.displayOrder = 6

        param7 = ARCPY.Parameter(displayName="Explanatory Variables to Match",
                                 name="explanatory_variables_to_match",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")
        param7.parameterDependencies = [param6.name]
        param7.columns = [['Field', 'Field From Prediction Locations'],
                          ['GPString', 'Field From Input Features']]
        param7.filters[1].type = "ValueList"
        param7.filters[0].list = ["Double", "Float", "Short", "Long"]
        param7.category = "Prediction Options"
        param7.displayOrder = 7

        param8 = ARCPY.Parameter(displayName="Match Distance Features",
                                 name="explanatory_distance_matching",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")
        param8.columns = [['GPFeatureLayer', 'Prediction Distance Features'],
                          ['GPString', 'Input Distance Features']]
        param8.filters[0].list = ["Polygon", "Point", "Polyline"]
        param8.controlCLSID = "{C99D0042-EF42-4B04-8A0B-1A53F6DB67A6}"
        param8.category = "Prediction Options"
        param8.displayOrder = 8
        param8.enabled = hasAdvancedLicense

        param9 = ARCPY.Parameter(displayName="Output Predicted Features",
                                 name="output_predicted_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Optional",
                                 direction="Output")
        param9.category = "Prediction Options"
        param9.displayOrder = 9

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param9]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        import GLR

        desc = None
        if parameters[0].altered or parameters[2].altered:
            modelType = parameters[2].value
            try:
                desc = ARCPY.Describe(parameters[0].value)
                shapeType = desc.ShapeType.upper()
                outLYR = ""
                if modelType == "CONTINUOUS":
                    if shapeType == "POINT":
                        outLYR = "GWR_Points.lyrx"
                    if shapeType == "POLYGON":
                        outLYR = "GWR_Polygons.lyrx"
                else:
                    if shapeType == "POINT":
                        outLYR = "GGWR_Points.lyrx"
                    if shapeType == "POLYGON":
                        outLYR = "GGWR_Polygons.lyrx"
                parameters[3].symbology = OS.path.join(pathLayers, outLYR)
            except:
                pass

        #### Remove All the Items in the Predict UI If Origin Parameter is None ####
        if not parameters[6].value:
            parameters[7].value = None
            parameters[8].value = None
        if not parameters[4].value:
            parameters[7].value = None
        if not parameters[5].value:
            parameters[8].value = None

        #### Match Input / Prediction Fields ####
        changedPredictions = paramChanged(parameters[6])
        if paramChanged(parameters[4]) or changedPredictions:
            param6 = parameters[6].value
            param4 = parameters[4].value
            if param4 and param6:
                #### Set Default Matches (Only on First Attempt) ####
                indVars = parameters[4].valueAsText.split(";")
                try:
                    desc = ARCPY.Describe(param6)
                    shapeType = desc.ShapeType.upper()
                    predLYR = ""
                    if modelType == "BINARY":
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points_Binary.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons_Binary.lyrx"
                    elif modelType == "COUNT":
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points_Count.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons_Count.lyrx"
                    else:
                        if shapeType == "POINT":
                            predLYR = "GWR_Predict_Points.lyrx"
                        else:
                            predLYR = "GWR_Predict_Polygons.lyrx"
                    parameters[9].symbology = OS.path.join(pathLayers, predLYR)

                    nameAliasMapPredFC = dict()
                    for fieldObj in desc.fields:
                        nameAliasMapPredFC[fieldObj.name] = fieldObj.aliasName
                    vtList = matchVariables(indVars, desc)
                    nameAliasMapInputFC = dict()
                    desc = ARCPY.Describe(parameters[0].value)
                    for fieldObj in desc.fields:
                        nameAliasMapInputFC[fieldObj.name] = fieldObj.aliasName
                    for pair in vtList:
                        pair[1] = nameAliasMapInputFC[pair[1]]
                    if parameters[7].value:
                        #### Keep the Already Existing Fields Selected by User ####
                        existingMatchPairs = dict()
                        for vtRow in parameters[7].value:
                            predField = vtRow[0].value
                            indFieldAlias = vtRow[1]
                            if predField in nameAliasMapPredFC and indFieldAlias not in existingMatchPairs:
                                existingMatchPairs[indFieldAlias] = predField
                        for pair in vtList:
                            if pair[1] in existingMatchPairs:
                                pair[0] = existingMatchPairs[pair[1]]
                    parameters[7].value = vtList
                except:
                    pass
        #### Match Input / Prediction Distance Features ####
        if paramChanged(parameters[5]) or changedPredictions:
            distanceFeatures = parameters[5].value
            predictFeatures = parameters[6].value
            if distanceFeatures and predictFeatures:
                #### Only Set if Empty ####
                fcList = parameters[5].valueAsText.split(";")
                vtList = baseDistanceMatchList(fcList)
                matchedDistances = UTILS.getTextParameterMatch(8, parameters,
                                                               ["MappingLayerObject", "mp.Layer"])
                if matchedDistances is not None:
                    #### Keep the Already Existing FCs Selected by User ####
                    distEntry = [f[0] for f in matchedDistances]
                    existingMatchPairs = dict()
                    for f in matchedDistances:
                        predDisFC = f[0]
                        indDisFC = f[1]
                        existingMatchPairs[indDisFC] = predDisFC
                    for pair in vtList:
                        if pair[1] in existingMatchPairs:
                            pair[0] = existingMatchPairs[pair[1]]
                for pair in vtList:
                    pair[0] = pair[0].strip("'").strip("\"")
                parameters[8].value = vtList

        #### Attach the Field Names to Output FC and Prediction FC for Model Builder####
        if parameters[0].value and parameters[1].value and \
                parameters[3].value:
            try:
                outPath, outName = OS.path.split(UTILS.getTextParameter(3, parameters))
                if ARCPY.Exists(outPath):
                    outputFCFields = GLR.getOutputFCFields(parameters)
                    parameters[3].schema.additionalFields = outputFCFields
                else:
                    parameters[3].schema.additionalFields = []
            except:
                parameters[3].schema.additionalFields = []
        else:
            parameters[3].schema.additionalFields = []
        if parameters[0].value and parameters[1].value and \
                parameters[3].value and parameters[6].value and \
                parameters[9].value:
            try:
                outPath, outName = OS.path.split(UTILS.getTextParameter(9, parameters))
                if ARCPY.Exists(outPath):
                    predictFCFields = GLR.getPredictFCFields(parameters)
                    parameters[9].schema.additionalFields = predictFCFields
                else:
                    parameters[9].schema.additionalFields = []
            except:
                parameters[9].schema.additionalFields = []
        else:
            parameters[9].schema.additionalFields = []
        return

    def updateMessages(self, parameters):
        #### Optional to Required Parameter Messages ####

        #### Matching VT Errors ####
        if parameters[6].value and parameters[4].value:
            descInputFC = ARCPY.Describe(parameters[0].value)
            aliasNameMapInputFC = dict()
            nameAliasMapInputFC = dict()
            for fieldObj in descInputFC.fields:
                aliasNameMapInputFC[fieldObj.aliasName] = fieldObj.name
                nameAliasMapInputFC[fieldObj.name] = fieldObj.aliasName
            predFields = []
            inFieldAliases = []
            missingMatch = []
            if parameters[7].value:
                for vtRow in parameters[7].value:
                    predField = vtRow[0].value
                    indFieldAlias = vtRow[1]
                    predFields.append(predField)
                    inFieldAliases.append(indFieldAlias)
                    if predField in ["#", ""]:
                        missingMatch.append(indFieldAlias)

            #### Missing Match ####
            if len(missingMatch):
                missingMatch = ", ".join([i for i in missingMatch])
                parameters[7].setIDMessage("ERROR", 110158, missingMatch)

            #### Check for Unique Prediction Fields ####
            predFieldsSet = set(predFields)
            if len(predFieldsSet) != len(predFields):
                duplicate = []
                for fieldName in predFieldsSet:
                    if predFields.count(fieldName) != 1 and fieldName not in ['', '#']:
                        duplicate.append(nameAliasMapInputFC[fieldName])
                if len(duplicate) > 0:
                    duplicate = ", ".join(duplicate)
                    parameters[7].setIDMessage("ERROR", 110160, duplicate)

            #### Check for Unique Input Fields ####
            inFieldsAliasSet = set(inFieldAliases)
            if len(inFieldsAliasSet) != len(inFieldAliases):
                duplicate = []
                for inFieldAlias in inFieldsAliasSet:
                    if inFieldAliases.count(inFieldAlias) != 1 and inFieldAlias not in ['', '#']:
                        duplicate.append(inFieldAlias)
                if len(duplicate) > 0:
                    duplicate = ", ".join(duplicate)
                    parameters[7].setIDMessage("ERROR", 110159, duplicate)

            #### Report Any Input Fields Left Unmatched From Ind Vars ####
            indVarAliases = set([nameAliasMapInputFC[indVar] for indVar in parameters[4].valueAsText.split(";") if
                                 indVar in nameAliasMapInputFC])
            missingVars = indVarAliases.difference(inFieldsAliasSet)
            if len(missingVars):
                missingVars = ", ".join([i for i in missingVars])
                parameters[7].setIDMessage("ERROR", 110157, missingVars)
            unexpectedVars = inFieldsAliasSet.difference(indVarAliases)
            hasEmptyField = False
            if '' in unexpectedVars or "#" in unexpectedVars:
                hasEmptyField = True
            unexpectedVars = [v for v in unexpectedVars if v not in ['', '#']]
            if hasEmptyField:
                unexpectedVars.append("''")
            if len(unexpectedVars):
                unexpectedVars = ", ".join(unexpectedVars)
                parameters[7].setIDMessage("ERROR", 110247, unexpectedVars)

        #### Matching Distance VT Errors ####
        if parameters[6].value and parameters[5].value:
            predFields = []
            inDistanceFCs = []
            missingMatch = []
            if parameters[8].value:
                for vtRow in parameters[8].value:
                    predField = vtRow[0]
                    indField = vtRow[1]
                    predFields.append(predField)
                    inDistanceFCs.append(indField)
                    if str(predField) in ["#", '']:
                        missingMatch.append(indField)

            #### Missing Match ####
            if len(missingMatch):
                missingMatch = ", ".join([i for i in missingMatch])
                parameters[8].setIDMessage("ERROR", 110218, missingMatch)

            #### Check for Unique Prediction Fields ####
            predFieldsSet = set(predFields)
            if len(predFieldsSet) != len(predFields):
                duplicate = []
                for fieldName in predFieldsSet:
                    if predFields.count(fieldName) != 1 and fieldName not in ['', '#']:
                        duplicate.append(fieldName)
                if len(duplicate) > 0:
                    duplicate = ", ".join(duplicate)
                    parameters[8].setIDMessage("ERROR", 110220, duplicate)

            #### Check for Unique Input Fields ####
            predDistanceFCsSet = set(inDistanceFCs)
            if len(predDistanceFCsSet) != len(inDistanceFCs):
                duplicate = []
                for fieldName in predDistanceFCsSet:
                    if inDistanceFCs.count(fieldName) != 1 and fieldName not in ['', '#']:
                        duplicate.append(fieldName)
                if len(duplicate) > 0:
                    duplicate = ", ".join(duplicate)
                    parameters[8].setIDMessage("ERROR", 110219, duplicate)

            #### Report Any Input Fields Left Unmatched From Ind Vars ####
            indFCs = set(parameters[5].valueAsText.split(";"))
            missingVars = indFCs.difference(inDistanceFCs)
            if len(missingVars):
                missingVars = ", ".join([i for i in missingVars])
                parameters[8].setIDMessage("ERROR", 110217, missingVars)
            unexpectedFCs = predDistanceFCsSet.difference(indFCs)
            hasEmptyField = False
            if '' in unexpectedFCs or "#" in unexpectedFCs:
                hasEmptyField = True
            unexpectedFCs = [v for v in unexpectedFCs if v not in ['', '#']]
            if hasEmptyField:
                unexpectedFCs.append("''")
            if len(unexpectedFCs):
                unexpectedFCs = ", ".join([i for i in unexpectedFCs])
                parameters[8].setIDMessage("ERROR", 110248, unexpectedFCs)

        #### Must Provide Output Prediction Features ####
        if parameters[6].value and not parameters[9].value:
            parameters[9].setIDMessage("ERROR", 110241)

        return

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import SSDataObject as SSDO
        import GLR

        ### Get parameter values ####
        ARCPY.env.overwriteOutput = True
        inputFC = UTILS.getTextParameter(0, parameters)
        depVarName = UTILS.getTextParameter(1, parameters).upper()
        modelType = UTILS.getTextParameter(2, parameters).upper()
        indVarNames = UTILS.getTextParameter(4, parameters)
        if indVarNames:
            indVarNames = indVarNames.upper().split(";")
        else:
            indVarNames = []
        outputFC = UTILS.getTextParameter(3, parameters)
        outPath, outName = OS.path.split(outputFC)
        distanceFeatures = UTILS.getTextParameter(5, parameters)
        if len(indVarNames) == 0 and distanceFeatures is None:
            ARCPY.AddIDMessage("ERROR", 110254)
            raise SystemExit()

        #### For users with basic license but use ####
        if not checkLicense() and distanceFeatures is not None:
            ARCPY.AddIDMessage("ERROR", 110258)
            raise SystemExit()

        predictInputFC = UTILS.getTextParameter(6, parameters)
        predictVT = parameters[7].value
        matchDistances = UTILS.getTextParameterMatch(8, parameters,
                                                     ["MappingLayerObject", "mp.Layer"])
        predictOutputFC = UTILS.getTextParameter(9, parameters)

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC)
        allVars = [depVarName] + indVarNames
        ssdo.obtainData(ssdo.oidName, allVars, minNumObs=5)

        #### Get Family ####
        family = convertFamilyType[modelType]

        #### Get Distance Features ####
        if distanceFeatures is not None:
            df = WU.DistanceFeatures(ssdo)
            fcList = distanceFeatures.split(";")
            for fc in fcList:
                df.addFeatures(fc.replace("'", ""))
        else:
            df = None

        #### GLR ####
        glr = GLR.GLR(ssdo, depVarName, indVarNames,
                      family=family, distanceFeatures=df)

        #### Report ####
        glr.getReport()

        #### Create Output ####
        GLR.createGLROutputFC(glr, outputFC)

        #### Render Results ####
        if glr.family != "GAUSSIAN":
            if ssdo.shapeType.upper() == "POINT":
                parameters[3].symbology = OS.path.join(pathLayers,
                                                       "GGWR_Points.lyrx")
            else:
                parameters[3].symbology = OS.path.join(pathLayers,
                                                       "GGWR_Polygons.lyrx")
        else:
            if ssdo.shapeType.upper() == "POINT":
                parameters[3].symbology = OS.path.join(pathLayers,
                                                       "GWR_Points.lyrx")
            else:
                parameters[3].symbology = OS.path.join(pathLayers,
                                                       "GWR_Polygons.lyrx")

        #### Prediction ####
        if predictInputFC is not None:
            #### Parse Matching Field Names ####
            predVarNames = []
            if predictVT is not None:
                varEntry = [vRow[0].value for vRow in predictVT]
                predVarNames = [i.upper() for i in varEntry]

            #### Create Prediction SSDataObject ####
            ssdoPred = SSDO.SSDataObject(predictInputFC,
                                         explicitSpatialRef=ssdo.spatialRef)
            ssdoPred.obtainData(ssdoPred.oidName, predVarNames)

            #### Get Matching Distance Features ####
            if matchDistances is not None:
                distEntry = [f[0] for f in matchDistances]
                dfPred = WU.DistanceFeatures(ssdoPred)
                for fc in distEntry:
                    dfPred.addFeatures(fc)
            else:
                dfPred = None

            predictGLR = GLR.PredictGLR(glr)
            predictGLR.createPredictionFC(ssdoPred, predictOutputFC,
                                          indVarNames=predVarNames,
                                          distanceFeatures=dfPred)

            #### Render Predictions ####
            if glr.family == "LOGIT":
                if ssdoPred.shapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points_Binary.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons_Binary.lyrx"
            elif glr.family == "POISSON":
                if ssdoPred.shapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points_Count.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons_Count.lyrx"
            else:
                if ssdoPred.shapeType.upper() == "POINT":
                    predLYR = "GWR_Predict_Points.lyrx"
                else:
                    predLYR = "GWR_Predict_Polygons.lyrx"

            parameters[9].symbology = OS.path.join(pathLayers,
                                                   predLYR)
        else:
            predictGWR = None

        #### Add Charts To The Results ####
        chartList = list()
        depVarNameOrigin = UTILS.getTextParameter(1, parameters)
        indVarNamesOrigin = UTILS.getTextParameter(4, parameters)
        if indVarNamesOrigin:
            indVarNamesOrigin = indVarNamesOrigin.split(";")
        else:
            indVarNamesOrigin = []
        if df:
            indVarNamesOrigin += df.names
        appendVarNames = UTILS.createAppendFieldNames([depVarNameOrigin] + indVarNamesOrigin, outPath)
        chartTitle = ""

        #### Create Scatter Plot Matrix for Xs and Y ####
        smChartFields = []
        if modelType == 'CONTINUOUS' or modelType == 'COUNT':
            smChartFields = [appendVarNames[0]]
        smChartFields.extend(appendVarNames[1:])
        if len(smChartFields) < 3:
            if len(smChartFields) == 2:
                chartTitle = ARCPY.GetIDMessage(84888).format("Relationship")
                sChart1 = ARCPY.Chart(chartTitle)
                sChart1.type = 'scatter'
                sChart1.title = chartTitle
                # sChart1.description = 'desc'
                sChart1.xAxis.field = smChartFields[1]
                sChart1.yAxis.field = [smChartFields[0]]
                sChart1.xAxis.title = smChartFields[1]
                sChart1.yAxis.title = smChartFields[0]
                sChart1.scatter.showTrendLine = True
                chartList.append(sChart1)
        else:
            if len(smChartFields) > 10:
                ARCPY.AddIDMessage("WARNING", 110249, len(smChartFields))
                smChartFields = smChartFields[:10]
            chartTitle = ARCPY.GetIDMessage(84888).format("Relationships")
            smChart = ARCPY.Chart(chartTitle)
            smChart.type = 'scatterMatrix'
            smChart.title = chartTitle
            smChart.scatterMatrix.fields = smChartFields
            smChart.scatterMatrix.showTrendLine = True
            smChart.scatterMatrix.showHistograms = True
            # smChart.scatterMatrix.showAsRSquared = True
            chartList.append(smChart)

        if modelType == 'BINARY':
            #### Create Box Plot for Xs split By Y####
            chartTitle = ARCPY.GetIDMessage(84896)
            bpChart = ARCPY.Chart(ARCPY.GetIDMessage(84896))
            bpChart.type = 'boxPlot'
            bpChart.title = chartTitle
            # bpChart.description = 'desc'
            bpChart.xAxis.field = ""
            bpChart.yAxis.field = appendVarNames[1:]
            # bpChart.xAxis.title = 'Predicted'
            bpChart.yAxis.title = ARCPY.GetIDMessage(84897)
            #### Set Box Plot Properties ####
            bpChart.boxPlot.splitCategory = appendVarNames[0]
            bpChart.boxPlot.splitCategoryAsMeanLine = False
            bpChart.boxPlot.standardizeValues = True
            chartList.append(bpChart)

        #### Create Histograms for Residuals/Deviance Residuals ####
        histChartShowComparisonDistribution = True
        histChartShowMean = True
        histChartXfield = ''
        histChartXTitle = ''
        if modelType == 'CONTINUOUS':
            chartTitle = ARCPY.GetIDMessage(84889)
            histChartXfield = 'STDRESID'
            histChartXTitle = ARCPY.GetIDMessage(84891)
            histChartShowComparisonDistribution = True
            histChartShowMean = True
        elif modelType == 'COUNT':
            chartTitle = ARCPY.GetIDMessage(84890)
            histChartXfield = 'DEV_RESID'
            histChartXTitle = ARCPY.GetIDMessage(84892)
            histChartShowComparisonDistribution = True
            histChartShowMean = True
        elif modelType == 'BINARY':
            chartTitle = ARCPY.GetIDMessage(84890)
            histChartXfield = 'DEV_RESID'
            histChartXTitle = ARCPY.GetIDMessage(84892)
            histChartShowComparisonDistribution = False
            histChartShowMean = False

        histChart = ARCPY.Chart(chartTitle)
        histChart.type = 'histogram'
        histChart.title = chartTitle
        histChart.xAxis.field = histChartXfield
        histChart.xAxis.title = histChartXTitle
        histChart.histogram.showComparisonDistribution = histChartShowComparisonDistribution
        histChart.histogram.showMean = histChartShowMean
        chartList.append(histChart)

        if modelType == 'CONTINUOUS' or modelType == 'COUNT':
            #### Create Scatter Plot for Residuals in CONTINUOUS and COUNT Model ####
            yAxisField = []
            yAxisTitle = ''
            if modelType == 'CONTINUOUS':
                chartTitle = ARCPY.GetIDMessage(84893)
                yAxisField = ['STDRESID']
                yAxisTitle = ARCPY.GetIDMessage(84891)
            elif modelType == 'COUNT':
                chartTitle = ARCPY.GetIDMessage(84894)
                yAxisField = ['DEV_RESID']
                yAxisTitle = ARCPY.GetIDMessage(84892)
            sChart = ARCPY.Chart(chartTitle)
            sChart.type = 'scatter'
            sChart.title = chartTitle
            # sChart.description = 'desc'
            sChart.xAxis.field = 'PREDICTED'
            sChart.yAxis.field = yAxisField
            sChart.xAxis.title = ARCPY.GetIDMessage(84895)
            sChart.yAxis.title = yAxisTitle
            sChart.scatter.showTrendLine = False
            chartList.append(sChart)
        elif modelType == 'BINARY':
            #### Create Bar Chart for Y and Predicted Y ####
            chartTitle = ARCPY.GetIDMessage(84898)
            barChart = ARCPY.Chart(chartTitle)
            barChart.type = "bar"
            barChart.title = chartTitle
            barChart.xAxis.field = "PREDICTED"
            barChart.yAxis.field = ""
            barChart.xAxis.sort = "asc"
            barChart.bar.aggregation = "COUNT"
            barChart.bar.splitCategory = appendVarNames[0]
            chartList.append(barChart)

        parameters[3].charts = chartList
        return


class OrdinaryLeastSquares(object):
    def __init__(self):
        self.label = "Ordinary Least Squares"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060003
        self.params = None
        #### Set Rendering Scheme Dict ####
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Unique ID Field",
                                 name="Unique_ID_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param3 = ARCPY.Parameter(displayName="Dependent Variable",
                                 name="Dependent_Variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.list = ['Short', 'Long', 'Float', 'Double']

        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Explanatory Variables",
                                 name="Explanatory_Variables",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param4.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param4.filter.list = ['Short', 'Long', 'Float', 'Double']

        param4.parameterDependencies = ["Input_Feature_Class"]

        param5 = ARCPY.Parameter(displayName="Coefficient Output Table",
                                 name="Coefficient_Output_Table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Output")
        param5.category = "Additional Options"
        param6 = ARCPY.Parameter(displayName="Diagnostic Output Table",
                                 name="Diagnostic_Output_Table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Output")
        param6.category = "Additional Options"
        param7 = ARCPY.Parameter(displayName="Output Report File",
                                 name="Output_Report_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Output")
        param7.filter.list = ['pdf']
        return [param0, param1, param2, param3, param4, param5, param6, param7]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.setParameterInfo(self.params[0].value)
            else:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    pass

        #### Add Fields ####
        addFields = []

        #### Unique ID Field ####
        if self.params[1].value:
            fieldName = self.params[1].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Dependent Var ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Independent Vars ####
        if self.params[4].value:
            for fieldName in self.params[4].value.exportToString().split(";"):
                if fieldName in self.fieldObjects:
                    addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["Estimated", "Residual", "StdResid"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[2].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        self.params = parameters
        if self.params[7].altered:
            if self.params[7].value:
                #### Check Path to Output Exists ####
                outPath, outName = OS.path.split(self.params[7].value.value)
                if not OS.path.exists(outPath):
                    self.params[7].setIDMessage("ERROR", 436, outPath)

    def setParameterInfo(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            shapeType = desc.ShapeType.upper()
            renderOut = self.renderType[shapeType]
            if renderOut == 0:
                renderLayerFile = "StdResidPoints.lyr"
            elif renderOut == 1:
                renderLayerFile = "StdResidPolylines.lyr"
            else:
                renderLayerFile = "StdResidPolygons.lyr"

            fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                                   "Layers", renderLayerFile)
            self.params[2].symbology = fullRLF
            for field in desc.fields:
                self.fieldObjects[field.name] = field
        except:
            pass

    def execute(self, parameters, messages):
        import OLS as SSOLS

        #### Get User Provided Inputs ####
        inputFC = UTILS.getTextParameter(0, parameters)
        masterField = UTILS.getTextParameter(1, parameters)
        outputFC = UTILS.getTextParameter(2, parameters)
        depVarName = UTILS.getTextParameter(3, parameters).upper()
        indVarNames = UTILS.getTextParameter(4, parameters).upper()
        indVarNames = indVarNames.split(";")

        #### Get User Provided Optional Output Table Parameters ####
        coefTable = UTILS.getTextParameter(5, parameters)
        diagTable = UTILS.getTextParameter(6, parameters)
        reportFile = UTILS.getTextParameter(7, parameters)

        #### Create SSDataObject ####
        fieldList = [depVarName] + indVarNames
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(masterField, fieldList, minNumObs=5)

        #### Call OLS Class for Regression ####
        ols = SSOLS.OLS(ssdo, depVarName, indVarNames)

        #### Print Results ####
        ols.report()

        #### Spatial Autocorrelation Warning ####
        ARCPY.AddIDMessage("WARNING", 851)

        #### Create Output Feature Class ####
        ols.outputResults(outputFC, parameters)
        outFCBase = OS.path.basename(outputFC).split(".")[0]

        #### Construct Output Database Tables if User-Specified ####
        if coefTable:
            #### Resolve Complete Table Name ####
            coefPath, coefName = OS.path.split(coefTable)
            if coefPath == "":
                coefPath = OS.path.split(ssdo.catPath)[0]
                coefTable = OS.path.join(coefPath, coefName)

            #### Check that Table Will not Overwrite OutputFC ####
            if OS.path.basename(coefTable).split(".")[0] == outFCBase:
                ARCPY.AddIDMessage("WARNING", 943, coefTable)
            else:
                ols.createCoefficientTable(coefTable)

        if diagTable:
            #### Resolve Complete Table Name ####
            diagPath, diagName = OS.path.split(diagTable)
            if diagPath == "":
                diagPath = OS.path.split(ssdo.catPath)[0]
                diagTable = OS.path.join(diagPath, diagName)

            #### Check that Table Will not Overwrite OutputFC ####
            if OS.path.basename(diagTable).split(".")[0] == outFCBase:
                ARCPY.AddIDMessage("WARNING", 943, diagTable)
            else:
                ols.createDiagnosticTable(diagTable)

        #### Create Report File ####
        if reportFile:
            ols.createOutputGraphic(reportFile)


class ConvertSpatialWeightsMatrixtoTable(object):
    def __init__(self):
        self.label = "Convert Spatial Weights Matrix to Table"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Utilities"
        self.helpContext = 9050009
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Spatial Weights Matrix File",
                                 name="Input_Spatial_Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['swm', 'gwt']

        param1 = ARCPY.Parameter(displayName="Output Table",
                                 name="Output_Table",
                                 datatype="DETable",
                                 parameterType="Required",
                                 direction="Output")

        return [param0, param1]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        #### Add Output Field Schema ####
        addFields = []
        swmFile = self.params[0].value
        if swmFile:
            #### Unicode / Scratch Folder Safe Path ####
            swmFile = swmFile.value
            if swmFile.upper().count('%SCRATCHFOLDER%'):
                swmFile = ARCPY.env.scratchFolder + swmFile[15:]

        if not self.params[0].hasBeenValidated:
            try:
                swm = WU.SWMReader(swmFile)
                masterField = swm.masterField
                swm.close()
                newField = ARCPY.Field()
                newField.name = masterField
                newField.type = "LONG"
                addFields.append(newField)
            except:
                #### Cannot Read SWM Header, Perhaps in Model ####
                pass

            fieldNames = ["NID", "WEIGHT"]
            for ind, field in enumerate(fieldNames):
                newField = ARCPY.Field()
                newField.name = field
                if ind == 0:
                    newField.type = "LONG"
                else:
                    newField.type = "DOUBLE"
                addFields.append(newField)
            self.params[1].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        self.params = parameters
        #### Invalid SWM File ####
        fields = self.params[1].schema.additionalFields
        if not len(fields):
            swmFile = str(self.params[0].value)
            self.params[0].clearMessage()
            self.params[0].setIDMessage("ERROR", 977, swmFile)

    def execute(self, parameters, messages):
        import SWM2Table as SWMT
        swmFile = UTILS.getTextParameter(0, parameters)
        outputTable = UTILS.getTextParameter(1, parameters)
        SWMT.swm2Table(swmFile, outputTable, parameters)


class MedianCenter(object):
    def __init__(self):
        self.label = "Median Center"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Measuring Geographic Distributions"
        self.helpContext = 9040006
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Weight Field",
                                 name="Weight_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']
        param2.parameterDependencies = ["Input_Feature_Class"]

        param3 = ARCPY.Parameter(displayName="Case Field",
                                 name="Case_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['Short', 'Long', 'Text', 'Date']
        param3.parameterDependencies = ["Input_Feature_Class"]

        param4 = ARCPY.Parameter(displayName="Attribute Field",
                                 name="Attribute_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param4.filter.list = ['Short', 'Long', 'Float', 'Double']
        param4.parameterDependencies = ["Input_Feature_Class"]

        return [param0, param1, param2, param3, param4]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            # if not self.params[0].isInputValueDerived():
            try:
                desc = ARCPY.Describe(self.params[0].value)
                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                pass

        #### Add Fields ####
        addFields = []

        #### Weight Field ####
        if self.params[2].value:
            fieldName = self.params[2].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Case Field ####
        if self.params[3].value:
            fieldName = self.params[3].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Att Fields ####
        if self.params[4].value:
            for fieldName in self.params[4].value.exportToString().split(";"):
                if fieldName in self.fieldObjects:
                    addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["XCoord", "YCoord"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields
        self.params[1].schema.featureTypeRule = "AsSpecified"
        self.params[1].schema.featureType = "Simple"
        self.params[1].schema.geometryTypeRule = "AsSpecified"
        self.params[1].schema.geometryType = "Point"

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        import MedianCenter as MEC
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        weightField = UTILS.getTextParameter(2, parameters, fieldName=True)
        caseField = UTILS.getTextParameter(3, parameters, fieldName=True)
        attFields = UTILS.getTextParameter(4, parameters, fieldName=True)

        fieldList = []
        if weightField:
            fieldList.append(weightField)
        if caseField:
            fieldList.append(caseField)
        if attFields:
            attFields = attFields.split(";")
            fieldList = fieldList + attFields

        #### Populate SSDO with Data ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=1,
                        requireGeometry=ssdo.complexFeature)

        #### Run Analysis ####
        mc = MEC.MedianCenter(ssdo, weightField=weightField,
                              caseField=caseField, attFields=attFields)

        #### Create Output ####
        mc.createOutput(outputFC, parameters)


class GroupingAnalysis(object):
    def __init__(self):
        self.label = "Grouping Analysis"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030004
        self.maxNumGroups = 15
        self.maxNumVars = 15
        self.allSpaceTypes = ["CONTIGUITY_EDGES_ONLY",
                              "CONTIGUITY_EDGES_CORNERS",
                              "DELAUNAY_TRIANGULATION",
                              "K_NEAREST_NEIGHBORS",
                              "GET_SPATIAL_WEIGHTS_FROM_FILE",
                              "NO_SPATIAL_CONSTRAINT"]
        self.subSpaceTypes = ["DELAUNAY_TRIANGULATION",
                              "K_NEAREST_NEIGHBORS",
                              "GET_SPATIAL_WEIGHTS_FROM_FILE",
                              "NO_SPATIAL_CONSTRAINT"]
        self.distSetTypes = ["K_NEAREST_NEIGHBORS",
                             "CONTIGUITY_EDGES_ONLY",
                             "CONTIGUITY_EDGES_CORNERS"]
        self.allowGroupSet = True

        #### Set Rendering Scheme Dict ####
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Unique ID Field",
                                 name="Unique_ID_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long']
        param1.parameterDependencies = ["Input_Features"]

        param2 = ARCPY.Parameter(displayName="Output Feature Class",
                                 name="Output_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output",
                                 )

        param3 = ARCPY.Parameter(displayName="Number of Groups",
                                 name="Number_of_Groups",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")

        param3.value = 2

        param4 = ARCPY.Parameter(displayName="Analysis Fields",
                                 name="Analysis_Fields",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param4.filter.list = ['Short', 'Long', 'Float', 'Double', 'Date']
        param4.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param4.parameterDependencies = ["Input_Features"]

        param5 = ARCPY.Parameter(displayName="Spatial Constraints",
                                 name="Spatial_Constraints",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param5.filter.type = "ValueList"
        param5.filter.list = ['CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'DELAUNAY_TRIANGULATION', 'K_NEAREST_NEIGHBORS',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE', 'NO_SPATIAL_CONSTRAINT']

        param6 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "ValueList"
        param6.filter.list = ['EUCLIDEAN', 'MANHATTAN']
        param6.value = 'EUCLIDEAN'

        param7 = ARCPY.Parameter(displayName="Number of Neighbors",
                                 name="Number_of_Neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param7.value = 8

        param8 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['swm', 'gwt']

        param9 = ARCPY.Parameter(displayName="Initialization Method",
                                 name="Initialization_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param9.filter.type = "ValueList"
        param9.filter.list = ['FIND_SEED_LOCATIONS', 'GET_SEEDS_FROM_FIELD',
                              'USE_RANDOM_SEEDS']
        param9.value = 'FIND_SEED_LOCATIONS'

        param10 = ARCPY.Parameter(displayName="Initialization Field",
                                  name="Initialization_Field",
                                  datatype="Field",
                                  parameterType="Optional",
                                  direction="Input")
        param10.filter.list = ['Short', 'Long']
        param10.parameterDependencies = ["Input_Features"]
        param10.enabled = False

        param11 = ARCPY.Parameter(displayName="Output Report File",
                                  name="Output_Report_File",
                                  datatype="DEFile",
                                  parameterType="Optional",
                                  direction="Output")
        param11.filter.list = ['pdf']

        param12 = ARCPY.Parameter(displayName="Evaluate Optimal Number of Groups",
                                  name="Evaluate_Optimal_Number_of_Groups",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param12.filter.list = ['EVALUATE', 'DO_NOT_EVALUATE']
        param12.value = False

        param13 = ARCPY.Parameter(displayName="Output_FStat",
                                  name="Output_FStat",
                                  datatype="GPDouble",
                                  parameterType="Derived",
                                  direction="Output")

        param14 = ARCPY.Parameter(displayName="Max_FStat_Group",
                                  name="Max_FStat_Group",
                                  datatype="GPLong",
                                  parameterType="Derived",
                                  direction="Output")

        param15 = ARCPY.Parameter(displayName="Max_FStat",
                                  name="Max_FStat",
                                  datatype="GPDouble",
                                  parameterType="Derived",
                                  direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7,
                param8, param9, param10, param11, param12, param13, param14, param15]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        #### Validate Polygon Types and Fields ####
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    shapeType = desc.shapeType.upper()
                    if shapeType == "POLYGON":
                        self.params[5].filter.list = self.allSpaceTypes
                    else:
                        self.params[5].filter.list = self.subSpaceTypes
                    self.setOutputSymbology(shapeType)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    self.params[5].filter.list = self.allSpaceTypes

            else:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    for field in desc.fields:
                        self.fieldObjects[field.name] = field
                except:
                    self.params[5].filter.list = self.allSpaceTypes
                    pass
        #### Default Number of Groups ####
        if not self.params[3].value:
            self.params[3].value = 2

        #### Validate Space Concepts ####
        spaceConcept = self.params[5].value
        if spaceConcept:
            spaceConcept = spaceConcept.upper()

        if spaceConcept == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            self.params[8].enabled = True
        else:
            self.params[8].enabled = False

        if spaceConcept in self.distSetTypes:
            self.params[6].enabled = True
            self.params[7].enabled = True
            numNeighs = self.params[7].value
            if not numNeighs:
                if spaceConcept == "K_NEAREST_NEIGHBORS":
                    self.params[7].value = 8
                else:
                    self.params[7].value = 0
        else:
            self.params[6].enabled = False
            self.params[7].enabled = False
            self.params[7].value = None

        initApproach = self.params[9].value
        if spaceConcept == "NO_SPATIAL_CONSTRAINT":
            self.params[9].enabled = True
            if initApproach == "GET_SEEDS_FROM_FIELD":
                self.params[10].enabled = True
            else:
                self.params[10].enabled = False
        else:
            self.params[9].enabled = False
            self.params[10].enabled = False

        if self.params[0].altered or self.params[2].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                if self.params[2].value:
                    output = self.params[2].value.value
                else:
                    output = None
                outSpatRef = returnOutputSpatialRef(desc.SpatialReference,
                                                    output)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[6].enabled = False
                else:
                    self.params[6].enabled = True
            except:
                pass

        #### Assess Whether to Allow PDF Report ####
        #### Set to *15 Variables/Groups ####
        numFactors = []
        numGroups = self.params[3].value
        allowReport = True
        if numGroups:
            if numGroups > self.maxNumGroups:
                allowReport = False

        varNames = self.params[4].value
        if varNames:
            numVars = str(varNames).count(";") + 1
            if numVars > self.maxNumVars:
                allowReport = False
        if allowReport:
            self.params[11].enabled = True
        else:
            self.params[11].enabled = False

        #### Add Fields ####
        addFields = []

        #### Unique ID Field ####
        if self.params[1].value:
            fieldName = None
            try:
                fieldName = self.params[1].value.value
            except:
                fieldName = self.params[1].value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        #### Analysis Field(s) ####
        if self.params[4].value:
            for fieldName in self.params[4].value.exportToString().split(";"):
                if fieldName in self.fieldObjects:
                    addFields.append(self.fieldObjects[fieldName])

        #### Seed Field ####
        if self.params[10].value:
            fieldName = None
            try:
                fieldName = self.params[10].value.value
            except:
                fieldName = self.params[10].value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["SS_GROUP"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "FLOAT"
            addFields.append(newField)
        self.params[2].schema.additionalFields = addFields

        #### Set Derived Output to Empty ####
        self.params[13].value = None
        self.params[14].value = None
        self.params[15].value = None
        return

    def updateMessages(self, parameters):
        self.params = parameters
        numGroups = self.params[3].value
        if numGroups < 2:
            self.params[3].setIDMessage("ERROR", 1221, 2)

        spaceConcept = self.params[5].value
        if spaceConcept:
            spaceConcept = spaceConcept.upper()

        if spaceConcept in self.distSetTypes:
            numNeighs = self.params[7].value
            if spaceConcept == "K_NEAREST_NEIGHBORS":
                warnNumber = 2
            else:
                warnNumber = 0
            if numNeighs < warnNumber:
                self.params[7].setIDMessage("ERROR", 1219, warnNumber)

        #### Must Provide Seed Definition Field ####
        initApproach = self.params[9].value
        if spaceConcept == "NO_SPATIAL_CONSTRAINT":
            if initApproach == "GET_SEEDS_FROM_FIELD":
                if not self.params[10].value:
                    self.params[10].setIDMessage("ERROR", 1327)

        if self.params[11].altered:
            if self.params[11].value:
                #### Check Path to Output Exists ####
                outPath, outName = OS.path.split(self.params[11].value.value)
                if not OS.path.exists(outPath):
                    self.params[11].setIDMessage("ERROR", 436, outPath)
        return

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        if renderOut == 0:
            renderLayerFile = "GroupPoints.lyr"
        elif renderOut == 1:
            renderLayerFile = "GroupPolylines.lyr"
        else:
            renderLayerFile = "GroupPolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[2].symbology = fullRLF

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import Partition as PAR

        inputFC = UTILS.getTextParameter(0, parameters)
        masterField = UTILS.getTextParameter(1, parameters).upper()
        outputFC = UTILS.getTextParameter(2, parameters)

        #### User Defined Number of Groups ####
        kPartitions = UTILS.getNumericParameter(3, parameters)

        analysisFields = UTILS.getTextParameter(4, parameters).upper()
        analysisFields = analysisFields.split(";")

        #### Conceptualization ####
        spaceConcept = UTILS.getTextParameter(5, parameters).upper()

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = UTILS.getTextParameter(6, parameters).upper().replace(" ", "_")
        if distanceConcept == "#" or distanceConcept == "":
            distanceConcept = "EUCLIDEAN"

        #### Number of Neighbors ####
        numNeighs = UTILS.getNumericParameter(7, parameters)

        #### Quick Validation of k-nearest ####
        if spaceConcept == "K_NEAREST_NEIGHBORS":
            if numNeighs <= 0:
                ARCPY.AddIDMessage("ERROR", 976)
                raise SystemExit()

        #### Spatial Weights Matrix File ####
        weightsFile = UTILS.getTextParameter(8, parameters)
        useWeightsFile = spaceConcept == "GET_SPATIAL_WEIGHTS_FROM_FILE"
        if not weightsFile and useWeightsFile:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and not useWeightsFile:
            ARCPY.AddIDMessage("WARNING", 925)
            weightsFile = None

        #### Initialization Approach ####
        initMethod = UTILS.getTextParameter(9, parameters)
        if initMethod == "#" or initMethod == "":
            initMethod = "FIND_SEED_LOCATIONS"

        #### Initial Seed/Solution Field ####
        fieldList = [i for i in analysisFields]
        initField = UTILS.getTextParameter(10, parameters, fieldName=True)
        if initField is not None:
            fieldList.append(initField)

        if spaceConcept == "NO_SPATIAL_CONSTRAINT":
            if initMethod == "GET_SEEDS_FROM_FIELD" and initField is None:
                ARCPY.AddIDMessage("ERROR", 1327)
                raise SystemExit()

        #### Report File ####
        reportFile = UTILS.getTextParameter(11, parameters)
        if reportFile == "#" or reportFile == "":
            reportFile = None
        else:
            #### Validate Number of Vars/Groups for Report (Max 15) ####
            if kPartitions > self.maxNumGroups or len(analysisFields) > self.maxNumVars:
                reportFile = None
                ARCPY.AddIDMessage("WARNING", 1328)

        #### Permutations ####
        optimalBool = parameters[12].value

        #### Warn About Chordal Bool ####
        if spaceConcept in ["NO_SPATIAL_CONSTRAINT",
                            "GET_SPATIAL_WEIGHTS_FROM_FILE"]:
            useChordal = False
        else:
            useChordal = True

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=useChordal)

        #### Populate SSDO with Data ####
        if spaceConcept not in ["NO_SPATIAL_CONSTRAINT", "GET_SPATIAL_WEIGHTS_FROM_FILE"]:
            ssdo.obtainData(masterField, fieldList, minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, fieldList, minNumObs=3,
                            warnNumObs=30)

        #### Execute ####
        part = PAR.Partition(ssdo, analysisFields, spaceConcept=spaceConcept,
                             distConcept=distanceConcept, numNeighs=numNeighs,
                             weightsFile=weightsFile, initMethod=initMethod,
                             kPartitions=kPartitions, initField=initField,
                             optimizeGroups=optimalBool)

        #### Report ####
        pdfOutput = part.report(fileName=reportFile, optimal=optimalBool)

        #### Create OutputFC ####
        part.createOutput(outputFC, parameters)

        fStat = ""
        if ~SSDO.NUM.isnan(part.fStat):
            out = fStat

        #### Optimal Number of Partitions ####
        if optimalBool:
            #### Get FStat Info ####
            maxInd, maxGroup, maxFStat = part.fStatInfo

            #### Plot Results ####
            if reportFile:
                if part.aspatial:
                    PAR.plotFStats(pdfOutput, part.groupList, part.fStatRes,
                                   maxInd=maxInd)
                else:
                    PAR.plotFStatsSpatial(pdfOutput, part.groupList, part.fStatRes,
                                          maxInd=maxInd)

            #### Set Derived Output ####
            UTILS.setParameterAsText(13, fStat, parameters)
            UTILS.setParameterAsText(14, maxGroup, parameters)
            UTILS.setParameterAsText(15, maxFStat, parameters)

        else:
            #### Set All Derived F-Stats to Main Partition Values ####
            UTILS.setParameterAsText(13, fStat, parameters)
            UTILS.setParameterAsText(14, "", parameters)
            UTILS.setParameterAsText(15, "", parameters)
        return


class ExploratoryRegression(object):
    def __init__(self):
        self.label = "Exploratory Regression"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060005
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Dependent Variable",
                                 name="Dependent_Variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']

        param1.parameterDependencies = ["Input_Features"]

        param2 = ARCPY.Parameter(displayName="Candidate Explanatory Variables",
                                 name="Candidate_Explanatory_Variables",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param2.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']

        param2.parameterDependencies = ["Input_Features"]

        param3 = ARCPY.Parameter(displayName="Weights Matrix File",
                                 name="Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ['swm', 'gwt']
        param4 = ARCPY.Parameter(displayName="Output Report File",
                                 name="Output_Report_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Output")
        param4.filter.list = ['txt']
        param5 = ARCPY.Parameter(displayName="Output Results Table",
                                 name="Output_Results_Table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Output")

        param6 = ARCPY.Parameter(displayName="Maximum Number of Explanatory Variables",
                                 name="Maximum_Number_of_Explanatory_Variables",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param6.category = "Search Criteria"
        # param6.filter.type = "Range"
        # param6.filter.list = [1,20]
        param6.value = 5

        param7 = ARCPY.Parameter(displayName="Minimum Number of Explanatory Variables",
                                 name="Minimum_Number_of_Explanatory_Variables",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param7.category = "Search Criteria"
        # param7.filter.type = "Range"
        # param7.filter.list = [1,20]
        param7.value = 1

        param8 = ARCPY.Parameter(displayName="Minimum Acceptable Adj R Squared",
                                 name="Minimum_Acceptable_Adj_R_Squared",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param8.category = "Search Criteria"
        param8.filter.type = "Range"
        param8.filter.list = [0.0, 1.0]
        param8.value = 0.5

        param9 = ARCPY.Parameter(displayName="Maximum Coefficient p value Cutoff",
                                 name="Maximum_Coefficient_p_value_Cutoff",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param9.category = "Search Criteria"
        param9.filter.type = "Range"
        param9.filter.list = [0.0, 1.0]
        param9.value = 0.05

        param10 = ARCPY.Parameter(displayName="Maximum VIF Value Cutoff",
                                  name="Maximum_VIF_Value_Cutoff",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")
        param10.category = "Search Criteria"
        param10.filter.type = "Range"
        param10.filter.list = [0.0, 99999999]
        param10.value = 7.5

        param11 = ARCPY.Parameter(displayName="Minimum Acceptable Jarque Bera p value",
                                  name="Minimum_Acceptable_Jarque_Bera_p_value",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")
        param11.category = "Search Criteria"
        param11.filter.type = "Range"
        param11.filter.list = [0.0, 1.0]
        param11.value = 0.1

        param12 = ARCPY.Parameter(displayName="Minimum Acceptable Spatial Autocorrelation p value",
                                  name="Minimum_Acceptable_Spatial_Autocorrelation_p_value",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")
        param12.category = "Search Criteria"
        param12.filter.type = "Range"
        param12.filter.list = [0.0, 1.0]
        param12.value = 0.1

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11,
                param12]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        #### Set Default Values ####
        if not self.params[6].value:
            self.params[6].value = 5
        if not self.params[7].value:
            self.params[7].value = 1
        if self.params[8].value == None:
            self.params[8].value = .5
        if self.params[9].value == None:
            self.params[9].value = .05
        if self.params[10].value == None:
            self.params[10].value = 7.5
        if self.params[11].value == None:
            self.params[11].value = .1
        if self.params[12].value == None:
            self.params[12].value = .1

    def updateMessages(self, parameters):
        self.params = parameters
        #### Assure Min Less Than Max ####
        value6 = int(self.params[6].value)
        value7 = int(self.params[7].value)
        if value7 > value6:
            self.params[7].setIDMessage("ERROR", 1220)

        if self.params[4].altered:
            if self.params[4].value:
                #### Check Path to Output Exists ####
                outPath, outName = OS.path.split(self.params[4].value.value)
                if not OS.path.exists(outPath):
                    self.params[4].setIDMessage("ERROR", 436, outPath)

        if self.params[6].altered:
            if self.params[6].value:
                n = int(self.params[6].value)
                if not 1 <= n <= 20:
                    self.params[6].setIDMessage("ERROR", 854, 1, 20)

        if self.params[7].altered:
            if self.params[7].value:
                n = int(self.params[7].value)
                if not 1 <= n <= 20:
                    self.params[7].setIDMessage("ERROR", 854, 1, 20)

    def execute(self, parameters, messages):
        import ExploratoryRegression as ER
        from scipy.special import comb as COMB

        #### Get User Provided Inputs ####
        ARCPY.env.overwriteOutput = True
        inputFC = UTILS.getTextParameter(0, parameters)
        dependentVar = UTILS.getTextParameter(1, parameters).upper()
        independentVarsReg = UTILS.getTextParameter(2, parameters)
        independentVars = independentVarsReg.upper().split(";")
        weightsFile = UTILS.getTextParameter(3, parameters)

        #### Optional Output ####
        outputReportFile = UTILS.getTextParameter(4, parameters)
        outputTable = UTILS.getTextParameter(5, parameters)

        #### Search Criterion ####
        maxIndVars = UTILS.getNumericParameter(6, parameters)
        minIndVars = UTILS.getNumericParameter(7, parameters)
        minR2 = UTILS.getNumericParameter(8, parameters, defualt="FLOAT")
        maxCoef = UTILS.getNumericParameter(9, parameters, defualt="FLOAT")
        maxVIF = UTILS.getNumericParameter(10, parameters, defualt="FLOAT")
        minJB = UTILS.getNumericParameter(11, parameters, defualt="FLOAT")
        minMI = UTILS.getNumericParameter(12, parameters, defualt="FLOAT")

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### MasterField Can Not Be The Dependent Variable ####
        if masterField == dependentVar:
            ARCPY.AddIDMessage("ERROR", 945, masterField,
                               ARCPY.GetIDMessage(84112))
            raise SystemExit()

        #### Remove the MasterField from Independent Vars ####
        if masterField in independentVars:
            independentVars.remove(masterField)
            ARCPY.AddIDMessage("WARNING", 736, masterField)

        #### Remove the Dependent Variable from Independent Vars ####
        if dependentVar in independentVars:
            independentVars.remove(dependentVar)
            ARCPY.AddIDMessage("WARNING", 850, dependentVar)

        #### Raise Error If No Independent Vars ####
        if not len(independentVars):
            ARCPY.AddIDMessage("ERROR", 737)
            raise SystemExit()

        #### Obtain Data ####
        allVars = [dependentVar] + independentVars

        #### Test is the number of  regression is too large ####
        regressionCountLimit = 1e6
        regressionCountSum = 0
        for k in range(minIndVars, maxIndVars + 1, 1):
            regressionCount = COMB(len(independentVars), k)
            if regressionCount > regressionCountLimit:
                ARCPY.AddIDMessage("ERROR", 110263, regressionCountLimit)
                raise SystemExit()
            regressionCountSum += regressionCount
        if regressionCountSum > regressionCountLimit:
            ARCPY.AddIDMessage("ERROR", 110263, regressionCountLimit)
            raise SystemExit()

        #### Populate SSDO with Data ####
        if not weightsFile:
            ssdo.obtainData(masterField, allVars, minNumObs=5,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, allVars, minNumObs=5,
                            warnNumObs=30)

        exploreRegress = ER.ExploratoryRegression(ssdo, dependentVar,
                                                  independentVars,
                                                  weightsFile=weightsFile,
                                                  outputReportFile=outputReportFile,
                                                  outputTable=outputTable,
                                                  maxIndVars=maxIndVars,
                                                  minIndVars=minIndVars,
                                                  minR2=minR2, maxCoef=maxCoef,
                                                  maxVIF=maxVIF, minJB=minJB,
                                                  minMI=minMI)

        #### Assure Table is Added to TOC ####
        if outputTable:
            if exploreRegress.dbf:
                UTILS.setParameterAsText(5, exploreRegress.outputTable, parameters)


class IncrementalSpatialAutocorrelation(object):
    def __init__(self):
        self.label = "Incremental Spatial Autocorrelation"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Analyzing Patterns"
        self.helpContext = 9010005
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Input Field",
                                 name="Input_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long', 'Float', 'Double']

        param1.parameterDependencies = ["Input_Features"]

        param2 = ARCPY.Parameter(displayName="Number of Distance Bands",
                                 name="Number_of_Distance_Bands",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "Range"
        param2.filter.list = [2, 30]
        param2.value = 10

        param3 = ARCPY.Parameter(displayName="Beginning Distance",
                                 name="Beginning_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.type = "Range"
        param3.filter.list = [0, 999999999]
        param4 = ARCPY.Parameter(displayName="Distance Increment",
                                 name="Distance_Increment",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.type = "Range"
        param4.filter.list = [0.000000001, 999999999]

        param5 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param5.filter.type = "ValueList"

        param5.filter.list = ['EUCLIDEAN', 'MANHATTAN']

        param5.value = 'EUCLIDEAN'

        param6 = ARCPY.Parameter(displayName="Row Standardization",
                                 name="Row_Standardization",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.list = ['ROW_STANDARDIZATION', 'NO_STANDARDIZATION']

        param6.value = True

        param7 = ARCPY.Parameter(displayName="Output Table",
                                 name="Output_Table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Output")

        param8 = ARCPY.Parameter(displayName="Output Report File",
                                 name="Output_Report_File",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Output")
        param8.filter.list = ['pdf']
        param9 = ARCPY.Parameter(displayName="First Peak",
                                 name="First_Peak",
                                 datatype="GPDouble",
                                 parameterType="Derived",
                                 direction="Output")

        param10 = ARCPY.Parameter(displayName="Max Peak",
                                  name="Max_Peak",
                                  datatype="GPDouble",
                                  parameterType="Derived",
                                  direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        if self.params[0].altered:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                outSpatRef = setEnvSpatialReference(desc.SpatialReference)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[5].enabled = False
                else:
                    self.params[5].enabled = True
            except:
                pass

        nIncrements = self.params[2].value
        if not nIncrements:
            self.params[2].value = 10

        #### Set Default Peak Distances to Empty ####
        self.params[9].value = None
        self.params[10].value = None

        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import SSUtilities as UTILS
        import SSDataObject as SSDO
        import MoransI_Increment as MI
        import WeightsUtilities as WU

        #### Input Features and Variable ####
        inputFC = UTILS.getTextParameter(0, parameters)
        varName = UTILS.getTextParameter(1, parameters).upper()

        #### Number of Distance Thresholds ####
        nIncrements = UTILS.getNumericParameter(2, parameters)
        if nIncrements > 30:
            nIncrements = 30

        #### Starting Distance ####
        begDist = UTILS.getNumericParameter(3, parameters)
        if begDist:
            begDist = float(begDist)

        #### Step Distance ####
        dIncrement = UTILS.getNumericParameter(4, parameters)
        if dIncrement:
            dIncrement = float(dIncrement)

        #### EUCLIDEAN or MANHATTAN ####
        distanceConcept = UTILS.getTextParameter(5, parameters).upper().replace(" ", "_")
        concept = WU.conceptDispatch[distanceConcept]

        #### Row Standardized ####
        rowStandard = parameters[6].value

        #### Output Table ####
        outputTable = UTILS.getTextParameter(7, parameters)

        #### Report File ####
        reportFile = UTILS.getTextParameter(8, parameters)

        #### Create a Spatial Stats Data Object (SSDO) ####
        ssdo = SSDO.SSDataObject(inputFC, useChordal=True)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo)

        #### Populate SSDO with Data ####
        ssdo.obtainData(masterField, [varName], minNumObs=4,
                        requireSearch=True, warnNumObs=30)

        #### Run Analysis ####
        gi = MI.GlobalI_Step(ssdo, varName, nIncrements=nIncrements,
                             begDist=begDist, dIncrement=dIncrement,
                             concept=concept, rowStandard=rowStandard)

        #### Report Results ####
        reportTable = gi.report()

        #### Optionally Create Output ####
        if outputTable:
            outputTable, dbf = gi.createOutput(outputTable)
            if dbf:
                UTILS.setParameterAsText(7, outputTable, parameters)

        if reportFile:
            gi.createOutputGraphic(reportFile, gi.firstPeakInd, gi.maxPeakInd)

        #### Set Peak Distances ####
        firstPeak = gi.firstPeakDistance
        if firstPeak is None:
            firstPeak = ""
        UTILS.setParameterAsText(9, firstPeak, parameters)

        maxPeak = gi.maxPeakDistance
        if maxPeak is None:
            maxPeak = ""
        UTILS.setParameterAsText(10, maxPeak, parameters)


class OptimizedHotSpotAnalysis(object):
    def __init__(self):
        self.label = "Optimized Hot Spot Analysis"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030005
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}
        self.aggTypes = {"SNAP_NEARBY_INCIDENTS_TO_CREATE_WEIGHTED_POINTS": 0,
                         "COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS": 1,
                         "COUNT_INCIDENTS_WITHIN_AGGREGATION_POLYGONS": 2,
                         "COUNT_INCIDENTS_WITHIN_HEXAGON_POLYGONS": 3}
        self.fieldObjects = {}
        self.oidName = None
        self.shapeType = None
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point', 'Multipoint', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="Output_Features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Analysis Field",
                                 name="Analysis_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']
        param2.parameterDependencies = ["Input_Features"]

        param3 = ARCPY.Parameter(displayName="Incident Data Aggregation Method",
                                 name="Incident_Data_Aggregation_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS', 'COUNT_INCIDENTS_WITHIN_HEXAGON_POLYGONS',
                              'COUNT_INCIDENTS_WITHIN_AGGREGATION_POLYGONS',
                              'SNAP_NEARBY_INCIDENTS_TO_CREATE_WEIGHTED_POINTS']

        param3.value = 'COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS'

        param3.enabled = False

        param4 = ARCPY.Parameter(displayName="Bounding Polygons Defining Where Incidents Are Possible",
                                 name="Bounding_Polygons_Defining_Where_Incidents_Are_Possible",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Polygon']
        param4.enabled = False

        param5 = ARCPY.Parameter(displayName="Polygons For Aggregating Incidents Into Counts",
                                 name="Polygons_For_Aggregating_Incidents_Into_Counts",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param5.filter.list = ['Polygon']
        param5.enabled = False

        param6 = ARCPY.Parameter(displayName="Density Surface",
                                 name="Density_Surface",
                                 datatype="DERasterDataset",
                                 parameterType="Optional",
                                 direction="Output")

        param6.enabled = False

        param7 = ARCPY.Parameter(displayName="Cell Size",
                                 name="Cell_Size",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = supportDist
        param7.category = "Override Settings"
        param8 = ARCPY.Parameter(displayName="Distance Band",
                                 name="Distance_Band",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = supportDist
        param8.category = "Override Settings"

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""

        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            if self.params[0].value:
                self.setParameterInfo(self.params[0].value)

        self.params[6].enabled = 0

        if self.shapeType in [None, "POLYGON"]:
            self.params[3].enabled = 0
            self.params[4].enabled = 0
            self.params[5].enabled = 0
            self.params[7].enabled = 0
        else:
            #### For Points ####
            fieldName = self.params[2].value
            aggMethod = self.params[3].value
            self.params[7].enabled = 1

            if fieldName:
                #### If Marked, Allow Density, No Agg Method ####
                self.params[3].enabled = 0
                self.params[4].enabled = 0
                self.params[5].enabled = 0
            else:
                #### If Unmarked, Allow Poly FCs ####
                self.params[3].enabled = 1

                if aggMethod.upper() not in self.aggTypes:
                    aggMethod = None

                if aggMethod:
                    aggType = self.aggTypes[aggMethod.upper()]
                    if aggType == 2:
                        #### Allow Polygons for Counts ####
                        self.params[5].enabled = 1
                    else:
                        self.params[5].enabled = 0

                    if aggType == 1 or aggType == 3:
                        #### Allow Bounding Polygons for Fishnet ####
                        self.params[4].enabled = 1
                        self.params[7].enabled = 1
                    else:
                        self.params[4].enabled = 0
                        self.params[7].enabled = 0
                elif aggMethod is not None:
                    self.params[4].enabled = 0
                    self.params[5].enabled = 0

        #### Add Fields ####
        addFields = []

        #### Result Fields ####
        fieldNames = ["GiZScore", "GiPValue", "Gi_Bin"]
        fieldTypes = ["DOUBLE", "DOUBLE", "LONG"]

        #### Analysis Field ####
        if self.params[2].value:
            self.params[7].enabled = 0

            fieldName = None
            try:
                fieldName = self.params[1].value.value
            except:
                fieldName = self.params[1].value

            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])
        else:
            self.params[7].enabled = 1
            aggMethod = self.params[3].value

            if aggMethod.upper() not in self.aggTypes:
                aggMethod = None
                self.params[3].enabled = 1

            if aggMethod:
                aggType = self.aggTypes[aggMethod.upper()]
                if aggType == 1 or aggType == 3:
                    #### Allow Bounding Polygons for Fishnet ####
                    self.params[4].enabled = 1
                    self.params[7].enabled = 1
                else:
                    self.params[4].enabled = 0
                    self.params[7].enabled = 0

                if aggType:
                    analysisName = "JOIN_COUNT"
                else:
                    analysisName = "ICOUNT"
                fieldNames = [analysisName] + fieldNames
                fieldTypes = ["LONG"] + fieldTypes

        #### Add Master Field ####
        if self.params[0].value:
            masterFieldObj = ARCPY.Field()
            masterFieldObj.name = "SOURCE_ID"
            masterFieldObj.type = "LONG"
            addFields.append(masterFieldObj)

        for fieldInd, fieldName in enumerate(fieldNames):
            fieldType = fieldTypes[fieldInd]
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = fieldType
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields

        #### Valid Raster Name ####
        if self.params[6].altered:
            if self.params[6].value:
                try:
                    rastValue = UTILS.returnRasterName(self.params[6].value.value)
                    self.params[6].value = rastValue
                except:
                    pass

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        self.params = parameters
        if not self.params[2].value:
            if self.params[0].value:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    shapeType = desc.ShapeType.upper()
                    if shapeType == "POLYGON":
                        self.params[2].setIDMessage("ERROR", 110151)
                    else:
                        aggMethod = self.params[3].value
                        if not aggMethod:
                            self.params[3].setIDMessage("ERROR", 110152)
                        else:
                            aggType = self.aggTypes[aggMethod.upper()]
                            if aggType == 2:
                                if not self.params[5].value:
                                    self.params[5].setIDMessage("ERROR", 110153)
                except:
                    pass

        if self.params[6].value:
            try:
                outPath, outName = OS.path.split(self.params[6].value.value)
                if not OS.path.exists(outPath):
                    self.params[6].setIDMessage("ERROR", 560)
            except:
                pass

        if self.params[7].value:
            cellSizeUnit = self.params[7].value.value
            try:
                cellSizeParts = cellSizeUnit.split()
                cellSize = UTILS.strToFloat(cellSizeParts[0])

                if cellSize <= 0:
                    self.params[7].setIDMessage("ERROR", 531)
            except:
                pass

        if self.params[8].value:
            bandSizeUnit = self.params[8].value.value
            try:
                bandSizeParts = bandSizeUnit.split()
                bandSize = UTILS.strToFloat(bandSizeParts[0])

                if bandSize <= 0:
                    self.params[8].setIDMessage("ERROR", 531)
            except:
                pass

        if self.params[7].value and self.params[8].value:
            cellSizeUnit = self.params[7].value.value
            bandSizeUnit = self.params[8].value.value
            try:
                cellSizeParts = cellSizeUnit.split()
                bandSizeParts = bandSizeUnit.split()
                cellSize = UTILS.strToFloat(cellSizeParts[0])
                bandSize = UTILS.strToFloat(bandSizeParts[0])
                cellSizeUnit = cellSizeParts[1].upper()
                bandSizeUnit = bandSizeParts[1].upper()
                unitCell, factorCell = UTILS.distanceUnitInfo[cellSizeUnit]
                unitBand, factorBand = UTILS.distanceUnitInfo[bandSizeUnit]
                cellSize = factorCell * cellSize
                bandSize = factorBand * bandSize
                if bandSize <= cellSize:
                    self.params[8].setIDMessage("ERROR", 192, self.params[8].name)
            except:
                pass

        return

    def setParameterInfo(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            shapeType = desc.ShapeType.upper()
            self.oidName = desc.oidFieldName
            self.setOutputSymbology(shapeType)
            self.shapeType = shapeType
            for field in desc.fields:
                self.fieldObjects[field.name] = field
        except:
            self.oidName = None
            self.shapeType = None

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        varName = self.params[2].value

        #### Output Features ####
        if varName:
            if renderOut == 0:
                renderLayerFile = "LocalGPoints.lyr"
            elif renderOut == 1:
                renderLayerFile = "LocalGPolylines.lyr"
            else:
                renderLayerFile = "LocalGPolygons.lyr"
        else:
            aggMethod = self.params[3].value
            if aggMethod:
                aggType = self.aggTypes[aggMethod.upper()]
                if aggType:
                    renderLayerFile = "LocalGPolygons.lyr"
                else:
                    renderLayerFile = "LocalGPoints.lyr"
            else:
                renderLayerFile = "LocalGPolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[1].symbology = fullRLF

        #### Output Density ####
        if self.params[6].value:
            if varName:
                rasterLayerFile = "PointDensityHSGray.lyr"
            else:
                rasterLayerFile = "PointDensityHSGrayPoints.lyr"

            fullRast = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                                    "Layers", renderLayerFile)
            self.params[6].symbology = fullRast

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import OptimizedHotSpotAnalysis as OHSA
        import arcpy.management as DM

        #### Input Parameters ####
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        varName = UTILS.getTextParameter(2, parameters, fieldName=True)
        aggMethod = UTILS.getTextParameter(3, parameters)
        if aggMethod:
            aggType = self.aggTypes[aggMethod.upper()]
        else:
            aggType = 1

        boundaryFC = UTILS.getTextParameter(4, parameters)
        polygonFC = UTILS.getTextParameter(5, parameters)
        outputRaster = UTILS.getTextParameter(6, parameters)

        userCellSize, userCellUnit = UTILS.getLinearUnitParameter(7, parameters)
        userBandSize, userBandUnit = UTILS.getLinearUnitParameter(8, parameters)
        useDefaultDistance = False
        useDefaultBand = False

        if userCellUnit is None:
            useDefaultDistance = True

        if userBandUnit is None:
            useDefaultBand = True

        #### Check Number of Polygons ####
        if polygonFC and aggType == 2:
            ssdoPoly = SSDO.SSDataObject(polygonFC)
            ssdoPoly.obtainData(ssdoPoly.oidName)
            OHSA.checkNumberPolygons(ssdoPoly.numObs)

        makeFeatureLayerNoExtent = UTILS.clearExtent(DM.MakeFeatureLayer)
        selectLocationNoExtent = UTILS.clearExtent(DM.SelectLayerByLocation)
        featureLayer = "InputOHSA_FC"
        featureLayerInit = "InputOHSA_Init_FC"
        makeFeatureLayerNoExtent(inputFC, featureLayerInit)
        selectionType = UTILS.getSelectionType(featureLayerInit)

        #### Handle Current Selection and Study Area Selection ####
        if aggType == 1 or aggType == 3:
            if boundaryFC:
                selectLocationNoExtent(featureLayerInit, "INTERSECT",
                                       boundaryFC, "#",
                                       selectionType)
            polygonFC = None

        elif aggType == 2:
            selectLocationNoExtent(featureLayerInit, "INTERSECT",
                                   polygonFC, "#",
                                   selectionType)
            boundaryFC = None

        else:
            boundaryFC = None
            polygonFC = None

        #### Create SSDO ####
        makeFeatureLayerNoExtent(featureLayerInit, featureLayer)
        UTILS.passiveDelete(featureLayerInit)
        ssdo = SSDO.SSDataObject(featureLayer, templateFC=outputFC,
                                 useChordal=True)

        extentFactor = ssdo.distanceInfo.convertFactor
        processingBandSize = None
        processingCellSize = None
        cellSizeOrigin = None
        bandSizeOrigin = None

        if not useDefaultBand:
            bandSizeStr, bandSizeFactor = UTILS.distanceUnitInfo[userBandUnit]
            processingBandSize = (userBandSize * bandSizeFactor) / extentFactor
            bandSizeOrigin = UTILS.getTextParameter(8, parameters)

        if not useDefaultDistance:
            cellSizeStr, cellSizeFactor = UTILS.distanceUnitInfo[userCellUnit]
            processingCellSize = (userCellSize * cellSizeFactor) / extentFactor
            extendDistance = processingCellSize
            if ssdo.useChordal:
                extendDistance = (userCellSize * cellSizeFactor) / UTILS.GCSDegree2Meters
            cellSizeOrigin = UTILS.getTextParameter(7, parameters)
            #### Check and Make Sure the Cell Size Won't Exceed The Limitation of Input Feature Layer's SRS Extent ####
            xMin, yMin, zMin, xMax, yMax, zMax = UTILS.getXYZProjectionDomain(ssdo.spatialRef)
            centroid = ssdo.extent.polygon.centroid
            cX = centroid.X
            cY = centroid.Y
            if cX - extendDistance < xMin \
                    or cX + extendDistance > xMax \
                    or cY - extendDistance < yMin \
                    or cY + extendDistance > yMax:
                ARCPY.AddIDMessage("ERROR", 110250)
                raise SystemExit()

        hs = OHSA.OptHotSpots(ssdo, outputFC, varName=varName, aggType=aggType,
                              polygonFC=polygonFC, boundaryFC=boundaryFC,
                              outputRaster=outputRaster, cellSize2Use=processingCellSize,
                              bandSize2Use=processingBandSize, parameters=parameters,
                              cellSizeOrigin=cellSizeOrigin, bandSizeOrigin=bandSizeOrigin)
        UTILS.passiveDelete(featureLayer)


class SimilaritySearch(object):
    def __init__(self):
        self.label = "Similarity Search"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030006
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}
        self.outputRenderInfo = {
            ('BOTH', 0): 'SimSearchBothPoints.lyr',
            ('MOST_SIMILAR', 0): 'SimSearchMostPoints.lyr',
            ('LEAST_SIMILAR', 0): 'SimSearchLeastPoints.lyr',
            ('BOTH', 1): 'SimSearchBothPolylines.lyr',
            ('MOST_SIMILAR', 1): 'SimSearchMostPolylines.lyr',
            ('LEAST_SIMILAR', 1): 'SimSearchLeastPolylines.lyr',
            ('BOTH', 2): 'SimSearchBothPolygons.lyr',
            ('MOST_SIMILAR', 2): 'SimSearchMostPolygons.lyr',
            ('LEAST_SIMILAR', 2): 'SimSearchLeastPolygons.lyr',
        }

        self.outputFieldInfo = {
            'ATTRIBUTE_VALUES':
                {'SIMRANK': ('Similarity Rank', 'LONG', 0),
                 'DSIMRANK': ('Dissimilarity Rank', 'LONG', 0),
                 'SIMINDEX': ('Sum Squared Value Differences', 'DOUBLE', 0.0),
                 'DSTCLOSEST': ('Distance to closest', 'DOUBLE', 0.0),
                 'LABELRANK': ('Render Rank', 'LONG', 0)},
            'RANKED_ATTRIBUTE_VALUES':
                {'SIMRANK': ('Similarity Rank', 'LONG', 0),
                 'DSIMRANK': ('Dissimilarity Rank', 'LONG', 0),
                 'SIMINDEX': ('Sum Squared Rank Differences', 'DOUBLE', 0.0),
                 'DSTCLOSEST': ('Distance to closest', 'DOUBLE', 0.0),
                 'LABELRANK': ('Render Rank', 'LONG', 0)},
            'ATTRIBUTE_PROFILES':
                {'SIMRANK': ('Similarity Rank', 'LONG', 0),
                 'DSIMRANK': ('Dissimilarity Rank', 'LONG', 0),
                 'SIMINDEX': ('Cosine Similarity', 'DOUBLE', 1.0),
                 'DSTCLOSEST': ('Distance to closest', 'DOUBLE', 0.0),
                 'LABELRANK': ('Render Rank', 'LONG', 0)}
        }

        self.matchFieldInfo = {
            'BOTH':
                ['SIMRANK', 'DSIMRANK', 'SIMINDEX', 'DSTCLOSEST', 'LABELRANK'],
            'MOST_SIMILAR':
                ['SIMRANK', 'SIMINDEX', 'DSTCLOSEST', 'LABELRANK'],
            'LEAST_SIMILAR':
                ['DSIMRANK', 'SIMINDEX', 'DSTCLOSEST', 'LABELRANK']
        }
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features To Match",
                                 name="Input_Features_To_Match",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Candidate Features",
                                 name="Candidate_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param2 = ARCPY.Parameter(displayName="Output Features",
                                 name="Output_Features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param3 = ARCPY.Parameter(displayName="Collapse Output To Points",
                                 name="Collapse_Output_To_Points",
                                 datatype="GPBoolean",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.list = ['COLLAPSE', 'NO_COLLAPSE']
        param3.value = False

        param4 = ARCPY.Parameter(displayName="Most Or Least Similar",
                                 name="Most_Or_Least_Similar",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['MOST_SIMILAR', 'LEAST_SIMILAR', 'BOTH']

        param4.parameterDependencies = ["Input_Features"]

        param4.value = 'MOST_SIMILAR'

        param5 = ARCPY.Parameter(displayName="Match Method",
                                 name="Match_Method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param5.filter.type = "ValueList"

        param5.filter.list = ['ATTRIBUTE_VALUES', 'RANKED_ATTRIBUTE_VALUES', 'ATTRIBUTE_PROFILES']

        param5.value = 'ATTRIBUTE_VALUES'

        param6 = ARCPY.Parameter(displayName="Number Of Results",
                                 name="Number_Of_Results",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")

        param6.filter.list = []

        param6.value = 10

        param7 = ARCPY.Parameter(displayName="Attributes Of Interest",
                                 name="Attributes_Of_Interest",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param7.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"

        param7.filter.list = ['Short', 'Long', 'Float', 'Double']

        param7.parameterDependencies = ["Input_Features_To_Match"]

        param8 = ARCPY.Parameter(displayName="Fields To Append To Output",
                                 name="Fields_To_Append_To_Output",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param8.filter.list = ['Short', 'Long', 'Float', 'Double', 'Text', 'Date']
        param8.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param8.category = "Additional Options"
        param8.parameterDependencies = ["Candidate_Features"]

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        #### All Fields ####
        baseFields = {}
        self.params[3].enabled = True

        if self.params[0].altered:
            try:
                d = ARCPY.Describe(self.params[0].value)
                shapeType = d.shapeType.upper()
                for field in d.fields:
                    baseFields[field.name] = field
                self.setOutputSymbology(shapeType)
            except:
                pass

        candFields = {}
        if self.params[1].altered:
            try:
                d = ARCPY.Describe(self.params[1].value)
                for field in d.fields:
                    candFields[field.name] = field
                d = ARCPY.Describe(self.params[0].value)
                shapeType = d.shapeType.upper()
                self.setOutputSymbology(shapeType)
            except:
                pass

        if self.params[0].value and self.params[1].value:
            self.setCollapse()

        ##### Add Fields ####
        addFields = []
        newField = ARCPY.Field()
        newField.name = "MATCH_ID"
        newField.type = "LONG"
        addFields.append(newField)

        newField = ARCPY.Field()
        newField.name = "CAND_ID"
        newField.type = "LONG"
        addFields.append(newField)

        if self.params[7].value:  # and ARCPY.Exists(self.params[0].value)
            for fieldName in self.params[7].value.exportToString().split(";"):
                if fieldName in baseFields:
                    addFields.append(baseFields[fieldName])

        if self.params[8].value:
            for fieldName in self.params[8].value.exportToString().split(";"):
                if fieldName in candFields:
                    addFields.append(candFields[fieldName])

        #### Add Result Fields ####
        fieldNames = self.matchFieldInfo[self.params[4].value]
        fieldInfo = self.outputFieldInfo[self.params[5].value]
        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = fieldInfo[fieldName][1]
            addFields.append(newField)

        self.params[2].schema.additionalFields = addFields

    def updateMessages(self, parameters):
        return

    def setCollapse(self):
        shapeTypeBase = None
        shapeTypeCand = None
        try:
            d = ARCPY.Describe(self.params[0].value)
            shapeTypeBase = self.renderType[d.shapeType.upper()]
        except:
            pass
        try:
            d = ARCPY.Describe(self.params[1].value)
            shapeTypeCand = self.renderType[d.shapeType.upper()]
        except:
            pass

        if shapeTypeBase == 0 or shapeTypeCand == 0:
            self.params[3].enabled = False
        if shapeTypeBase != shapeTypeCand:
            self.params[3].value = True
            self.params[3].enabled = False

        #### Must Have Advanced License ####
        if not checkLicense():
            self.params[3].value = True
            self.params[3].enabled = False

    def setOutputSymbology(self, shapeType):
        if self.params[3].value:
            renderType = 0
        else:
            renderType = self.renderType[shapeType]
            try:
                d = ARCPY.Describe(self.params[1].value)
                candType = self.renderType[d.shapeType.upper()]
                if candType != renderType:
                    renderType = 0
            except:
                pass

        try:
            numResults = int(self.params[6].value)
        except:
            numResults = 10

        renderKey = (self.params[4].value, renderType)
        renderFile = self.outputRenderInfo[renderKey]
        renderLayerFile = returnRenderLayerFile(numResults, renderFile)
        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)

        self.params[2].symbology = fullRLF

    def execute(self, parameters, messages):
        import Similarity as SIM

        inputFC = UTILS.getTextParameter(0, parameters)
        candidateFC = UTILS.getTextParameter(1, parameters)
        outputFC = UTILS.getTextParameter(2, parameters)
        collapseToPoints = parameters[3].value
        similarType = UTILS.getTextParameter(4, parameters)
        matchMethod = UTILS.getTextParameter(5, parameters)
        numResults = UTILS.getNumericParameter(6, parameters)
        tempFieldNames = UTILS.getTextParameter(7, parameters).upper()
        tempFieldNames = tempFieldNames.split(";")
        appendFields = UTILS.getTextParameter(8, parameters)

        if appendFields is not None:
            appendFields = appendFields.upper()
            appendFields = appendFields.split(";")
            appendFields = [i for i in appendFields if i not in tempFieldNames]
        else:
            appendFields = []

        #### Get/Check Output Spatial Ref ####
        explicitSpatialRef = SIM.getOutputSpatialRef(inputFC, candidateFC,
                                                     outputFC)

        #### Initialize DataObjects ####
        ssdoBase = SSDO.SSDataObject(inputFC, useChordal=False,
                                     explicitSpatialRef=explicitSpatialRef)
        ssdoCand = SSDO.SSDataObject(candidateFC, useChordal=False,
                                     explicitSpatialRef=explicitSpatialRef)

        #### Field Validation ####
        fieldNames, appendBase, badInputNames = SIM.fieldValidation(ssdoBase,
                                                                    ssdoCand,
                                                                    tempFieldNames,
                                                                    appendFields)

        #### Warn About Excluded Fields ####
        badNames = len(badInputNames)
        if badNames:
            badInputNames = ", ".join(badInputNames)
            ARCPY.AddIDMessage("WARNING", 1584, badInputNames)

        #### No Valid Fields Found ####
        if not len(fieldNames):
            ARCPY.AddIDMessage("ERROR", 1585)
            raise SystemExit()

        #### Runtime Check for Cosign Sim (In Class as Well for Variance) ####
        if len(fieldNames) == 1 and matchMethod == 'ATTRIBUTE_PROFILES':
            ARCPY.AddIDMessage("ERROR", 1598)
            raise SystemExit()

        allFieldNamesBase = fieldNames + appendBase
        allFieldNamesCand = fieldNames + appendFields

        ssdoBase.obtainData(ssdoBase.oidName, allFieldNamesBase,
                            explicitBadRecordID=1615,
                            useNullinFields=appendBase)
        if ssdoBase.numObs == 0:
            ARCPY.AddIDMessage("ERROR", 1599)
            raise SystemExit()

        ssdoCand.obtainData(ssdoCand.oidName, allFieldNamesCand,
                            explicitBadRecordID=1616,
                            useNullinFields=appendFields)

        if ssdoCand.numObs <= 2:
            ARCPY.AddIDMessage("ERROR", 1589)
            raise SystemExit()

        ss = SIM.SimilaritySearch(ssdoBase, ssdoCand, fieldNames,
                                  similarType=similarType,
                                  matchMethod=matchMethod,
                                  numResults=numResults,
                                  appendFields=allFieldNamesCand)
        ss.report()

        baseIsPoint = UTILS.renderType[ssdoBase.shapeType.upper()] == 0
        baseCandDiff = ssdoBase.shapeType.upper() != ssdoCand.shapeType.upper()
        if collapseToPoints or baseIsPoint or baseCandDiff:
            ss.createOutput(outputFC, parameters)
        else:
            ss.createOutputShapes(outputFC, parameters)


class GenerateNetworkSpatialWeights(object):
    def __init__(self):
        self.label = "Generate Network Spatial Weights"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060004
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point']

        param1 = ARCPY.Parameter(displayName="Unique ID Field",
                                 name="Unique_ID_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Output Spatial Weights Matrix File",
                                 name="Output_Spatial_Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Required",
                                 direction="Output")

        param2.filter.list = ['swm']

        param3 = ARCPY.Parameter(displayName="Input Network",
                                 name="Input_Network",
                                 datatype="GPNetworkDatasetLayer",
                                 parameterType="Required",
                                 direction="Input")

        param4 = ARCPY.Parameter(displayName="Impedance Attribute",
                                 name="Impedance_Attribute",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param4.category = "Custom Travel Mode Options"
        param4.filter.type = "ValueList"

        param4.filter.list = []

        param5 = ARCPY.Parameter(displayName="Impedance Cutoff",
                                 name="Impedance_Cutoff",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param5.category = "Network Analysis Options"
        param6 = ARCPY.Parameter(displayName="Maximum Number of Neighbors",
                                 name="Maximum_Number_of_Neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param6.category = "Network Analysis Options"
        param7 = ARCPY.Parameter(displayName="Barriers",
                                 name="Barriers",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['Point', 'Polygon', 'Polyline']
        param7.category = "Network Analysis Options"
        param8 = ARCPY.Parameter(displayName="U-turn Policy",
                                 name="U-turn_Policy",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param8.category = "Custom Travel Mode Options"
        param8.filter.type = "ValueList"

        param8.filter.list = ['ALLOW_UTURNS', 'NO_UTURNS', 'ALLOW_DEAD_ENDS_ONLY',
                              'ALLOW_DEAD_ENDS_AND_INTERSECTIONS_ONLY']

        param8.value = 'ALLOW_UTURNS'

        param9 = ARCPY.Parameter(displayName="Restrictions",
                                 name="Restrictions",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param9.category = "Custom Travel Mode Options"
        param9.filter.type = "ValueList"

        param9.filter.list = []

        param10 = ARCPY.Parameter(displayName="Use Hierarchy in Analysis",
                                  name="Use_Hierarchy_in_Analysis",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param10.filter.list = ['USE_HIERARCHY', 'NO_HIERARCHY']
        param10.value = False
        param10.category = "Custom Travel Mode Options"

        param11 = ARCPY.Parameter(displayName="Search Tolerance",
                                  name="Search_Tolerance",
                                  datatype="GPLinearUnit",
                                  parameterType="Optional",
                                  direction="Input")
        param11.category = "Network Analysis Options"
        param11.value = '5000 Meters'

        param12 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                  name="Conceptualization_of_Spatial_Relationships",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")
        param12.category = "Weights Options"
        param12.filter.type = "ValueList"

        param12.filter.list = ['INVERSE', 'FIXED']

        param12.value = 'INVERSE'

        param13 = ARCPY.Parameter(displayName="Exponent",
                                  name="Exponent",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")
        param13.category = "Weights Options"
        param13.value = 1.0

        param14 = ARCPY.Parameter(displayName="Row Standardization",
                                  name="Row_Standardization",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param14.filter.list = ['ROW_STANDARDIZATION', 'NO_STANDARDIZATION']
        param14.value = True

        param14.category = "Weights Options"
        param15 = ARCPY.Parameter(displayName="Travel Mode",
                                  name="Travel_Mode",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")

        param15.filter.type = "ValueList"

        param15.filter.list = []

        param16 = ARCPY.Parameter(displayName="Time of Day",
                                  name="Time_of_Day",
                                  datatype="GPDate",
                                  parameterType="Optional",
                                  direction="Input")
        param16.category = "Network Analysis Options"
        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11,
                param12, param13, param14, param15, param16]

    def isLicensed(self):
        try:
            t = ARCPY.CheckOutExtension("Network")
            if t != 'CheckedOut':
                return False
        except:
            return False

        return True

    def updateParameters(self, parameters):
        self.params = parameters
        #### Network Dataset Changed ####
        if self.params[3].altered:
            if self.params[3].value and not self.params[3].hasBeenValidated:
                self.travelModes = returnTravelModes(self.params[3])
                travelList = list(self.travelModes.keys())
                travelList.append("Custom")
                self.params[15].filter.list = travelList
                self.setTravelModeParams(self.params[15].value)
                self.updateNetworkParams(self.params[3].value)

        #### Travel Mode Changed ####
        if self.params[15].altered:
            if self.params[15].value and self.params[3].value and not self.params[15].hasBeenValidated:
                self.travelModes = returnTravelModes(self.params[3])
                travelList = list(self.travelModes.keys())
                travelList.append("Custom")
                self.params[15].filter.list = travelList
                self.updateTravelModeParams(self.params[15].value)

        #### Disable Exponent if Fixed Distance ####
        if self.params[12].value == "INVERSE":
            self.params[13].enabled = 1
        else:
            self.params[13].enabled = 0

    def updateMessages(self, parameters):
        self.params = parameters
        #### Make Sure Cutoff is > 0 ####
        if self.params[5].altered and self.params[5].value <= 0:
            self.params[5].setIDMessage("Error", 30057)

            #### Make Sure Number of Neighs is > 0 ####
        if self.params[6].altered and self.params[6].value <= 0:
            self.params[6].setIDMessage("Error", 30057)

        #### Make Sure Linear Unit in => 0 ####
        if self.params[11].altered:
            if float(str(self.params[11].value).split(" ")[0]) < 0:
                self.params[11].setIDMessage("Error", 30065)

    def updateTravelModeParams(self, travelMode):
        if travelMode.upper() != "CUSTOM":
            self.setTravelModeParams(travelMode)
        else:
            desc = ARCPY.Describe(self.params[3].value)
            self.setCustomParams(desc)

    def updateNetworkParams(self, network):
        """Sets Network Parameters."""

        #### Describe and Assess Travel Mode ####
        desc = ARCPY.Describe(network)
        defaultTravelMode = desc.defaultTravelModeName
        hasTravelMode = self.params[15].value not in ["", None]
        if defaultTravelMode != "" and not hasTravelMode:
            self.setTravelModeParams(defaultTravelMode)
        else:
            if hasTravelMode:
                if self.params[15].value.upper() != "CUSTOM":
                    self.setTravelModeParams(self.params[15].value)
                else:
                    self.setCustomParams(desc)
            else:
                self.params[15].value = "Custom"
                self.setCustomParams(desc)
        return

    def setCustomParams(self, desc):
        self.resetNetworkProps()
        attributes = desc.attributes
        costs = []
        defCost = ""
        restrictions = []
        defRestrictions = []
        costDomain = self.params[4].filter
        restDomain = self.params[9].filter
        hierarchy = 0
        defHierarchy = False
        for attribute in attributes:
            fieldName = attribute.name
            useType = attribute.usageType

            #### Costs ####
            if useType == "Cost":
                costs.append(fieldName.upper())
                #### Check For Defaults ####
                if attribute.useByDefault:
                    defCost = fieldName.upper()

            #### Restrictions ####
            elif useType == "Restriction":
                #### Check For Defaults ####
                if attribute.useByDefault:
                    defRestrictions.append(fieldName.upper())
                restrictions.append(fieldName.upper())

            #### Hierarchy ####
            elif useType == "Hierarchy":
                hierarchy = 1
                #### Check For Defaults ####
                if attribute.useByDefault:
                    defHierarchy = True
            else:
                pass

        if hierarchy == 1:
            self.params[10].enabled = True
        else:
            self.params[10].enabled = False

        costDomain.list = costs
        restDomain.list = restrictions

        if not self.params[4].altered:
            self.params[4].value = defCost
        if not self.params[9].altered:
            self.params[9].value = ";".join(defRestrictions)
        if not self.params[10].altered:
            self.params[10].value = defHierarchy

    def setTravelModeParams(self, travelMode):
        if travelMode not in self.travelModes:
            # self.params[15].value = "Custom"
            self.updateTravelModeParams("Custom")
            # if not self.params[4].value:
            #    self.setCustomParams(ARCPY.Describe(self.params[3].value))
        else:
            travelModeInfo = self.travelModes[travelMode]
            self.params[4].value = travelModeInfo.impedance
            self.params[8].value = travelModeInfo.uTurns
            self.params[9].value = ";".join(travelModeInfo.restrictions)
            self.params[10].value = travelModeInfo.useHierarchy == "USE_HIERARCHY"
            self.params[15].value = travelMode
            self.params[4].enabled = False
            self.params[8].enabled = False
            self.params[9].enabled = False
            self.params[10].enabled = False

    def resetNetworkProps(self, resetValues=False):
        """Resets the network dataset derived parameters to nothing"""
        self.params[4].enabled = True
        self.params[8].enabled = True
        self.params[9].enabled = True
        self.params[4].filter.list = []
        self.params[9].filter.list = []
        if resetValues:
            self.params[4].value = ""
            self.params[8].value = ""
            self.params[9].value = ""
        return

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""

        #### Process Dialogue Inputs ####
        inputFC = UTILS.getTextParameter(0, parameters)
        masterField = UTILS.getTextParameter(1, parameters)
        swmFile = UTILS.getTextParameter(2, parameters)
        inputNetwork = UTILS.getTextParameter(3, parameters)
        impedance = UTILS.getTextParameter(4, parameters)

        cutoff = UTILS.getNumericParameter(5, parameters)
        if not cutoff:
            cutoff = "#"

        numberOfNeighs = UTILS.getNumericParameter(6, parameters)
        if not numberOfNeighs:
            numberOfNeighs = "#"

        inputBarrier = UTILS.getTextParameter(7, parameters)
        if not inputBarrier:
            inputBarrier = "#"

        uturnPolicy = UTILS.getTextParameter(8, parameters)

        restrictions = UTILS.getTextParameter(9, parameters)
        if not restrictions:
            restrictions = "#"

        hierarchyBool = parameters[10].value
        if hierarchyBool:
            hierarchy = 'USE_HIERARCHY'
        else:
            hierarchy = 'NO_HIERARCHY'

        searchTolerance = UTILS.getTextParameter(11, parameters)
        if not searchTolerance:
            searchTolerance = "#"

        #### Assign to appropriate spatial weights method ####
        spaceConcept = UTILS.getTextParameter(12, parameters)
        spaceConcept = spaceConcept + "_DISTANCE"
        try:
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()

        #### Must Be Inverse Distance [0] or Fixed Distance [1] ####
        if wType not in [0, 1]:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()
        else:
            fixed = wType

        exponent = UTILS.getNumericParameter(13, parameters)
        rowStandard = parameters[14].value

        #### New Params ####
        travelMode = UTILS.getTextParameter(15, parameters)
        timeOfDay = parameters[16].value

        import Network2SWM as NSWM
        NSWM.network2SWM(inputFC, masterField, swmFile, inputNetwork, impedance,
                         cutoff=cutoff, numberOfNeighs=numberOfNeighs,
                         inputBarrier=inputBarrier, uturnPolicy=uturnPolicy,
                         restrictions=restrictions, hierarchy=hierarchy,
                         searchTolerance=searchTolerance, fixed=fixed,
                         exponent=exponent, rowStandard=rowStandard)
        return


class OptimizedOutlierAnalysis(object):
    def __init__(self):
        self.label = "Optimized Outlier Analysis"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030007
        self.aggTypes = {"SNAP_NEARBY_INCIDENTS_TO_CREATE_WEIGHTED_POINTS": 0,
                         "COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS": 1,
                         "COUNT_INCIDENTS_WITHIN_AGGREGATION_POLYGONS": 2,
                         "COUNT_INCIDENTS_WITHIN_HEXAGON_POLYGONS": 3}
        self.params = None
        self.renderType = {'POINT': 0, 'MULTIPOINT': 0,
                           'POLYLINE': 1, 'LINE': 1,
                           'POLYGON': 2}
        self.shapeType = None
        self.oidName = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="Input_Features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point', 'Multipoint', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="Output_Features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Analysis Field",
                                 name="Analysis_Field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']
        param2.parameterDependencies = ["Input_Features"]

        param3 = ARCPY.Parameter(displayName="Incident Data Aggregation Method",
                                 name="Incident_Data_Aggregation_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS', 'COUNT_INCIDENTS_WITHIN_HEXAGON_POLYGONS',
                              'COUNT_INCIDENTS_WITHIN_AGGREGATION_POLYGONS',
                              'SNAP_NEARBY_INCIDENTS_TO_CREATE_WEIGHTED_POINTS']

        param3.value = 'COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS'

        param3.enabled = False

        param4 = ARCPY.Parameter(displayName="Bounding Polygons Defining Where Incidents Are Possible",
                                 name="Bounding_Polygons_Defining_Where_Incidents_Are_Possible",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Polygon']
        param4.enabled = False

        param5 = ARCPY.Parameter(displayName="Polygons For Aggregating Incidents Into Counts",
                                 name="Polygons_For_Aggregating_Incidents_Into_Counts",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param5.filter.list = ['Polygon']
        param5.enabled = False

        param6 = ARCPY.Parameter(displayName="Performance Adjustment",
                                 name="Performance_Adjustment",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param6.filter.type = "ValueList"

        param6.filter.list = ['QUICK_199', 'BALANCED_499', 'ROBUST_999']

        param6.value = 'BALANCED_499'

        param6.enabled = False

        param7 = ARCPY.Parameter(displayName="Cell Size",
                                 name="Cell_Size",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = supportDist
        param7.category = "Override Settings"
        param8 = ARCPY.Parameter(displayName="Distance Band",
                                 name="Distance_Band",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = supportDist
        param8.category = "Override Settings"
        return [param0, param1, param2, param3, param4, param5, param6, param7, param8]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if self.params[0].altered:
            if self.params[0].value:
                self.setParameterInfo(self.params[0].value)

        self.params[6].enabled = 1
        if self.shapeType in [None, "POLYGON"]:
            self.params[3].enabled = 0
            self.params[4].enabled = 0
            self.params[5].enabled = 0
            self.params[7].enabled = 0
        else:
            #### For Points ####
            fieldName = self.params[2].value
            aggMethod = self.params[3].value
            self.params[7].enabled = 1
            if fieldName:
                #### If Marked, Allow Density, No Agg Method ####
                self.params[3].enabled = 0
                self.params[4].enabled = 0
                self.params[5].enabled = 0
            else:
                #### If Unmarked, Allow Poly FCs ####
                self.params[3].enabled = 1

                if aggMethod.upper().replace(' ', "_") not in self.aggTypes:
                    aggMethod = None

                if aggMethod:
                    self.params[3].value = aggMethod.upper().replace(' ', "_")
                    aggType = self.aggTypes[aggMethod.upper().replace(' ', "_")]
                    if aggType == 2:
                        #### Allow Polygons for Counts ####
                        self.params[5].enabled = 1
                    else:
                        self.params[5].enabled = 0

                    if aggType == 1 or aggType == 3:
                        #### Allow Bounding Polygons for Fishnet ####
                        self.params[4].enabled = 1
                        self.params[7].enabled = 1
                    else:
                        self.params[4].enabled = 0
                        self.params[7].enabled = 0
                elif aggMethod is not None:
                    self.params[4].enabled = 0
                    self.params[5].enabled = 0

        #### Add Fields ####
        addFields = []

        #### Result Fields ####
        fieldNames = ["LMiIndex", "LMiZScore", "LMiPValue", "COType"]

        #### Analysis Field ####
        if self.params[2].value:
            self.params[7].enabled = 0
            fieldName = self.params[1].value.value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])
        else:
            self.params[7].enabled = 1
            aggMethod = self.params[3].value

            if aggMethod.upper() not in self.aggTypes:
                aggMethod = None
                self.params[3].enabled = 1

            if aggMethod:
                aggType = self.aggTypes[aggMethod.upper()]
                if aggType == 1 or aggType == 3:
                    #### Allow Bounding Polygons for Fishnet ####
                    self.params[4].enabled = 1
                    self.params[7].enabled = 1
                else:
                    self.params[4].enabled = 0
                    self.params[7].enabled = 0

                if aggType:
                    analysisName = "JOIN_COUNT"
                else:
                    analysisName = "ICOUNT"
                fieldNames = [analysisName] + fieldNames

        #### Result Fields ####
        for fieldInd, fieldName in enumerate(fieldNames):
            newField = ARCPY.Field()
            newField.name = fieldName
            if fieldName == "COType":
                newField.type = "TEXT"
                newField.length = 2
            else:
                newField.type = "DOUBLE"
            addFields.append(newField)
        self.params[1].schema.additionalFields = addFields

        #### Add Master Field ####
        if self.params[0].value:
            masterFieldObj = ARCPY.Field()
            masterFieldObj.name = "SOURCE_ID"
            masterFieldObj.type = "LONG"
            addFields.append(masterFieldObj)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        self.params = parameters
        if not self.params[2].value:
            if self.params[0].value:
                try:
                    desc = ARCPY.Describe(self.params[0].value)
                    shapeType = desc.ShapeType.upper()
                    if shapeType == "POLYGON":
                        self.params[2].setIDMessage("ERROR", 110151)
                    else:
                        aggMethod = self.params[3].value
                        if not aggMethod:
                            self.params[3].setIDMessage("ERROR", 110152)
                        else:
                            aggType = self.aggTypes[aggMethod.upper()]
                            if aggType == 2:
                                if not self.params[5].value:
                                    self.params[5].setIDMessage("ERROR", 110153)
                except:
                    pass

        if self.params[7].value:
            cellSizeUnit = self.params[7].value.value
            try:
                cellSizeParts = cellSizeUnit.split()
                cellSize = UTILS.strToFloat(cellSizeParts[0])
                if cellSize <= 0:
                    self.params[7].setIDMessage("ERROR", 531)
            except:
                pass

        if self.params[8].value:
            bandSizeUnit = self.params[8].value.value
            try:
                bandSizeParts = bandSizeUnit.split()
                bandSize = UTILS.strToFloat(bandSizeParts[0])
                if bandSize <= 0:
                    self.params[8].setIDMessage("ERROR", 531)
            except:
                pass

        if self.params[7].value and self.params[8].value:
            cellSizeUnit = self.params[7].value.value
            bandSizeUnit = self.params[8].value.value
            try:
                cellSizeParts = cellSizeUnit.split()
                bandSizeParts = bandSizeUnit.split()
                cellSize = UTILS.strToFloat(cellSizeParts[0])
                bandSize = UTILS.strToFloat(bandSizeParts[0])
                cellSizeUnit = cellSizeParts[1].upper()
                bandSizeUnit = bandSizeParts[1].upper()
                unitCell, factorCell = UTILS.distanceUnitInfo[cellSizeUnit]
                unitBand, factorBand = UTILS.distanceUnitInfo[bandSizeUnit]
                cellSize = factorCell * cellSize
                bandSize = factorBand * bandSize
                if bandSize <= cellSize:
                    self.params[8].setIDMessage("ERROR", 192, self.params[8].name)
            except:
                pass

    def setParameterInfo(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            shapeType = desc.ShapeType.upper()
            self.oidName = desc.oidFieldName
            self.shapeType = shapeType
            self.setOutputSymbology(shapeType)
            for field in desc.fields:
                self.fieldObjects[field.name] = field
        except:
            self.oidName = None
            self.shapeType = None

    def setOutputSymbology(self, shapeType):
        renderOut = self.renderType[shapeType]
        varName = self.params[2].value

        #### Output Features ####
        if varName:
            if renderOut == 0:
                renderLayerFile = "LocalIPoints.lyr"
            elif renderOut == 1:
                renderLayerFile = "LocalIPolylines.lyr"
            else:
                renderLayerFile = "LocalIPolygons.lyr"
        else:
            aggMethod = self.params[3].value
            if aggMethod:
                aggType = self.aggTypes[aggMethod.upper()]
                if aggType:
                    renderLayerFile = "LocalIPolygons.lyr"
                else:
                    renderLayerFile = "LocalIPoints.lyr"
            else:
                renderLayerFile = "LocalIPolygons.lyr"

        fullRLF = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates",
                               "Layers", renderLayerFile)
        self.params[1].symbology = fullRLF

    def execute(self, parameters, messages):
        """Retrieves the parameters from the User Interface and executes the
        appropriate commands."""
        import OptimizedOutlierAnalysis as OOA
        import arcpy.management as DM

        #### Input Parameters ####
        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        varName = UTILS.getTextParameter(2, parameters, fieldName=True)
        aggMethod = UTILS.getTextParameter(3, parameters)
        if aggMethod:
            aggType = self.aggTypes[aggMethod.upper()]
        else:
            aggType = 1
        boundaryFC = UTILS.getTextParameter(4, parameters)
        polygonFC = UTILS.getTextParameter(5, parameters)

        permutationsOption = UTILS.getTextParameter(6, parameters)

        permutations = 499
        try:
            permutationsOption = permutationsOption.split('_')[1]
            permutations = int(permutationsOption)
        except:
            pass

        userCellSize, userCellUnit = UTILS.getLinearUnitParameter(7, parameters)
        userBandSize, userBandUnit = UTILS.getLinearUnitParameter(8, parameters)
        useDefaultDistance = False
        useDefaultBand = False

        if userCellUnit is None:
            useDefaultDistance = True

        if userBandUnit is None:
            useDefaultBand = True

        #### Check Number of Polygons ####
        if polygonFC and aggType == 2:
            ssdoPoly = SSDO.SSDataObject(polygonFC)
            ssdoPoly.obtainData(ssdoPoly.oidName)
            OOA.checkNumberPolygons(ssdoPoly.numObs)

        makeFeatureLayerNoExtent = UTILS.clearExtent(DM.MakeFeatureLayer)
        selectLocationNoExtent = UTILS.clearExtent(DM.SelectLayerByLocation)
        featureLayer = "InputOA_FC"
        featureLayerInit = "InputOA_Init_FC"
        makeFeatureLayerNoExtent(inputFC, featureLayerInit)
        selectionType = UTILS.getSelectionType(featureLayerInit)

        #### Handle Current Selection and Study Area Selection ####
        if aggType == 1 or aggType == 3:
            if boundaryFC:
                selectLocationNoExtent(featureLayerInit, "INTERSECT",
                                       boundaryFC, "#",
                                       selectionType)
            polygonFC = None

        elif aggType == 2:
            selectLocationNoExtent(featureLayerInit, "INTERSECT",
                                   polygonFC, "#",
                                   selectionType)
            boundaryFC = None

        else:
            boundaryFC = None
            polygonFC = None

        #### Create SSDO ####
        makeFeatureLayerNoExtent(featureLayerInit, featureLayer)
        UTILS.passiveDelete(featureLayerInit)
        ssdo = SSDO.SSDataObject(featureLayer, templateFC=outputFC,
                                 useChordal=True)

        extentFactor = ssdo.distanceInfo.convertFactor
        processingBandSize = None
        processingCellSize = None
        cellSizeOrigin = None
        bandSizeOrigin = None

        if not useDefaultBand:
            bandSizeStr, bandSizeFactor = UTILS.distanceUnitInfo[userBandUnit]
            processingBandSize = (userBandSize * bandSizeFactor) / extentFactor
            bandSizeOrigin = UTILS.getTextParameter(8, parameters)

        if not useDefaultDistance:
            cellSizeStr, cellSizeFactor = UTILS.distanceUnitInfo[userCellUnit]
            processingCellSize = (userCellSize * cellSizeFactor) / extentFactor
            extendDistance = processingCellSize
            if ssdo.useChordal:
                extendDistance = (userCellSize * cellSizeFactor) / UTILS.GCSDegree2Meters
            cellSizeOrigin = UTILS.getTextParameter(7, parameters)
            #### Check and Make Sure the Cell Size Won't Exceed The Limitation of Input Feature Layer's SRS Extent ####
            xMin, yMin, zMin, xMax, yMax, zMax = UTILS.getXYZProjectionDomain(ssdo.spatialRef)
            centroid = ssdo.extent.polygon.centroid
            cX = centroid.X
            cY = centroid.Y
            if cX - extendDistance < xMin \
                    or cX + extendDistance > xMax \
                    or cY - extendDistance < yMin \
                    or cY + extendDistance > yMax:
                ARCPY.AddIDMessage("ERROR", 110250)
                raise SystemExit()

        hs = OOA.OptimizedOutlier(ssdo, outputFC, varName=varName, aggType=aggType,
                                  polygonFC=polygonFC, boundaryFC=boundaryFC,
                                  permutations=permutations,
                                  cellSize2Use=processingCellSize, bandSize2Use=processingBandSize,
                                  parameters=parameters,
                                  cellSizeOrigin=cellSizeOrigin, bandSizeOrigin=bandSizeOrigin)

        UTILS.passiveDelete(featureLayer)


class GenerateSpatialWeightsMatrix(object):
    def __init__(self):
        self.label = "Generate Spatial Weights Matrix"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060001
        self.params = None
        #### Set Lists of Spatial Concepts ####
        self.baseConcepts = ["INVERSE_DISTANCE", "FIXED_DISTANCE",
                             "K_NEAREST_NEIGHBORS", "DELAUNAY_TRIANGULATION",
                             "SPACE_TIME_WINDOW", "CONVERT_TABLE"]

        self.allConcepts = ["INVERSE_DISTANCE", "FIXED_DISTANCE",
                            "K_NEAREST_NEIGHBORS", "CONTIGUITY_EDGES_ONLY",
                            "CONTIGUITY_EDGES_CORNERS",
                            "DELAUNAY_TRIANGULATION",
                            "SPACE_TIME_WINDOW", "CONVERT_TABLE"]

        self.distSetTypes = ["INVERSE_DISTANCE", "FIXED_DISTANCE",
                             "K_NEAREST_NEIGHBORS",
                             "CONTIGUITY_EDGES_ONLY",
                             "CONTIGUITY_EDGES_CORNERS"]

        self.zSupport = ["INVERSE_DISTANCE", "FIXED_DISTANCE",
                         "K_NEAREST_NEIGHBORS", "SPACE_TIME_WINDOW"]

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Feature Class",
                                 name="Input_Feature_Class",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Unique ID Field",
                                 name="Unique_ID_Field",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ['Short', 'Long']

        param1.parameterDependencies = ["Input_Feature_Class"]

        param2 = ARCPY.Parameter(displayName="Output Spatial Weights Matrix File",
                                 name="Output_Spatial_Weights_Matrix_File",
                                 datatype="DEFile",
                                 parameterType="Required",
                                 direction="Output")

        param2.filter.list = ['swm']

        param3 = ARCPY.Parameter(displayName="Conceptualization of Spatial Relationships",
                                 name="Conceptualization_of_Spatial_Relationships",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['INVERSE_DISTANCE', 'FIXED_DISTANCE', 'K_NEAREST_NEIGHBORS', 'CONTIGUITY_EDGES_ONLY',
                              'CONTIGUITY_EDGES_CORNERS', 'DELAUNAY_TRIANGULATION', 'SPACE_TIME_WINDOW',
                              'CONVERT_TABLE']

        param4 = ARCPY.Parameter(displayName="Distance Method",
                                 name="Distance_Method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['EUCLIDEAN', 'MANHATTAN']

        param4.value = 'EUCLIDEAN'

        param4.enabled = False

        param5 = ARCPY.Parameter(displayName="Exponent",
                                 name="Exponent",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")

        param5.value = 1.0

        param5.enabled = False

        param6 = ARCPY.Parameter(displayName="Threshold Distance",
                                 name="Threshold_Distance",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "Range"
        param6.filter.list = [0.0, 999999999.0]
        param6.enabled = False

        param7 = ARCPY.Parameter(displayName="Number of Neighbors",
                                 name="Number_of_Neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")

        param7.enabled = False

        param8 = ARCPY.Parameter(displayName="Row Standardization",
                                 name="Row_Standardization",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['ROW_STANDARDIZATION', 'NO_STANDARDIZATION']
        param8.value = True

        param9 = ARCPY.Parameter(displayName="Input Table",
                                 name="Input_Table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Input")

        param9.enabled = False

        param10 = ARCPY.Parameter(displayName="Date/Time Field",
                                  name="Date_Time_Field",
                                  datatype="Field",
                                  parameterType="Optional",
                                  direction="Input")

        param10.parameterDependencies = ["Input_Feature_Class"]
        param10.filter.list = ['Date']
        param10.enabled = False

        param11 = ARCPY.Parameter(displayName="Date/Time Interval Type",
                                  name="Date_Time_Interval_Type",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")

        param11.filter.type = "ValueList"

        param11.filter.list = ['SECONDS', 'MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'MONTHS', 'YEARS']

        param11.enabled = False

        param12 = ARCPY.Parameter(displayName="Date/Time Interval Value",
                                  name="Date_Time_Interval_Value",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")

        param12.enabled = False

        param13 = ARCPY.Parameter(displayName="Use Z Values",
                                  name="Use_Z_values",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param13.filter.list = ['USE_Z_VALUES', 'DO_NOT_USE_Z_VALUES']
        param13.enabled = True

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11,
                param12, param13]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        if self.params[0].altered:
            if not self.params[0].isInputValueDerived():
                self.checkContiguity(self.params[0].value)

        #### Validate and Correct The SWM File Path ####
        if paramChanged(parameters[2]):
            try:
                if parameters[2].value:
                    swmPath = parameters[2].value.value
                    swmName, swmExt = OS.path.splitext(swmPath)
                    if swmExt != ".swm":
                        parameters[2].value = swmName + ".swm"
            except:
                pass

        #### Validate Space Concepts ####
        spaceConcept = self.params[3].value
        if spaceConcept:
            spaceConcept = spaceConcept.upper()

        #### Enable/Disable Distance Method ####
        nonDistMeth = ["DELAUNAY_TRIANGULATION", "CONVERT_TABLE", ""]
        if spaceConcept in nonDistMeth:
            self.params[4].enabled = 0
        else:
            try:
                desc = ARCPY.Describe(self.params[0].value)
                outSpatRef = setEnvSpatialReference(desc.SpatialReference)
                if outSpatRef.type.upper() == "GEOGRAPHIC":
                    self.params[4].enabled = False
                else:
                    self.params[4].enabled = True
            except:
                pass

        #### Enable/Disable Exponent ####
        if spaceConcept == "INVERSE_DISTANCE":
            self.params[5].enabled = 1
        else:
            self.params[5].enabled = 0

        #### Enable/Disable Threshold Distance ####
        threshTypes = ["INVERSE_DISTANCE", "FIXED_DISTANCE", "SPACE_TIME_WINDOW"]
        if spaceConcept in threshTypes:
            self.params[6].enabled = 1
        else:
            self.params[6].enabled = 0

        #### Enable/Disable Number of Neighs ####
        nonNNTypes = ["DELAUNAY_TRIANGULATION", "CONVERT_TABLE",
                      "SPACE_TIME_WINDOW", ""]
        if spaceConcept in nonNNTypes:
            self.params[7].enabled = 0
        else:
            self.params[7].enabled = 1

        if spaceConcept in self.distSetTypes:
            self.params[7].enabled = True
            numNeighs = self.params[7].value
            if not numNeighs:
                if spaceConcept == "K_NEAREST_NEIGHBORS":
                    self.params[7].value = 8
                else:
                    self.params[7].value = 0
        else:
            self.params[7].enabled = False
            self.params[7].value = None

        #### Enable Table Input ####
        if spaceConcept == "CONVERT_TABLE":
            self.params[9].enabled = 1
        else:
            self.params[9].enabled = 0

        #### Enable Space-Time Params ####
        if spaceConcept == "SPACE_TIME_WINDOW":
            self.params[10].enabled = 1
            self.params[11].enabled = 1
            self.params[12].enabled = 1
        else:
            self.params[10].enabled = 0
            self.params[11].enabled = 0
            self.params[12].enabled = 0

        if self.params[13].altered:
            changeConcept = self.shapeType != "POLYGON" and self.params[13].value
            if self.params[13].value and changeConcept:
                self.params[3].filter.list = self.zSupport
            else:
                self.params[3].filter.list = self.allConcepts

    def updateMessages(self, parameters):
        self.params = parameters
        spaceConcept = self.params[3].value
        if spaceConcept:
            spaceConcept = spaceConcept.upper()

        if spaceConcept == "K_NEAREST_NEIGHBORS":
            numNeighs = self.params[7].value
            if numNeighs < 1:
                self.params[7].setIDMessage("ERROR", 1219, 1)

        if self.params[3].value:
            value3 = self.params[3].value

            #### Convert Table ####
            if value3 == 'CONVERT_TABLE':
                if self.params[9].value in ["", "#", None]:
                    self.params[9].setIDMessage("ERROR", 110189)

            elif value3 == 'SPACE_TIME_WINDOW':
                if self.params[10].value in ["", "#", None]:
                    self.params[10].setIDMessage("ERROR", 1320)

                if self.params[11].value in ["", "#", None]:
                    self.params[11].setIDMessage("ERROR", 1321)

                if self.params[12].value in ["", "#", None]:
                    self.params[12].setIDMessage("ERROR", 1322)

    def checkContiguity(self, inputFC):
        try:
            desc = ARCPY.Describe(inputFC)
            self.shapeType = desc.ShapeType.upper()
            if self.shapeType == "POLYGON":
                self.params[13].enabled = 0
                self.params[3].filter.list = self.allConcepts
            else:
                self.hasZ = desc.HasZ
                if self.hasZ:
                    self.params[13].enabled = 1
                    self.params[3].filter.list = self.zSupport
                else:
                    self.params[13].enabled = 0
                    self.params[3].filter.list = self.baseConcepts
        except:
            self.shapeType = "POLYGON"
            self.hasZ = False
            pass

    def execute(self, parameters, messages):

        inputFC = UTILS.getTextParameter(0, parameters)
        masterField = UTILS.getTextParameter(1, parameters)
        swmFile = UTILS.getTextParameter(2, parameters)
        spaceConcept = UTILS.getTextParameter(3, parameters)
        distanceConcept = UTILS.getTextParameter(4, parameters)
        exponent = UTILS.getNumericParameter(5, parameters)
        threshold = UTILS.getNumericParameter(6, parameters)
        kNeighs = UTILS.getNumericParameter(7, parameters)
        rowStandard = parameters[8].value
        tableFile = UTILS.getTextParameter(9, parameters)

        #### Assess Temporal Options ####'
        timeField = UTILS.getTextParameter(10, parameters, fieldName=True)
        timeType = UTILS.getTextParameter(11, parameters)
        timeValue = UTILS.getNumericParameter(12, parameters)

        zEnabled = False

        #### Use 3D in PRO ####
        isPRO = UTILS.isPRO()
        if isPRO:
            zEnabled = parameters[13].value

        #### Assign to appropriate spatial weights method ####
        try:
            wType = WU.weightDispatch[spaceConcept]
        except:
            ARCPY.AddIDMessage("Error", 723)
            raise SystemExit()

        import Weights as WEIGHTS

        #### EUCLIDEAN or MANHATTAN ####
        try:
            concept = WU.conceptDispatch[distanceConcept]
        except:
            concept = "EUCLIDEAN"
            ARCPY.AddIDMessage("Warning", 110112)

        if not kNeighs:
            kNeighs = 0

        #### Check Z Enable ####
        desc = ARCPY.Describe(inputFC)
        hasZ = desc.HasZ

        if not hasZ and zEnabled:
            zEnabled = False
            ARCPY.AddIDMessage("Warning", 826)

        if wType <= 1:
            #### Distance Based Weights ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84118))

            #### Set Options for Fixed vs. Inverse ####
            if wType == 0:
                exponent = exponent
                fixed = 0
            else:
                exponent = 1
                fixed = 1

            #### Execute Distance-Based Weights ####
            w = WEIGHTS.distance2SWM(inputFC, swmFile, masterField, fixed=fixed,
                                     concept=concept, exponent=exponent,
                                     threshold=threshold, kNeighs=kNeighs,
                                     rowStandard=rowStandard,
                                     zEnabled=zEnabled)

        elif wType == 2:
            #### k-Nearest Neighbors Weights ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84119))
            w = WEIGHTS.kNearest2SWM(inputFC, swmFile, masterField, concept=concept,
                                     kNeighs=kNeighs, rowStandard=rowStandard,
                                     zEnabled=zEnabled)

        elif wType == 3:
            #### Delaunay Triangulation Weights ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84120))
            w = WEIGHTS.delaunay2SWM(inputFC, swmFile, masterField,
                                     rowStandard=rowStandard)

        elif wType == 4:
            #### Contiguity Based Weights, Edges Only ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84121))
            w = WEIGHTS.polygon2SWM(inputFC, swmFile, masterField, concept=concept,
                                    kNeighs=kNeighs, rowStandard=rowStandard,
                                    contiguityType="ROOK")

        elif wType == 5:
            #### Contiguity Based Weights, Edges and Corners ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84122))
            w = WEIGHTS.polygon2SWM(inputFC, swmFile, masterField, concept=concept,
                                    kNeighs=kNeighs, rowStandard=rowStandard,
                                    contiguityType="QUEEN")

        elif wType == 9:
            ARCPY.AddMessage(ARCPY.GetIDMessage(84255))
            w = WEIGHTS.spaceTime2SWM(inputFC, swmFile, masterField, concept=concept,
                                      threshold=threshold, rowStandard=rowStandard,
                                      timeField=timeField, timeType=timeType,
                                      timeValue=timeValue,
                                      zEnabled=zEnabled)

        else:
            #### Tabular Input for Weights ####
            ARCPY.AddMessage(ARCPY.GetIDMessage(84123))
            if tableFile == "" or tableFile == "#":
                ARCPY.AddIDMessage("Error", 721)
                raise SystemExit()
            else:
                WEIGHTS.table2SWM(inputFC, masterField, swmFile, tableFile,
                                  rowStandard=rowStandard)


class DensityBasedClustering(object):
    def __init__(self):
        self.label = "Density-based Clustering"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030008
        self.methods = ["DBSCAN", "HDBSCAN", "OPTICS"]
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point']

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Cluster Method",
                                 name="cluster_method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")

        param2.filter.type = "ValueList"

        param2.filter.list = ['DBSCAN', 'HDBSCAN', 'OPTICS']

        param3 = ARCPY.Parameter(displayName="Minimum Number of Features per Cluster",
                                 name="min_features_cluster",
                                 datatype="GPLong",
                                 parameterType="Required",
                                 direction="Input")

        param3.filter.type = "Range"
        param3.filter.list = [2, 100000000]

        param4 = ARCPY.Parameter(displayName="Search Distance",
                                 name="search_distance",
                                 datatype="GPLinearUnit",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = supportDist
        param4.enabled = False

        param5 = ARCPY.Parameter(displayName="Cluster Sensitivity",
                                 name="cluster_sensitivity",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")

        param5.enabled = False
        param5.filter.type = "Range"
        param5.filter.list = [0, 100]

        return [param0, param1, param2, param3, param4, param5]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        method = self.params[2]
        minNFea = self.params[3]
        sDistance = self.params[4]
        noise = self.params[5]

        if self.params[2].value:
            if self.params[2].value == self.methods[1]:
                enableParameters([minNFea], [sDistance, noise])
            elif self.params[2].value == self.methods[2]:
                enableParameters([minNFea, sDistance, noise], [])
            elif self.params[2].value == self.methods[0]:
                enableParameters([minNFea, sDistance], [noise])
        return

    def updateMessages(self, parameters):
        self.params = parameters
        minNFea = self.params[3]
        noise = self.params[5]
        sDistance = self.params[4]
        method = self.params[2]

        if noise.value:
            if UTILS.getNumericParameter(5, self.params) <= 0 or UTILS.getNumericParameter(5, self.params) > 100:
                noise.setIDMessage("ERROR", 854, 0, 100)

        if method.value:
            if method.value in ['DBSCAN']:
                if sDistance.value is not None:
                    value = getLinearUnitFloat(sDistance.value)
                    if value <= 0.0:
                        sDistance.setIDMessage("ERROR", 323)

            if method.value in ['OPTICS']:
                if sDistance.value is not None:
                    value = getLinearUnitFloat(sDistance.value)
                    if value <= 0.0:
                        sDistance.setIDMessage("ERROR", 323)

        if minNFea.value:
            value = UTILS.getNumericParameter(3, self.params)
            if value <= 1:
                minNFea.setIDMessage("ERROR", 110143)

        if minNFea.value == 0:
            minNFea.setIDMessage("ERROR", 110143)
        return

    def execute(self, parameters, messages):
        import SSCluster as SC

        inputFC = UTILS.getTextParameter(0, parameters)
        outputFC = UTILS.getTextParameter(1, parameters)
        typeValue = UTILS.getTextParameter(2, parameters)
        minClusterSize = int(UTILS.getTextParameter(3, parameters))
        distance = UTILS.getTextParameter(4, parameters)
        noise = UTILS.getNumericParameter(5, parameters)

        if distance in ["", "#"]:
            distance = None

        layer = None
        cluster = None

        threads = UTILS.getNumberOfThreadsDefault()
        if typeValue == 'DBSCAN':
            cluster = SC.DBSCAN(inputFC, outputFC, minClusterSize, distance, parallel=threads)
        if typeValue == 'HDBSCAN':
            cluster = SC.HDBSCAN(inputFC, outputFC, minClusterSize, parallel=threads)
        if typeValue == 'OPTICS':
            cluster = SC.OPTICS(inputFC, outputFC, minClusterSize, distance, noise, parallel=threads)

        cluster.run()
        layer = cluster.output()
        del cluster

        paramOutput = parameters[1]

        #### Bar Chart ####
        bChart = ARCPY.Chart(ARCPY.GetIDMessage(84783))
        bChart.type = "bar"
        bChart.title = ARCPY.GetIDMessage(84783)

        #### Assign X Axis Field ####
        bChart.xAxis.field = "CLUSTER_ID"
        bChart.xAxis.title = ARCPY.GetIDMessage(84790)
        bChart.xAxis.sort = "ASC"
        bChart.yAxis.field = ""
        bChart.yAxis.title = ARCPY.GetIDMessage(84785)
        bChart.bar.aggregation = "COUNT"

        if typeValue == 'OPTICS':
            chart = ARCPY.Chart(ARCPY.GetIDMessage(84769))
            chart.type = "scatter"
            chart.title = ARCPY.GetIDMessage(84769)
            chart.scatter.showTrendLine = False
            #### Assign Y Axis Field ####
            chart.yAxis.field = "REACHDIST"
            chart.yAxis.title = ARCPY.GetIDMessage(84770)

            #### Assign X Axis Field ####
            chart.xAxis.field = "REACHORDER"
            chart.xAxis.title = ARCPY.GetIDMessage(84771)
            paramOutput.charts = [chart, bChart]
        elif typeValue == 'HDBSCAN':
            hProb = ARCPY.Chart(ARCPY.GetIDMessage(84782))
            hProb.type = "histogram"
            hProb.title = ARCPY.GetIDMessage(84782)
            hProb.xAxis.field = "PROB"
            hProb.xAxis.title = ARCPY.GetIDMessage(84789)
            hProb.histogram.showMean = False
            paramOutput.charts = [hProb, bChart]
        else:
            paramOutput.charts = [bChart]
        try:
            paramOutput.symbology = layer
        except:
            ARCPY.AddIDMessage("WARNING", 973)
            pass

        return


class SpatiallyConstrainedMultivariateClustering(object):
    def __init__(self):
        self.label = "Spatially Constrained Multivariate Clustering"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030010
        self.allSpaceTypes = ["CONTIGUITY_EDGES_ONLY",
                              "CONTIGUITY_EDGES_CORNERS",
                              "TRIMMED_DELAUNAY_TRIANGULATION",
                              "GET_SPATIAL_WEIGHTS_FROM_FILE"]
        self.pointSpaceTypes = ["TRIMMED_DELAUNAY_TRIANGULATION",
                                "GET_SPATIAL_WEIGHTS_FROM_FILE"]
        self.skaterShape2Layer = {"POINT": "MultiVarClusterPoints.lyrx",
                                  "POLYGON": "MultiVarClusterPolygons.lyrx"}
        self.params = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param0.filter.list = ['Point', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Analysis Fields",
                                 name="analysis_fields",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param2.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']

        param2.parameterDependencies = ["in_features"]

        param3 = ARCPY.Parameter(displayName="Cluster Size Constraints",
                                 name="size_constraints",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param3.filter.type = "ValueList"

        param3.filter.list = ['NONE', 'NUM_FEATURES', 'ATTRIBUTE_VALUE']

        param3.value = 'NONE'

        param4 = ARCPY.Parameter(displayName="Constraint Field",
                                 name="constraint_field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ['Short', 'Long', 'Float', 'Double']
        param4.parameterDependencies = ["in_features"]

        param5 = ARCPY.Parameter(displayName="Minimum per Cluster",
                                 name="min_constraint",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")

        param6 = ARCPY.Parameter(displayName="Maximum per Cluster",
                                 name="max_constraint",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")

        param7 = ARCPY.Parameter(displayName="Number of Clusters",
                                 name="number_of_clusters",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")

        param8 = ARCPY.Parameter(displayName="Spatial Constraints",
                                 name="spatial_constraints",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param8.filter.type = "ValueList"

        param8.filter.list = ['CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS', 'TRIMMED_DELAUNAY_TRIANGULATION',
                              'GET_SPATIAL_WEIGHTS_FROM_FILE']

        param9 = ARCPY.Parameter(displayName="Spatial Weight Matrix File",
                                 name="weights_matrix_file",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param9.filter.list = ['swm', 'gwt']
        param10 = ARCPY.Parameter(displayName="Number of Permutations",
                                  name="number_of_permutations",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param10.filter.list = [0, 100, 200, 500, 1000]
        param10.value = 0
        param11 = ARCPY.Parameter(displayName="Output Table",
                                  name="output_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.params = parameters
        self.fieldObjects = {}
        if paramChanged(parameters[0]):
            try:
                desc = ARCPY.Describe(parameters[0].value)
                shapeType = desc.shapeType.upper()
                if shapeType.upper() == "POLYGON":
                    parameters[8].filter.list = self.allSpaceTypes
                else:
                    parameters[8].filter.list = self.pointSpaceTypes

                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                parameters[8].filter.list = self.allSpaceTypes

        #### SWM File ####
        if parameters[8].value == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            parameters[9].enabled = True
        else:
            parameters[9].enabled = False

        #### Min/Max Constraints ####
        if parameters[3].value == "NUM_FEATURES":
            parameters[4].value = None
            parameters[4].enabled = False
            parameters[5].enabled = True
            parameters[6].enabled = True
        elif parameters[3].value == "ATTRIBUTE_VALUE":
            parameters[4].enabled = True
            parameters[5].enabled = True
            parameters[6].enabled = True
        else:
            parameters[4].value = None
            parameters[4].enabled = False
            parameters[5].enabled = False
            parameters[6].enabled = False

        #### Disable Num Groups, Perms and Optimize Table with Max Constraint ####
        if parameters[3].value != "NONE":
            minValue = UTILS.getNumericParameter(5, parameters)
            maxValue = UTILS.getNumericParameter(6, parameters)
            if parameters[3].value == "NUM_FEATURES":
                if minValue is not None:
                    minValue = int(minValue)
                    parameters[5].value = minValue
                if maxValue is not None:
                    maxValue = int(maxValue)
                    parameters[6].value = maxValue
            if maxValue is not None:
                parameters[7].value = None
                parameters[7].enabled = False
                parameters[10].enabled = False
                parameters[11].enabled = False
                parameters[11].value = None
            else:
                parameters[7].enabled = True
                parameters[10].enabled = True
                parameters[11].enabled = True
        else:
            parameters[7].enabled = True
            parameters[10].enabled = True
            parameters[11].enabled = True

        #### Clear and Gray Out Max Constraint if Permutations ####
        if parameters[10].value:
            parameters[6].value = None
            parameters[6].enabled = False

        #### Default Spatial Constraint ####
        if parameters[0].value and parameters[8].value in [None, ""]:
            try:
                desc = ARCPY.Describe(parameters[0].value)
                shapeType = desc.shapeType.upper()
                if shapeType.upper() == "POLYGON":
                    parameters[8].value = "CONTIGUITY_EDGES_CORNERS"
                else:
                    parameters[8].value = "TRIMMED_DELAUNAY_TRIANGULATION"
            except:
                pass

        #### Analysis Field(s) ####
        addFields = []
        if parameters[2].value:
            for fieldName in parameters[2].value.exportToString().split(";"):
                if fieldName in self.fieldObjects:
                    addFields.append(self.fieldObjects[fieldName])

        if parameters[3].value == "ATTRIBUTE_VALUE" and parameters[4].value:
            fieldName = parameters[4].value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["CLUSTER_ID"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "LONG"
            addFields.append(newField)
        parameters[1].schema.additionalFields = addFields
        self.params[1].schema.featureTypeRule = "AsSpecified"
        self.params[1].schema.featureType = "Simple"
        self.params[1].schema.geometryTypeRule = "AsSpecified"
        self.params[1].schema.fieldsRule = "None"

        #### Output Table ####
        if parameters[11].value:
            fieldNames = ["NUM_GROUPS", "PSEUDO_F"]
            fieldTypes = ["LONG", "DOUBLE"]
            tabFields = []
            for fieldInd, fieldName in enumerate(fieldNames):
                newField = ARCPY.Field()
                newField.name = fieldName
                newField.type = fieldTypes[fieldInd]
                tabFields.append(newField)
            self.params[11].schema.additionalFields = tabFields

        return

    def updateMessages(self, parameters):
        self.params = parameters
        #### Positive K > 1 When Chosen ####
        numGroups = UTILS.getNumericParameter(7, parameters)
        if numGroups is not None:
            if numGroups < 2:
                parameters[7].setIDMessage("ERROR", 110128, 2)

        #### Must Choose Sum Field ####
        if parameters[3].value == "ATTRIBUTE_VALUE":
            sumField = UTILS.getTextParameter(4, parameters, fieldName=True)
            if sumField is None:
                parameters[4].setIDMessage("ERROR", 110136)

        #### Min Must Be Smaller Than Max ####
        minNumValues = UTILS.getNumericParameter(5, parameters)
        maxNumValues = UTILS.getNumericParameter(6, parameters)
        if minNumValues is not None and maxNumValues is not None:
            if minNumValues >= maxNumValues:
                parameters[5].setIDMessage("ERROR", 110137)

        #### Must Be Positive Greater than Zero ####
        if minNumValues is not None:
            if minNumValues <= 0:
                parameters[5].setIDMessage("ERROR", 110138)

        if maxNumValues is not None:
            if maxNumValues <= 0:
                parameters[6].setIDMessage("ERROR", 110138)

        if parameters[1].value and parameters[11].value:
            fc = parameters[1].valueAsText
            tbl = parameters[11].valueAsText
            fcNoExt = fc.lower().replace(".shp", "")
            tblNoExt = tbl.lower().replace(".dbf", "")
            if fcNoExt == tblNoExt:
                parameters[11].setIDMessage("ERROR", 605, tbl, fc)

        if parameters[11].value:
            tbl = parameters[11].valueAsText
            if ".txt" in tbl:
                parameters[11].setIDMessage("ERROR", 210, tbl)

    def execute(self, parameters, messages):
        import SKATER as SK

        #### User Defined Inputs ####
        inputFC = parameters[0].valueAsText
        outputFC = parameters[1].valueAsText

        #### Analysis Fields ####
        analysisFields = parameters[2].valueAsText
        analysisFields = analysisFields.split(";")
        analysisFields = [i.upper() for i in analysisFields]
        fieldList = [i for i in analysisFields]

        #### Search Conditions ####
        minNumFeatures = None
        maxNumFeatures = None
        minNumValues = None
        maxNumValues = None
        searchCondition = UTILS.getTextParameter(3, parameters)
        sumField = UTILS.getTextParameter(4, parameters, fieldName=True)
        if searchCondition not in ["NONE", None]:
            if searchCondition == "ATTRIBUTE_VALUE":
                minNumValues = UTILS.getNumericParameter(5, parameters)
                maxNumValues = UTILS.getNumericParameter(6, parameters)
                if sumField not in fieldList:
                    fieldList.append(sumField)
            else:
                sumField = None
                minNumFeatures = UTILS.getNumericParameter(5, parameters)
                maxNumFeatures = UTILS.getNumericParameter(6, parameters)
                if minNumFeatures is not None:
                    minNumFeatures = int(minNumFeatures)
                if maxNumFeatures is not None:
                    maxNumFeatures = int(maxNumFeatures)

        #### Number of Groups ####
        kPartitions = UTILS.getNumericParameter(7, parameters)

        #### Conceptualization ####
        spaceConcept = UTILS.getTextParameter(8, parameters)

        #### Number of Neighbors ####
        numNeighs = 2

        #### Spatial Weights Matrix File ####
        weightsFile = UTILS.getTextParameter(9, parameters)
        useWeightsFile = spaceConcept == "GET_SPATIAL_WEIGHTS_FROM_FILE"
        if not weightsFile and useWeightsFile:
            ARCPY.AddIDMessage("ERROR", 930)
            raise SystemExit()
        if weightsFile and not useWeightsFile:
            weightsFile = None

        #### Number of Permutations ####
        permutations = UTILS.getNumericParameter(10, parameters)
        if permutations is None:
            permutations = 0

        #### FStat Table ####
        outputTable = parameters[11].valueAsText

        #### Warn About Chordal Bool ####
        useChordal = spaceConcept not in self.pointSpaceTypes

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC,
                                 useChordal=useChordal)

        #### Set Unique ID Field ####
        masterField = UTILS.setUniqueIDField(ssdo, weightsFile=weightsFile)

        #### Populate SSDO with Data ####
        if useChordal:
            ssdo.obtainData(masterField, fieldList, minNumObs=3,
                            requireSearch=True, warnNumObs=30)
        else:
            ssdo.obtainData(masterField, fieldList, minNumObs=3,
                            warnNumObs=30)

        #### Execute ####
        skater = SK.SKATER(ssdo, analysisFields, spaceConcept=spaceConcept,
                           distConcept="EUCLIDEAN", numNeighs=numNeighs,
                           weightsFile=weightsFile, kPartitions=kPartitions,
                           sumField=sumField, minNumFeatures=minNumFeatures,
                           maxNumFeatures=maxNumFeatures, minNumValues=minNumValues,
                           maxNumValues=maxNumValues, permutations=permutations,
                           outputTable=outputTable)

        skater.report()

        #### Permutations / Gather Evidence and Calculate Probabilities ####
        if skater.doPermutations > 0:
            skater.getEvidenceProbs()

        #### Create OutputFC ####
        skater.createOutput(outputFC)

        #### Set the Default Symbology ####
        try:
            renderLayerFile = self.skaterShape2Layer[ssdo.shapeType.upper()]
            templateDir = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates", "Layers")
            fullRLF = OS.path.join(templateDir, renderLayerFile)
            parameters[1].symbology = fullRLF
        except:
            ARCPY.AddIDMessage("WARNING", 973)

        #### Set Chart Output ####
        if UTILS.isPRO():

            #### Bar Chart ####
            bChart = ARCPY.Chart(ARCPY.GetIDMessage(84783))
            bChart.type = "bar"
            bChart.title = ARCPY.GetIDMessage(84783)

            #### Assign X Axis Field ####
            bChart.xAxis.field = "CLUSTER_ID"
            bChart.xAxis.title = ARCPY.GetIDMessage(84751)
            bChart.xAxis.sort = "ASC"
            bChart.yAxis.field = ""
            bChart.yAxis.title = ARCPY.GetIDMessage(84785)
            bChart.bar.aggregation = "COUNT"

            #### Box Plots ####
            box = ARCPY.Chart(ARCPY.GetIDMessage(84780))
            box.type = "boxPlot"
            box.title = ARCPY.GetIDMessage(84780)

            #### Assign Y Axis Field ####
            outPath, outName = OS.path.split(outputFC)
            plotFieldNames = [ssdo.fields[i].name for i in analysisFields]
            plotFieldNames = UTILS.createAppendFieldNames(plotFieldNames, outPath)

            box.yAxis.field = plotFieldNames
            if len(plotFieldNames) == 1:
                box.yAxis.title = ARCPY.GetIDMessage(84974)
            else:
                box.yAxis.title = ARCPY.GetIDMessage(84269)

            #### Assign X Axis Field ####
            box.xAxis.field = ""
            box.xAxis.title = ARCPY.GetIDMessage(84399)

            #### Set Box Plot Properties ####
            box.boxPlot.splitCategory = "CLUSTER_ID"
            box.boxPlot.splitCategoryAsMeanLine = True
            box.boxPlot.standardizeValues = True

            chartList = [box, bChart]
            probFieldName = "MEM_PROB"
            if skater.permutations:
                perm = ARCPY.Chart(ARCPY.GetIDMessage(84782))
                perm.type = "histogram"
                perm.histogram.showMean = False
                perm.title = ARCPY.GetIDMessage(84782)
                perm.xAxis.field = probFieldName
                perm.xAxis.title = ARCPY.GetIDMessage(84789)
                perm.histogram.showMean = False
                chartList.append(perm)

            parameters[1].charts = chartList

            if outputTable is not None:
                #### FStat Plot ####
                chart = ARCPY.Chart(ARCPY.GetIDMessage(84772))
                chart.type = "line"
                chart.title = ARCPY.GetIDMessage(84772)

                #### Assign X Axis Field ####
                chart.xAxis.field = "NUM_GROUPS"
                chart.xAxis.title = ARCPY.GetIDMessage(84764)

                #### Assign Y Axis Field ####
                chart.yAxis.field = "PSEUDO_F"
                chart.yAxis.title = ARCPY.GetIDMessage(84773)

                #### Sort by X ####
                # chart.xAxis.sort = chart.xAxis.field

                parameters[11].charts = [chart]


class MultivariateClustering(object):
    def __init__(self):
        self.label = "Multivariate Clustering"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030009
        self.params = None
        self.fieldObjects = None
        self.kMeansShape2Layer = {"POINT": "MultiVarClusterPoints.lyrx",
                                  "MULTIPOINT": "MultiVarClusterPoints.lyrx",
                                  "POLYGON": "MultiVarClusterPolygons.lyr",
                                  "POLYLINE": "MultiVarClusterLines.lyr"}

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param1.schema.featureTypeRule = "AsSpecified"
        param1.schema.featureType = "Simple"
        param1.schema.geometryTypeRule = "AsSpecified"
        param1.schema.fieldsRule = "None"

        param2 = ARCPY.Parameter(displayName="Analysis Fields",
                                 name="analysis_fields",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input",
                                 multiValue=True)
        param2.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']

        param2.parameterDependencies = ["in_features"]

        param3 = ARCPY.Parameter(displayName="Clustering Method",
                                 name="clustering_method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param3.filter.type = "ValueList"
        param3.filter.list = ['K_MEANS', 'K_MEDOIDS']
        param3.value = 'K_MEANS'

        param4 = ARCPY.Parameter(displayName="Initialization Method",
                                 name="initialization_method",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")

        param4.filter.type = "ValueList"

        param4.filter.list = ['OPTIMIZED_SEED_LOCATIONS', 'USER_DEFINED_SEED_LOCATIONS', 'RANDOM_SEED_LOCATIONS']

        param4.value = 'OPTIMIZED_SEED_LOCATIONS'

        param5 = ARCPY.Parameter(displayName="Initialization Field",
                                 name="initialization_field",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")

        param5.parameterDependencies = ["in_features"]
        param5.filter.list = ['Short', 'Long']

        param6 = ARCPY.Parameter(displayName="Number of Clusters",
                                 name="number_of_clusters",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")

        param7 = ARCPY.Parameter(displayName="Output Table",
                                 name="output_table",
                                 datatype="DETable",
                                 parameterType="Optional",
                                 direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6, param7]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        self.fieldObjects = {}
        if paramChanged(parameters[0]):
            try:
                #### Set Output Symbology ####
                desc = ARCPY.Describe(parameters[0].value)
                shapeType = desc.shapeType.upper()
                renderLayerFile = self.kMeansShape2Layer[shapeType]
                templateDir = OS.path.join(OS.path.dirname(SYS.path[0]),
                                           "Templates", "Layers")
                fullRLF = OS.path.join(templateDir, renderLayerFile)
                parameters[1].symbology = fullRLF

                for field in desc.fields:
                    self.fieldObjects[field.name] = field
            except:
                pass

        #### Set Initialization Info ####
        initApproach = parameters[4].value
        if initApproach == "USER_DEFINED_SEED_LOCATIONS":
            #### No K-Partitions or Optimized Option ####
            parameters[5].enabled = True
            parameters[6].value = None
            parameters[6].enabled = False
            parameters[7].value = None
            parameters[7].enabled = False
        else:
            parameters[5].enabled = False
            parameters[6].enabled = True
            parameters[7].enabled = True

        #### Analysis Field(s) ####
        addFields = []
        if parameters[2].value:
            for fieldName in parameters[2].value.exportToString().split(";"):
                if fieldName in self.fieldObjects:
                    addFields.append(self.fieldObjects[fieldName])

        if initApproach == "USER_DEFINED_SEED_LOCATIONS" and parameters[5].value:
            fieldName = parameters[5].value
            if fieldName in self.fieldObjects:
                addFields.append(self.fieldObjects[fieldName])

        fieldNames = ["CLUSTER_ID", "IS_SEED"]

        for fieldName in fieldNames:
            newField = ARCPY.Field()
            newField.name = fieldName
            newField.type = "LONG"
            addFields.append(newField)
        parameters[1].schema.additionalFields = addFields

        #### Output Table ####
        if parameters[7].value:
            fieldNames = ["NUM_GROUPS", "PSEUDO_F"]
            fieldTypes = ["LONG", "DOUBLE"]
            tabFields = []
            for fieldInd, fieldName in enumerate(fieldNames):
                newField = ARCPY.Field()
                newField.name = fieldName
                newField.type = fieldTypes[fieldInd]
                addFields.append(newField)
            parameters[7].schema.additionalFields = addFields
        return

    def updateMessages(self, parameters):
        #### Positive K > 1 When Chosen ####
        numGroups = UTILS.getNumericParameter(6, parameters)
        if numGroups is not None:
            if numGroups < 2:
                parameters[6].setIDMessage("ERROR", 110128, 2)

        #### Must Choose Init Field ####
        if parameters[4].value == "USER_DEFINED_SEED_LOCATIONS":
            initField = UTILS.getTextParameter(5, parameters, fieldName=True)
            if initField is None:
                parameters[5].setIDMessage("ERROR", 1327)

        if parameters[1].value and parameters[7].value:
            fc = parameters[1].valueAsText
            tbl = parameters[7].valueAsText
            fcNoExt = fc.lower().replace(".shp", "")
            tblNoExt = tbl.lower().replace(".dbf", "")
            if fcNoExt == tblNoExt:
                parameters[7].setIDMessage("ERROR", 605, tbl, fc)

        if parameters[7].value:
            tbl = parameters[7].valueAsText
            if ".txt" in tbl:
                parameters[7].setIDMessage("ERROR", 210, tbl)
        return

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import MultivariateClustering as MC

        #### User Defined Inputs ####
        inputFC = parameters[0].valueAsText
        outputFC = parameters[1].valueAsText

        #### Analysis Fields ####
        analysisFields = parameters[2].valueAsText
        analysisFields = analysisFields.split(";")
        analysisFields = [i.upper() for i in analysisFields]
        fieldList = [i for i in analysisFields]

        #### Clustering Method ####
        clusterMethod = UTILS.getTextParameter(3, parameters)
        if clusterMethod not in ['K_MEANS', 'K_MEDOIDS']:
            clusterMethod = 'K_MEANS'

        #### Init Conditions ####
        initMethod = parameters[4].valueAsText
        if initMethod == "USER_DEFINED_SEED_LOCATIONS":
            initField = UTILS.getTextParameter(5, parameters, fieldName=True)
            fieldList.append(initField)
        else:
            initField = None

        #### Number of Groups ####
        kPartitions = UTILS.getNumericParameter(6, parameters)

        #### FStat Table ####
        outputTable = parameters[7].valueAsText

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC, useChordal=False)

        #### Populate SSDO with Data ####
        ssdo.obtainData(ssdo.oidName, fieldList, minNumObs=3, warnNumObs=30)

        #### Execute ####
        clust = MC.MultivariateClustering(ssdo, analysisFields.copy(), initMethod=initMethod,
                                          initField=initField, kPartitions=kPartitions,
                                          outputTable=outputTable,
                                          clusterMethod=clusterMethod)

        clust.report()

        #### Create OutputFC ####
        clust.createOutput(outputFC)

        #### Set the Default Symbology ####
        renderLayerFile = self.kMeansShape2Layer[ssdo.shapeType.upper()]

        #### Render Results ####
        try:
            templateDir = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates", "Layers")
            fullRLF = OS.path.join(templateDir, renderLayerFile)
        except:
            ARCPY.AddIDMessage("WARNING", 973)

        #### Set Chart Output ####
        if UTILS.isPRO():

            #### Bar Chart ####
            bChart = ARCPY.Chart(ARCPY.GetIDMessage(84783))
            bChart.type = "bar"
            bChart.title = ARCPY.GetIDMessage(84783)

            #### Assign X Axis Field ####
            bChart.xAxis.field = "CLUSTER_ID"
            bChart.xAxis.title = ARCPY.GetIDMessage(84751)
            bChart.xAxis.sort = "ASC"
            bChart.yAxis.field = ""
            bChart.yAxis.title = ARCPY.GetIDMessage(84785)
            bChart.bar.aggregation = "COUNT"

            #### Box Plots ####
            box = ARCPY.Chart(ARCPY.GetIDMessage(84774))
            box.type = "boxPlot"
            box.title = ARCPY.GetIDMessage(84774)

            #### Assign Y Axis Field ####
            outPath, outName = OS.path.split(outputFC)
            plotFieldNames = [ssdo.fields[i].name for i in analysisFields]
            plotFieldNames = UTILS.createAppendFieldNames(plotFieldNames, outPath)
            box.yAxis.field = plotFieldNames
            box.yAxis.title = ARCPY.GetIDMessage(84269)

            #### Assign X Axis Field ####
            box.xAxis.field = ""
            box.xAxis.title = ARCPY.GetIDMessage(84399)

            #### Set Box Plot Properties ####
            box.boxPlot.splitCategory = "CLUSTER_ID"
            box.boxPlot.splitCategoryAsMeanLine = True
            box.boxPlot.standardizeValues = True

            parameters[1].charts = [box, bChart]

            if outputTable is not None:
                #### FStat Plot ####
                chart = ARCPY.Chart(ARCPY.GetIDMessage(84772))
                chart.type = "line"
                chart.title = ARCPY.GetIDMessage(84772)

                #### Assign X Axis Field ####
                chart.xAxis.field = "NUM_GROUPS"
                chart.xAxis.title = ARCPY.GetIDMessage(84764)

                #### Assign Y Axis Field ####
                chart.yAxis.field = "PSEUDO_F"
                chart.yAxis.title = ARCPY.GetIDMessage(84773)

                #### Sort by X ####
                # chart.xAxis.sort = chart.xAxis.field

                parameters[7].charts = [chart]


class Forest(object):
    def __init__(self):
        self.label = "Forest-based Classification and Regression"
        self.description = ""
        self.canRunInBackground = False
        self.helpContext = 9060006
        self.category = "Modeling Spatial Relationships"
        self.shapeType = None
        self.fieldNames = None
        self.fieldAlias = None
        self.rfD = None
        self.fieldInput = {}
        self.fileExt = ".RFM"
        self.discrete = "(CAT)"
        self.continuous = "(CNT)"
        self.notDisplay = ["OID", "FID", "SHAPE", "OBJECTID", "SHAPE_LENG", "SHAPE_AREA"]
        self.noTypeDisplay = ["OID", "FID", "DATE"]
        self.varTypeRev = {"(CNT)": 'Numeric', "(DSC)": 'Categorical'}
        self.typeOperationPolygon = ["AVG", "MAJORITY", "SUM"]
        self.typeOperationPoint = ["None"]
        self.isPolygon = False
        self.dbg = ""
        self.desc = None
        self.descF2P = None
        self.fieldAliasF2P = None
        self.fieldNamesF2P = None
        self.modelCreated = ''
        self.lic = True
        self.near = True

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Operation Mode",
                                 name="prediction_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ["TRAIN", "PREDICT_FEATURES", "PREDICT_RASTER"]
        param0.value = "TRAIN"
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Input Training Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")

        param1.filter.list = ["Polygon", "Point"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Variable to Predict",
                                 name="variable_predict",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param2.filter.list = ["Double", "Float", "Short", "Long", "Text"]
        param2.parameterDependencies = [param1.name]
        param2.displayOrder = 2

        param3 = ARCPY.Parameter(displayName="Treat Variable as Categorical",
                                 name="treat_variable_as_categorical",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ["CATEGORICAL", "NUMERIC"]
        param3.displayOrder = 3

        param4 = ARCPY.Parameter(displayName="Explanatory Training Variables",
                                 name="explanatory_variables",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")
        param4.displayOrder = 4
        param4.parameterDependencies = [param1.name]
        param4.columns = [['Field', 'Variable'], ['GPBoolean', 'Categorical']]
        param4.filters[0].list = ["Double", "Float", "Short", "Long", "Text"]
        param4.filters[1].type = "ValueList"
        param4.filters[1].list = ["CATEGORICAL", "NUMERIC"]

        param5 = ARCPY.Parameter(displayName="Explanatory Training Distance Features",
                                 name="distance_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param5.filter.list = ["Polygon", "Point", "Polyline"]
        param5.displayOrder = 5

        param6 = ARCPY.Parameter(displayName="Explanatory Training Rasters",
                                 name="explanatory_rasters",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")
        param6.columns = [['GPRasterLayer', 'Variable'], ['GPBoolean', 'Categorical']]
        param6.filters[1].type = "ValueList"
        param6.filters[1].list = ["CATEGORICAL", "NUMERIC"]
        param6.displayOrder = 6

        param7 = ARCPY.Parameter(displayName="Input Predict Features",
                                 name="features_to_predict",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param7.displayOrder = 7

        param8 = ARCPY.Parameter(displayName="Output Prediction Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Optional",
                                 direction="Output")
        param8.displayOrder = 8
        param8.parameterDependencies = [param7.name]

        param9 = ARCPY.Parameter(displayName="Output Prediction Raster",
                                 name="output_raster",
                                 datatype="DERasterDataset",
                                 parameterType="Optional",
                                 direction="Output")
        param9.displayOrder = 9

        param10 = ARCPY.Parameter(displayName="Match Explanatory Variables",
                                  name="explanatory_variable_matching",
                                  datatype="GPValueTable",
                                  parameterType="Optional",
                                  direction="Input")
        param10.columns = [['Field', 'Prediction'], ['GPString', 'Training']]
        param10.filters[0].list = ["Double", "Float", "Short", "Long", "Text"]
        param10.parameterDependencies = [param7.name]
        param10.controlCLSID = "{C99D0042-EF42-4B04-8A0B-1A53F6DB67A6}"
        param10.displayOrder = 10

        param11 = ARCPY.Parameter(displayName="Match Distance Features",
                                  name="explanatory_distance_matching",
                                  datatype="GPValueTable",
                                  parameterType="Optional",
                                  direction="Input")
        param11.columns = [['GPFeatureLayer', 'Prediction'], ['GPString', 'Training']]
        param11.filters[0].list = ["Polygon", "Point", "Polyline"]
        param11.controlCLSID = "{C99D0042-EF42-4B04-8A0B-1A53F6DB67A6}"
        param11.displayOrder = 11

        param12 = ARCPY.Parameter(displayName="Match Explanatory Rasters",
                                  name="explanatory_rasters_matching",
                                  datatype="GPValueTable",
                                  parameterType="Optional",
                                  direction="Input")
        param12.columns = [['GPRasterLayer', 'Prediction'], ['GPString', 'Training']]
        param12.controlCLSID = "{C99D0042-EF42-4B04-8A0B-1A53F6DB67A6}"
        param12.displayOrder = 12

        param13 = ARCPY.Parameter(displayName="Output Trained Features",
                                  name="output_trained_features",
                                  datatype="DEFeatureClass",
                                  parameterType="Optional",
                                  direction="Output")
        param13.displayOrder = 13
        param13.parameterDependencies = [param1.name]
        param13.category = "Additional Outputs"

        param14 = ARCPY.Parameter(displayName="Output Variable Importance Table",
                                  name="output_importance_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")
        param14.displayOrder = 14
        param14.category = "Additional Outputs"

        param15 = ARCPY.Parameter(displayName="Convert Polygons to Raster Resolution for Training",
                                  name="use_raster_values",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param15.filter.list = ["TRUE", "FALSE"]
        param15.category = "Advanced Forest Options"
        param15.value = True
        param15.displayOrder = 17

        param16 = ARCPY.Parameter(displayName="Number of Trees",
                                  name="number_of_trees",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")

        param16.category = "Advanced Forest Options"
        param16.displayOrder = 18
        param16.filter.type = "Range"
        param16.filter.list = [0, 10000000]
        param16.value = 100

        param17 = ARCPY.Parameter(displayName="Minimum Leaf Size",
                                  name="minimum_leaf_size",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param17.category = "Advanced Forest Options"
        param17.filter.type = "Range"
        param17.filter.list = [1, 10000000]
        param17.displayOrder = 19

        param18 = ARCPY.Parameter(displayName="Maximum Tree Depth ",
                                  name="maximum_depth",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param18.category = "Advanced Forest Options"
        param18.filter.type = "Range"
        param18.filter.list = [0, 100000000]
        param18.displayOrder = 20

        param19 = ARCPY.Parameter(displayName="Percentage of Training Available per Tree",
                                  name="sample_size",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param19.filter.type = "Range"
        param19.filter.list = [1, 100]
        param19.value = 100
        param19.displayOrder = 21
        param19.category = "Advanced Forest Options"

        param20 = ARCPY.Parameter(displayName="Number of Randomly Sampled Variables",
                                  name="random_variables",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param20.category = "Advanced Forest Options"
        param20.filter.type = "Range"
        param20.filter.list = [1, 10000000]
        param20.displayOrder = 22

        param21 = ARCPY.Parameter(displayName="Percentage of Training Data to Exclude for Validation",
                                  name="percentage_for_training",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")
        param21.category = "Validation Options"
        param21.filter.type = "Range"
        param21.filter.list = [0.0, 50.0]
        param21.value = 10.0
        param21.displayOrder = 23

        param22 = ARCPY.Parameter(displayName="Output Classification Performance Table",
                                  name="output_classification_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")
        param22.displayOrder = 15
        param22.category = "Additional Outputs"

        param23 = ARCPY.Parameter(displayName="Output Validation Table",
                                  name="output_validation_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")
        param23.displayOrder = 25
        param23.category = "Validation Options"

        param24 = ARCPY.Parameter(displayName="Compensate For Sparse Categories",
                                  name="compensate_sparse_categories",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param24.filter.list = ["TRUE", "FALSE"]
        param24.category = "Advanced Forest Options"
        param24.displayOrder = 16

        param25 = ARCPY.Parameter(displayName="Number of Runs for Validation",
                                  name="number_validation_runs",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param25.category = "Validation Options"
        param25.filter.type = "Range"
        param25.value = 1
        param25.filter.list = [1, 10000000]
        param25.displayOrder = 24

        param26 = ARCPY.Parameter(displayName="Calculate Uncertainty",
                                  name="calculate_uncertainty",
                                  datatype="GPBoolean",
                                  parameterType="Optional",
                                  direction="Input")
        param26.filter.list = ["TRUE", "FALSE"]
        param26.category = "Validation Options"
        param26.displayOrder = 26
        param26.value = False

        param27 = ARCPY.Parameter(displayName="Output Uncertainty Raster Layers",
                                  name="output_uncertainty_raster_layers",
                                  datatype="GPRasterLayer",
                                  parameterType="Derived",
                                  direction="Output",
                                  multiValue=True)

        if ARCPY.CheckExtension("spatial") != "Available":
            self.lic = False

        if self.lic:
            param0.filter.list = ["TRAIN", "PREDICT_FEATURES", "PREDICT_RASTER"]
        else:
            param0.filter.list = ["TRAIN", "PREDICT_FEATURES"]

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8,
                param9, param10, param11, param12, param13, param14, param15, param16,
                param17, param18, param19, param20, param21, param22, param23,
                param24, param25, param26, param27]

    def isLicensed(self):
        return True

    def getFieldName(self, text):
        if self.discrete in text:
            return text.replace(self.discrete, "").strip()
        elif self.continuous in text:
            return text.replace(self.continuous, "").strip()
        else:
            return text

    def splitFieldName(self, text, testId=0):
        """
        split Match Variable from fields
        INPUT:
            text {str}: It should be POP(DSC) POP; testId->1
        OUTPUT:
            list: [Training, rFType, Test]
         """
        textPart = text.split(" ")
        fieldTest = textPart[testId]
        fieldTraining = textPart[(not testId) * 1]
        if self.discrete in fieldTraining:
            return fieldTraining.replace(self.discrete, "").strip(), self.varTypeRev[self.discrete], fieldTest
        elif self.continuous in fieldTraining:
            return fieldTraining.replace(self.continuous, "").strip(), self.varTypeRev[self.continuous], fieldTest
        else:
            return text

    def setName(self, fieldName, typeRFField):
        if typeRFField in [True, 'true', self.discrete, self.varTypeRev[self.discrete]]:
            return '{0} {1}'.format(fieldName, self.discrete)
        elif typeRFField in [False, 'false', self.continuous, self.varTypeRev[self.continuous]]:
            return '{0} {1}'.format(fieldName, self.continuous)
        else:
            return None

    def populateField(self):
        if self.desc is not None:
            desc = self.desc  ##ARCPY.Describe(parin.value)
            try:
                self.fieldAlias = {field.aliasName: (field.name, field.type) for field in desc.fields}
                keys = list(self.fieldAlias.keys())
                for i in keys:
                    if self.fieldAlias[i][0] not in self.fieldAlias:
                        self.fieldAlias[self.fieldAlias[i][0]] = self.fieldAlias[i]
                self.fieldNames = {field.name: (field.aliasName, field.type) for field in desc.fields}
            except:
                self.fieldNames = None
                return

    def getFieldType(self, row):
        dat = ([self.fieldAlias[str(row[0].value)], False], False) \
            if row[1] in [None, False, "#"] \
            else ([self.fieldAlias[str(row[0].value)], row[1]], True)

        #### If Field is Set as Categorical ####
        if dat[1]:
            return dat[0]

        #### If Field is String Then It is Considered Categorical (True) Overwrite User ####
        row = dat[0]
        if self.fieldNames:
            if row[0][0] in self.fieldNames:
                fieldType = self.fieldNames[row[0][0]][1]
                if fieldType == "String":
                    return [row[0], True]
        return row

    def pv(self, value, id=None):
        from time import gmtime, strftime
        f = open(r"c:\temporal\tem.txt", "a")
        id = str(id)
        try:
            f.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " " + str(value) + " " + id + "\n")
        except:
            f.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "--\n")
            pass
        f.close()

    def checkRepeated(self, values, colId, initial=None):
        """
        Check Repeat elements in a parameter
        """
        try:

            if values:
                if "VALUE TABLE" in str(type(values)).upper() or \
                        "VALUETABLE" in str(type(values)).upper():
                    cols = values.columnCount
                    rows = values.rowCount
                    val = []
                    for r in range(rows):
                        val.append(values.getRow(r))
                    values = val

                listElem = []
                for ele in values:
                    if type(ele) == str:
                        listElem.append(ele)
                    elif type(ele) == list:
                        if type(ele[colId]) == str:
                            listElem.append(ele[colId])
                        else:
                            if "MappingLayerObject" in str(type(ele[colId])):
                                listElem.append(ele[colId].name)
                            else:
                                listElem.append(ele[colId].value)
                    else:
                        listElem.append(ele[colId].value)

                repeatedInitial = False
                if initial is not None:
                    repeatedInitial = listElem.count(str(initial)) >= 1
                    if repeatedInitial:
                        return None, str(initial)

                for ele in listElem:
                    if listElem.count(ele) > 1:
                        return ele, initial if repeatedInitial else None

                return None, initial if repeatedInitial else None
        except:
            pass

        return None, None

    def fcType(self, inputFC):
        try:
            self.desc = ARCPY.Describe(inputFC)
            if "Polygon" == self.desc.shapeType:
                self.isPolygon = True
            if "Point" == self.desc.shapeType:
                self.isPolygon = False
            self.populateField()
        except:
            pass

    def getDescribeF2P(self, inputFC):
        try:
            self.descF2P = ARCPY.Describe(inputFC)
            self.fieldAliasF2P = [field.aliasName for field in self.descF2P.fields]
            self.fieldNamesF2P = [field.name for field in self.descF2P.fields]
        except:
            pass

    def existInF2P(self, name):
        try:
            if name in self.fieldAliasF2P:
                return name
            if name in self.fieldNamesF2P:
                return name
        except:
            pass

        return None

    def replaceE(self, value, listR):
        for ele in listR:
            index = -1 * len(ele)
            info = value[index:]
            if value[index:] == ele:
                return value[:(index - 1)], info
        return value, ""

    def getValuesVT(self, parameter, infoList=None, removePart=[]):
        """ Get values from a value table parameter
        """
        info = parameter.valueAsText
        info = info.split(";")
        data = []

        if infoList is not None:
            try:
                for id, opt in enumerate(info):
                    part = []
                    count = sum(map(lambda x: 1 if "'" in x else 0, opt))
                    if count == 2:
                        part1 = opt.split("'")[1::2]
                        part2 = opt.replace(part1[0], "").replace("'", "").strip()
                        part = [part1[0], infoList[id]]
                    elif count == 4:
                        part = opt.split("'")[1::2]
                        part[1] = infoList[id]
                    else:
                        part = opt.split(" ")
                        part[1] = infoList[id]
                    data.append(part)
            finally:
                return data
            return data
        else:
            data2 = []
            try:
                for opt1 in info:
                    opt, infov = self.replaceE(opt1, removePart)
                    part = []

                    count = sum(map(lambda x: 1 if "'" in x else 0, opt))
                    if len(removePart) == 0:
                        count = sum(map(lambda x: 1 if "'" in x else 0, opt))

                    if count == 2:
                        part1 = opt.split("'")[1::2]
                        part2 = opt.replace(part1[0], "").replace("'", "").strip()
                        data.append(part1[0])

                        if not len(removePart):
                            data2.append(part2)
                        else:
                            data2.append(infov)

                    elif count == 4:
                        part = opt.split("'")[1::2]
                        data.append(part[0])
                        data2.append(part[1])

                    else:
                        part = opt.split(" ")
                        data.append(part[0])

                        if not len(removePart):
                            data2.append(part[1])
                        else:
                            data2.append(infov)

                return data, data2
            finally:
                return data, data2
            return data, data2
        return []

    def updateParameters(self, parameters):
        predictionType = parameters[0]
        inFeatures = parameters[1]
        variablePredict = parameters[2]
        treatVariableAsCategorical = parameters[3]
        explanatoryVariables = parameters[4]
        distanceFeatures = parameters[5]
        explanatoryRasters = parameters[6]
        featuresToPredict = parameters[7]
        outputFeatures = parameters[8]
        outputRaster = parameters[9]
        explanatoryVariableMatching = parameters[10]
        explanatoryDistanceMatching = parameters[11]
        explanatoryRastersMatching = parameters[12]
        outputTrainedFeatures = parameters[13]
        outputDiagnosticTable = parameters[14]
        useRasterValues = parameters[15]
        numberOfTrees = parameters[16]
        minimumLeafSize = parameters[17]
        maximumLevel = parameters[18]
        sampleSize = parameters[19]
        fieldsToTry = parameters[20]
        percentageForTraining = parameters[21]
        outputConfusionTable = parameters[22]
        outputCrossValidationTable = parameters[23]
        balanceTree = parameters[24]
        numberCrossValidationIterations = parameters[25]
        calculateUncertainty = parameters[26]

        if ARCPY.CheckExtension("spatial") != "Available":
            self.lic = False
            # explanatoryRasters.value  = None
            # explanatoryRastersMatching.value = None

        product = ARCPY.ProductInfo()
        if product in ["ArcView", "ArcEditor"]:
            self.near = False
            # distanceFeatures.value = None
            # explanatoryDistanceMatching.value = None

        if product == "ArcServer":
            #### 3D extension is used to verify that server used advance lic ####
            if ARCPY.CheckExtension("3D") == "Available":
                self.near = True
            else:
                self.near = False
                # distanceFeatures.value = None
                # explanatoryDistanceMatching.value = None

        if predictionType.value:
            if predictionType.value == "TRAIN":
                featuresToPredict.value = None
                explanatoryVariableMatching.value = None
                explanatoryRastersMatching.value = None
                explanatoryDistanceMatching.value = None
                outputFeatures.value = None
                outputRaster.value = None

                seePar = [4]
                hidePar = [7, 8, 9, 10, 11, 12]

                if self.lic:
                    seePar.append(6)
                else:
                    parameters[6].value = None
                    hidePar.append(6)

                if self.near:
                    seePar.append(5)
                else:
                    parameters[5].value = None
                    hidePar.append(5)

                enableParametersBy(parameters, seePar, hidePar)

            elif predictionType.value == "PREDICT_FEATURES":
                seePar = [4, 7, 8, 10]
                hidePar = [9]
                outputRaster.value = None

                if self.lic:
                    seePar.extend([6, 12])
                else:
                    hidePar.extend([6, 12])

                if self.near:
                    seePar.extend([5, 11])
                else:
                    hidePar.extend([5, 11])

                enableParametersBy(parameters, seePar, hidePar)

            elif predictionType.value == "PREDICT_RASTER":
                featuresToPredict.value = None
                outputFeatures.value = None
                enableParametersBy(parameters, [9, 10, 11, 12], [7, 8, 4, 5, 10, 11])
            else:
                return

        #### Get Information of Field Aliases of Input FC ####
        if inFeatures.enabled and inFeatures.altered:
            if inFeatures.value:
                self.fcType(inFeatures.value)

        #### Verify the Type of Field to Treat Tool as Class/Regr ####
        if variablePredict.altered:
            if self.desc is not None:
                try:
                    typeVar = [p.type for p in self.desc.fields if
                               p.name.upper() == variablePredict.value.value.upper()]
                    if len(typeVar):
                        if typeVar[0].upper() in ["TEXT", "STRING"]:
                            treatVariableAsCategorical.value = True
                except:
                    pass

        #### If Number of Trees is Zero - Just Train Option is Enable ####
        if numberOfTrees.value == 0:
            predictionType.filter.list = ["TRAIN"]
            predictionType.value = "TRAIN"
            calculateUncertainty.enabled = False
        else:
            calculateUncertainty.enabled = True
            if self.lic:
                predictionType.filter.list = ["TRAIN", "PREDICT_FEATURES", "PREDICT_RASTER"]
            else:
                predictionType.filter.list = ["TRAIN", "PREDICT_FEATURES"]

        #### Balance Trees is Just Applied in Classification ####
        if treatVariableAsCategorical.value:
            balanceTree.enabled = True
            outputConfusionTable.enabled = True
            calculateUncertainty.enabled = False
        else:
            balanceTree.enabled = False
            outputConfusionTable.enabled = False
            calculateUncertainty.enabled = True

        #### Disable Leaf/sample size/level if Balance is enabled ####
        if balanceTree.enabled:
            if balanceTree.value:
                enableParametersBy(parameters, [18], [17, 19])
            else:
                enableParametersBy(parameters, [17, 18, 19], [])
        else:
            enableParametersBy(parameters, [17, 18, 19], [])

        #### If Number of Trees is Zero - Just Train Option is Enable ####
        if numberOfTrees.value == 0:
            predictionType.filter.list = ["TRAIN"]
            predictionType.value = "TRAIN"
            enableParametersBy(parameters, [], [14, 17, 18, 19, 20, 21, 22, 24, 25, 26])
            numberCrossValidationIterations.value = 1
        else:
            predictionType.filter.list = ["TRAIN", "PREDICT_FEATURES", "PREDICT_RASTER"]
            visibleControls = None

            #### Hide Confusion Output Table ####
            if treatVariableAsCategorical.value:
                visibleControls = [14, 17, 18, 19, 20, 21, 22, 24, 25]
            else:
                visibleControls = [14, 17, 18, 19, 20, 21, 25, 26]
                parameters[24].value = False

            enableParametersBy(parameters, visibleControls, [])

            if balanceTree.value:
                enableParametersBy(parameters, [18], [17, 19])

        #### Percentage Training ####
        if percentageForTraining.value == 0:
            outputConfusionTable.enabled = False

        #### Output Cross Validation Table is Enabled When Iterations GT One ####
        if numberCrossValidationIterations.value:
            if int(numberCrossValidationIterations.value) > 1:
                outputCrossValidationTable.enabled = True
            else:
                outputCrossValidationTable.enabled = False

            if percentageForTraining.value == 0:
                outputCrossValidationTable.enabled = False

        #### Check Variables To Explode Polygon ####
        resolutionParameterShow = self.isPolygon and treatVariableAsCategorical.value and predictionType.value in [
            "TRAIN", "PREDICT_RASTER"]

        #### Check/Update Extension of Output Table Parameters ####
        tableCheck(outputDiagnosticTable)
        tableCheck(outputConfusionTable)
        tableCheck(outputCrossValidationTable)

        #### Update Explanatory Variables - Using Trick To Avoid Click By Default ####
        if predictionType.value in ["TRAIN", "PREDICT_FEATURES"]:

            if explanatoryVariables.value:
                v = []
                #### Fill Exp Variables - Checking Aliases ####
                try:
                    for i in explanatoryVariables.value:
                        if i[0].value not in [None, "#", ""]:
                            valueToInsert = self.getFieldType(i)
                            v.append([valueToInsert[0][0], valueToInsert[1]])
                except:
                    pass

                explanatoryVariables.value = v

            if featuresToPredict.altered:
                if featuresToPredict.value:
                    self.getDescribeF2P(featuresToPredict.value)

        if predictionType.value == "PREDICT_RASTER":
            explanatoryVariables.value = None
            distanceFeatures.value = None

        expRaster = None
        matchExpRaster = None

        if explanatoryRasters.altered:
            expRaster = explanatoryRasters.valueAsText
            matchExpRaster = explanatoryRastersMatching.valueAsText

        if predictionType.value == "PREDICT_FEATURES":
            if featuresToPredict.value:
                try:
                    if explanatoryVariables.value:
                        isFilled = False

                        explaVNames = []

                        for i in explanatoryVariables.value:
                            fieldName = None
                            fieldAlias = None
                            val = str(i[0].value)

                            if val in self.fieldNames:
                                fieldName = val
                                fieldAlias = self.fieldNames[val][0]
                                explaVNames.append((fieldName, fieldAlias))
                            elif val in self.fieldAlias:
                                fieldAlias = val
                                fieldName = self.fieldAlias[val][0]
                                explaVNames.append((fieldName, fieldAlias))

                        if explanatoryVariableMatching.value:
                            matchV = explanatoryVariableMatching.value
                            tEmptyToPredictFields = [i for i in matchV if i[0] is not None]
                            isFilled = len(tEmptyToPredictFields) == len(explaVNames)

                        if not isFilled:
                            explanatoryVariableMatching.value = [[self.existInF2P(i[0]), i[1]] for id, i in
                                                                 enumerate(explaVNames)]
                        else:
                            values = []
                            if len(explaVNames):
                                for id, i in enumerate(explaVNames):
                                    v = matchV[id]
                                    ex = self.existInF2P(v[0].value)
                                    values.append([ex, i[1]])
                                explanatoryVariableMatching.value = values

                except:
                    pass

        #### Clean Matching Variables ####
        if explanatoryVariables.value is None:
            explanatoryVariableMatching.value = None

        if expRaster in ["", None]:
            explanatoryRastersMatching.value = None
        if distanceFeatures.value is None:
            explanatoryDistanceMatching.value = None

        if predictionType.value in ["TRAIN", "PREDICT_FEATURES"]:
            if not distanceFeatures.hasBeenValidated or predictionType.altered:

                #### Get Current Distance Features ####
                if distanceFeatures.value:
                    distancesFCList = [pathDist.replace("'", "") for pathDist in \
                                       str(distanceFeatures.value).split(";")]
                    #### Create Var to Fill Match. Dist Param ####
                    matchD = [[pathDist, pathDist] for pathDist in distancesFCList]

                    if explanatoryDistanceMatching.values is None:
                        #### Update Match Dist Par ####
                        explanatoryDistanceMatching.values = matchD
                    else:
                        #### Get Current List Matching Feature ####
                        values = explanatoryDistanceMatching.values

                        if len(values) == len(distancesFCList):
                            #### Replace New Selection ####
                            explanatoryDistanceMatching.values = self.getValuesVT(explanatoryDistanceMatching,
                                                                                  distancesFCList)
                        else:
                            #### Update Using New List of Distance Features ###
                            matchD2 = matchD

                            if len(values) > 0:
                                #### Get List Per Colummn in Value Table ####
                                current2P, current2M = self.getValuesVT(explanatoryDistanceMatching)
                                matchD2 = []

                                #### Compare/Update With Previous Selection ####
                                for base in matchD:
                                    if base[0] in current2M:
                                        matchD2.append([current2P[current2M.index(base[0])], base[0]])
                                    else:
                                        matchD2.append([base[0], base[1]])

                            #### Replace Matching Parameter ####
                            explanatoryDistanceMatching.values = matchD2

                if distanceFeatures.value is None:
                    explanatoryDistanceMatching.value = None

            if distanceFeatures.value is None:
                explanatoryDistanceMatching.value = None

            if predictionType.value == "TRAIN":
                explanatoryDistanceMatching.value = None

        if predictionType.value in ["PREDICT_FEATURES", "PREDICT_RASTER"]:
            if explanatoryRasters.altered and not explanatoryRasters.hasBeenValidated or predictionType.altered:
                try:
                    matchR = None
                    if expRaster not in ["", None]:
                        #### Get Current List Of Rasters ####
                        valueRasters, cats = self.getValuesVT(explanatoryRasters, removePart=["#", "true", "false"])
                        #### Create Variable to Fill Match. Raster Param ####
                        matchR = [[pathR, pathR] for pathR in valueRasters]

                        if explanatoryRastersMatching.valueAsText in ["", None]:
                            #### Update Match Raster Par ####
                            explanatoryRastersMatching.values = matchR
                        else:
                            #### Get Current List Raster in the Match. Raster Parameter ####
                            values = explanatoryRastersMatching.valueAsText
                            values = values.split(";")

                            if len(values) == len(valueRasters):
                                #### Replace New Selection ####
                                explanatoryRastersMatching.values = self.getValuesVT(explanatoryRastersMatching,
                                                                                     valueRasters)
                            else:
                                #### Update Using New Raster List ###
                                matchR2 = matchR
                                if len(values) > 0:
                                    #### Get List Per Colummn in Value Table ####
                                    current2PR, current2MR = self.getValuesVT(explanatoryRastersMatching)
                                    matchR2 = []

                                    #### Compare/Update With Previous Selection ####
                                    for base in matchR:
                                        if base[0] in current2MR:
                                            matchR2.append([current2PR[current2MR.index(base[0])], base[0]])
                                        else:
                                            matchR2.append([base[0], base[1]])
                                #### Replace Match Raster Parameter ####
                                explanatoryRastersMatching.values = matchR2

                except:
                    pass

        if explanatoryVariables.value is None and distanceFeatures.value is None \
                and expRaster is not None and predictionType.value != "PREDICT_FEATURES" and self.isPolygon:
            enableParametersBy(parameters, [15], [])
            if not resolutionParameterShow:
                enableParametersBy(parameters, [], [15])

        else:
            enableParametersBy(parameters, [], [15])

        if outputRaster.value:
            path = str(outputRaster.value)
            if not UTILS.isGDB(path):
                outPath, outName = OS.path.split(path)
                if "." not in outName.upper():
                    outputRaster.value = str(outputRaster.value) + ".tif"
        pass

    def updateMessages(self, parameters):

        predictionType = parameters[0]
        inFeatures = parameters[1]
        variablePredict = parameters[2]
        treatVariableAsCategorical = parameters[3]
        explanatoryVariables = parameters[4]
        distanceFeatures = parameters[5]
        explanatoryRasters = parameters[6]
        featuresToPredict = parameters[7]
        outputFeatures = parameters[8]
        outputRaster = parameters[9]
        explanatoryVariableMatching = parameters[10]
        explanatoryDistanceMatching = parameters[11]
        explanatoryRastersMatching = parameters[12]
        outputTrainedFeatures = parameters[13]
        outputDiagnosticTable = parameters[14]
        useRasterValues = parameters[15]
        numberOfTrees = parameters[16]
        minimumLeafSize = parameters[17]
        maximumLevel = parameters[18]
        sampleSize = parameters[19]
        fieldsToTry = parameters[20]
        percentageForTraining = parameters[21]
        outputConfusionTable = parameters[22]
        outputCrossValidationTable = parameters[23]
        balanceTree = parameters[24]
        numberCrossValidationIterations = parameters[25]
        calculateUncertainty = parameters[26]

        if fieldsToTry.value:
            if fieldsToTry.value < 1:
                fieldsToTry.setIDMessage("ERROR", 30112, fieldsToTry.displayName)

        if maximumLevel.value:
            if maximumLevel.value < 1:
                maximumLevel.setIDMessage("ERROR", 30111, maximumLevel.displayName)

        if minimumLeafSize.value:
            if minimumLeafSize.value < 1:
                minimumLeafSize.setIDMessage("ERROR", 30112, minimumLeafSize.displayName)

        if explanatoryRasters.hasError():

            if "800" in str(explanatoryRasters.message):

                if explanatoryRasters.value:
                    for i in explanatoryRasters.value:
                        val = str(i[1]).upper()

                        if val in ["#", "NONE", "FALSE", "TRUE", "NUMERIC", "CATEGORICAL"]:
                            parameters[6].clearmessage()
                        else:
                            break

        if variablePredict.value is None:
            variablePredict.setIDMessage("ERROR", 530)

        if predictionType.value == "PREDICT_FEATURES":
            if featuresToPredict.value is None:
                featuresToPredict.setIDMessage("ERROR", 530)
            if outputFeatures.value is None:
                outputFeatures.setIDMessage("ERROR", 530)

        expRaster = None
        if predictionType.value == "PREDICT_RASTER":
            if outputRaster.value is None:
                outputRaster.setIDMessage("ERROR", 530)

        if predictionType.value in ["PREDICT_RASTER"]:
            expRaster = explanatoryRasters.value
            if expRaster is None:
                explanatoryRasters.setIDMessage("ERROR", 530)

        explVar = explanatoryVariables.value
        if explVar:
            repeatedInItself, compareOther = self.checkRepeated(explVar, 0, variablePredict.value)
            if compareOther is not None:
                explanatoryVariables.setIDMessage("ERROR", 110182, compareOther)

            repeatedInItself, compareOther = self.checkRepeated(explVar, 0)
            if repeatedInItself is not None:
                explanatoryVariables.setIDMessage("ERROR", 110182, repeatedInItself)

        if distanceFeatures.value:
            repeatedInItself, compareOther = self.checkRepeated(distanceFeatures.value, 0)
            if repeatedInItself is not None:
                distanceFeatures.setIDMessage("ERROR", 110182, repeatedInItself)

        if explanatoryRasters.altered:
            if expRaster:
                repeatedInItself, compareOther = self.checkRepeated(expRaster, 0)
                if repeatedInItself is not None:
                    explanatoryRasters.setIDMessage("ERROR", 110182, repeatedInItself)

        if percentageForTraining.value == 0:
            if numberCrossValidationIterations.value:
                if numberCrossValidationIterations.value > 1 and outputCrossValidationTable.enabled:
                    outputCrossValidationTable.setIDMessage("ERROR", 530)

        return

    def execute(self, parameters, messages):
        import SSForest as FOREST
        import imp
        imp.reload(FOREST)
        infoR = FOREST.execute(self, parameters)
        if infoR is not None:
            ARCPY.SetParameter(27, infoR)


class LocalBivariateRelationships(object):
    def __init__(self):
        self.label = "Local Bivariate Relationships"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Modeling Spatial Relationships"
        self.helpContext = 9060009
        self.shapeType = None

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ['Point', 'Polygon']
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Dependent Variable",
                                 name="dependent_variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.list = ['Short', 'Long', 'Float', 'Double']
        param1.parameterDependencies = ["in_features"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Explanatory Variable",
                                 name="explanatory_variable",
                                 datatype="Field",
                                 parameterType="Required",
                                 direction="Input")
        param2.filter.list = ['Short', 'Long', 'Float', 'Double']
        param2.parameterDependencies = ["in_features"]
        param2.displayOrder = 2

        param3 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")
        param3.displayOrder = 5

        param4 = ARCPY.Parameter(displayName="Number of Neighbors",
                                 name="number_of_neighbors",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.type = "Range"
        param4.value = 30
        param4.filter.list = [30, 1000]
        param4.displayOrder = 3

        param5 = ARCPY.Parameter(displayName="Number of Permutations",
                                 name="number_of_permutations",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")
        param5.filter.list = [99, 199, 499, 999]
        param5.value = 199
        param5.displayOrder = 4

        param6 = ARCPY.Parameter(displayName="Enable Local Scatterplot Pop-ups",
                                 name="enable_local_scatterplot_popups",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.list = ['CREATE_POPUP', 'NO_POPUP']
        param6.value = True
        param6.displayOrder = 6

        param7 = ARCPY.Parameter(displayName="Level of Confidence",
                                 name="level_of_confidence",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ["90%", "95%", "99%"]
        param7.value = "90%"
        param7.displayOrder = 7

        param8 = ARCPY.Parameter(displayName="Apply False Discovery Rate (FDR) Correction",
                                 name="apply_false_discovery_rate_fdr_correction",
                                 datatype="GPBoolean",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ['APPLY_FDR', 'NO_FDR']
        param8.value = True
        param8.category = "Advanced Options"
        param8.displayOrder = 8

        param9 = ARCPY.Parameter(displayName="Scaling Factor (Alpha)",
                                 name="scaling_factor",
                                 datatype="GPDouble",
                                 parameterType="Optional",
                                 direction="Input")
        param9.filter.type = "Range"
        param9.filter.list = [0.01, 1]
        param9.value = 0.5
        param9.category = "Advanced Options"
        param9.displayOrder = 9

        return [param0, param1, param2, param3, param4, param5, param6, param7, param8,
                param9]

    def updateParameters(self, parameters):

        desc = None
        self.fieldObjects = {}
        outParam = parameters[3]
        if parameters[0].altered:
            try:
                desc = ARCPY.Describe(parameters[0].value)
                for field in desc.fields:
                    self.fieldObjects[field.name] = field
                shapeType = desc.ShapeType.upper()
                outLYR = ""
                if shapeType == "POINT":
                    outLYR = "BivariateDependence_Points.lyrx"
                if shapeType == "POLYGON":
                    outLYR = "BivariateDependence_Polygons.lyrx"
                outParam.symbology = OS.path.join(pathLayers, outLYR)
            except:
                pass

        #### Analysis Fields ####
        addFields = []

        if outParam.value:
            outPath, outName = OS.path.split(outParam.valueAsText)
            if ARCPY.Exists(outPath):
                if parameters[1].value and parameters[2].value:
                    fieldNames = [parameters[1].valueAsText, parameters[2].valueAsText]
                    fields = [self.fieldObjects[i] for i in fieldNames if i in self.fieldObjects]
                    validNames = UTILS.createAppendFieldNames(fieldNames, outPath)
                    for ind, field in enumerate(fields):
                        try:
                            newField = createField(validNames[ind], outPath, field.type,
                                                   field.aliasName)
                            addFields.append(newField)
                        except:
                            pass

        #### Result Fields ####
        fieldNames = ["ENTROPY", "PVALUES", "LBR_SIG",
                      "INTERCEPT", "COEF_1",
                      "PINTERCEPT",
                      "P_COEF_1", "P_COEF_2",
                      "AICC", "R2", "P_AICc", "P_R2",
                      "SIG_COEF", "P_SIG_COEF",
                      "LBR_TYPE"]
        fieldTypes = ["DOUBLE", "DOUBLE", "TEXT",
                      "DOUBLE", "DOUBLE",
                      "DOUBLE",
                      "DOUBLE", "DOUBLE",
                      "DOUBLE", "DOUBLE", "DOUBLE", "DOUBLE",
                      "TEXT", "TEXT",
                      "TEXT"]
        fieldAliasNames = ["Entropy", "p-values", "Local Bivariate Relationship Confidence Level",
                           "Intercept", "Coefficient (Linear)",
                           "Polynomial Intercept",
                           "Polynomial Coefficient (Linear)", "Polynomial Coefficient (Squared)",
                           "AICc (Linear)", "r-squared (Linear)", "AICc (Polynomial)", "r-squared (Polynomial)",
                           "Significance of Coefficients (Linear)", "Significance of Coefficients (Polynomial)",
                           "Type of Relationship"]

        fieldLengths = [30, 3, 3, 30]
        lengthCount = 0

        for fieldInd, fieldName in enumerate(fieldNames):
            newField = ARCPY.Field()
            newField.name = fieldName
            fieldType = fieldTypes[fieldInd]
            newField.type = fieldType
            newField.aliasName = fieldAliasNames[fieldInd]
            if fieldType == "TEXT":
                newField.length = fieldLengths[lengthCount]
                lengthCount += 1
            addFields.append(newField)
        outParam.schema.additionalFields = addFields

        return

    def updateMessages(self, parameters):
        depVarParam = parameters[1]
        indVarParam = parameters[2]
        #### Make Sure the Explanatory Variable and Dependent Variable are different ####
        if depVarParam.value and indVarParam.value:
            if depVarParam.valueAsText == indVarParam.valueAsText:
                indVarParam.setIDMessage("ERROR", 110266)

        #### Manual Check for GPString Parameter Due to % in Value List ####
        confParam = parameters[7]
        if confParam.value:
            if confParam.value not in ["90%", "95%", "99%"]:
                confParam.setIDMessage("ERROR", 800, "90% | 95% | 99%")

        #### Warning Message for Local Scatterplots When Written to Shapefile ####
        outParam = parameters[3]
        scatParam = parameters[6]
        if outParam.value:
            outPath, outName = OS.path.split(outParam.valueAsText)
            if not ARCPY.Exists(outPath):
                outParam.setIDMessage("ERROR", 210, outParam.value.value)
        if scatParam.value and outParam.value:
            if UTILS.isShapeFile(outParam.valueAsText):
                scatParam.setIDMessage("WARNING", 110277)

        return

    def execute(self, parameters, messages):
        import SSUtilities as UTILS
        import SSDataObject as SSDO
        import BivariateDependence as BD

        ### Get parameter values ####
        ARCPY.env.overwriteOutput = True
        inputFC = UTILS.getTextParameter(0, parameters)
        depVarName = UTILS.getTextParameter(1, parameters).upper()
        indVarName = UTILS.getTextParameter(2, parameters).upper()
        outputFC = UTILS.getTextParameter(3, parameters)

        numNeighs = UTILS.getNumericParameter(4, parameters)
        if numNeighs is None:
            numNeighs = 30

        permutations = UTILS.getNumericParameter(5, parameters)
        if permutations is None:
            permutations = 199

        createPopUps = parameters[6].value

        significance = UTILS.getTextParameter(7, parameters)
        if significance is None:
            significance = "90%"

        applyFDR = parameters[8].value

        alpha = UTILS.getNumericParameter(9, parameters)
        if alpha is None:
            alpha = 0.5

        #### Create SSDataObject ####
        ssdo = SSDO.SSDataObject(inputFC, templateFC=outputFC)
        allVars = [depVarName, indVarName]
        ssdo.obtainData(ssdo.oidName, allVars, minNumObs=31)

        #### Make Sure the Total Number of Features is Larger than 20 ####
        if ssdo.numObs < 20:
            ARCPY.AddIDMessage("Error", 641, 20)
            raise SystemExit()
        #### Make Sure the Number of Neighbors is less Than the Total Number of Features ####
        if ssdo.numObs <= numNeighs:
            ARCPY.AddIDMessage("Error", 110265)
            raise SystemExit()

        #### Analysis ####
        bd = BD.ScanDependence(ssdo, depVarName, indVarName, alpha=alpha,
                               numNeighs=numNeighs, permutations=permutations,
                               significance=significance, solveType="MINIMUM_SPANNING_TREE",
                               createPopUps=createPopUps, applyFDR=applyFDR)

        #### Report ####
        bd.getReport()

        #### Create Output ####
        bd.createOutput(outputFC, applyFDR=applyFDR)

        #### Runtime Render Commands ####
        renderLayerFile = ""
        shapeType = ssdo.shapeType.upper()
        if shapeType == "POINT":
            renderLayerFile = "BivariateDependence_Points.lyrx"
        if shapeType == "POLYGON":
            renderLayerFile = "BivariateDependence_Polygons.lyrx"
        try:
            templateDir = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates", "Layers")
            fullRLF = OS.path.join(templateDir, renderLayerFile)
            parameters[3].symbology = fullRLF
        except:
            ARCPY.AddIDMessage("WARNING", 973)


class BuildBalancedZones(object):
    def __init__(self):
        self.label = "Build Balanced Zones"
        self.description = ""
        self.canRunInBackground = False
        self.category = "Mapping Clusters"
        self.helpContext = 9030011

        self.allSpaceTypes = ["CONTIGUITY_EDGES_ONLY",
                              "CONTIGUITY_EDGES_CORNERS",
                              "TRIMMED_DELAUNAY_TRIANGULATION",
                              "GET_SPATIAL_WEIGHTS_FROM_FILE"]
        self.pointSpaceTypes = ["TRIMMED_DELAUNAY_TRIANGULATION",
                                "GET_SPATIAL_WEIGHTS_FROM_FILE"]
        self.constPoly = ["EQUAL_AREA", "COMPACTNESS", "EQUAL_NUMBER_OF_FEATURES"]
        self.constPoint = ["COMPACTNESS", "EQUAL_NUMBER_OF_FEATURES"]
        self.onlyCompact = ["COMPACTNESS"]
        self.constPolyArea = ["EQUAL_AREA", "COMPACTNESS"]
        self.idMsg = ARCPY.GetIDMessage(84903)

    def getParameterInfo(self):

        param0 = ARCPY.Parameter(displayName="Input Features",
                                 name="in_features",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ['Point', 'Polygon']

        param1 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output")

        param2 = ARCPY.Parameter(displayName="Zone Creation Method",
                                 name="zone_creation_method",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param2.filter.list = ["ATTRIBUTE_TARGET", "NUMBER_ZONES_AND_ATTRIBUTE", "NUMBER_OF_ZONES"]
        param2.value = "ATTRIBUTE_TARGET"

        param3 = ARCPY.Parameter(displayName="Target Number of Zones",
                                 name="number_of_zones",
                                 datatype="GPLong",
                                 parameterType="Optional",
                                 direction="Input")

        param4 = ARCPY.Parameter(displayName="Zone Building Criteria With Target",
                                 name="zone_building_criteria_target",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")
        param4.controlCLSID = "{1AA9A769-D3F3-4EB0-85CB-CC07C79313C8}"
        param4.parameterDependencies = [param0.name]
        param4.columns = [['Field', 'Variable'], ['GPString', 'Sum'], ['GPDouble', 'Weight']]
        param4.filters[0].list = ["Double", "Float", "Short", "Long"]

        param5 = ARCPY.Parameter(displayName="Zone Building Criteria",
                                 name="zone_building_criteria",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")

        param5.parameterDependencies = [param0.name]
        param5.columns = [['Field', 'Variable'], ['GPDouble', 'Weight']]
        param5.filters[0].list = ["Double", "Float", "Short", "Long"]

        param6 = ARCPY.Parameter(displayName="Spatial Constraints",
                                 name="spatial_constraints",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.type = "ValueList"
        param6.filter.list = ['CONTIGUITY_EDGES_ONLY', 'CONTIGUITY_EDGES_CORNERS',
                              'TRIMMED_DELAUNAY_TRIANGULATION', 'GET_SPATIAL_WEIGHTS_FROM_FILE']
        # param6.value = 'TRIMMED_DELAUNAY_TRIANGULATION'

        param7 = ARCPY.Parameter(displayName="Spatial Weight Matrix File",
                                 name="weights_matrix_file",
                                 datatype="DEFile",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ['swm', 'gwt']

        param8 = ARCPY.Parameter(displayName="Zone Characteristics",
                                 name="zone_characteristics",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input",
                                 multiValue=True)
        param8.filter.list = ["EQUAL_AREA", "COMPACTNESS", "EQUAL_NUMBER_OF_FEATURES"]
        param8.category = "Additional Zone Selection Criteria"

        param9 = ARCPY.Parameter(displayName="Attribute to Consider",
                                 name="attribute_to_consider",
                                 datatype="GPValueTable",
                                 parameterType="Optional",
                                 direction="Input")

        param9.parameterDependencies = [param0.name]
        param9.columns = [['Field', 'Variable'], ['GPString', 'Function']]
        param9.filters[0].list = ["Double", "Float", "Short", "Long"]
        param9.filters[1].list = ["SUM", "AVERAGE", "VARIANCE", "MEDIAN"]
        param9.category = "Additional Zone Selection Criteria"

        param10 = ARCPY.Parameter(displayName="Distance to Consider",
                                  name="distance_to_consider",
                                  datatype="GPFeatureLayer",
                                  parameterType="Optional",
                                  multiValue=True,
                                  direction="Input")
        param10.category = "Additional Zone Selection Criteria"

        product = ARCPY.ProductInfo()
        if product in ["ArcView", "ArcEditor"]:
            param10.enabled = False

        if product == "ArcServer":
            if ARCPY.CheckExtension("3D") == "Available":
                param10.enabled = True
            else:
                param10.enabled = False

        param11 = ARCPY.Parameter(displayName="Categorical Variable to Maintain Proportions",
                                  name="categorial_variable",
                                  datatype="Field",
                                  parameterType="Optional",
                                  direction="Input")
        param11.parameterDependencies = [param0.name]
        param11.filter.list = ["Integer", "Short", "Text", "Double", "Float"]
        param11.category = "Additional Zone Selection Criteria"

        param12 = ARCPY.Parameter(displayName="Proportion Method",
                                  name="proportion_method",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")
        param12.filter.list = ['MAINTAIN_WITHIN_PROPORTION', 'MAINTAIN_OVERALL_PROPORTION']
        param12.filter.type = "ValueList"
        param12.category = "Additional Zone Selection Criteria"
        param12.enabled = False

        param13 = ARCPY.Parameter(displayName="Population Size",
                                  name="population_size",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")

        param13.filter.type = "Range"
        param13.value = 100
        param13.filter.list = [3, 10000000]
        param13.category = "Advanced Parameters"

        param14 = ARCPY.Parameter(displayName="Number of Generations",
                                  name="number_generations",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")

        param14.filter.type = "Range"
        param14.value = 50
        param14.filter.list = [1, 10000000]
        param14.category = "Advanced Parameters"

        param15 = ARCPY.Parameter(displayName="Mutation Factor",
                                  name="mutation_factor",
                                  datatype="GPDouble",
                                  parameterType="Optional",
                                  direction="Input")

        param15.filter.type = "Range"
        param15.value = 0.1
        param15.filter.list = [0.0, 1.0]
        param15.category = "Advanced Parameters"

        param16 = ARCPY.Parameter(displayName="Output Convergence Table",
                                  name="output_convergence_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")

        param16.category = "Advanced Parameters"

        return [param0, param1, param2, param3,
                param4, param5, param6, param7,
                param8, param9, param10, param11,
                param12, param13, param14, param15,
                param16]

    def isLicensed(self):
        return True

    def _getWeights(self, valuesVar, indexPosWeight=2):
        """ Get Weight from Value Table """

        values = []
        weights = []
        names = set()
        for value in valuesVar.value:
            record = value
            weight = record[indexPosWeight]
            names.add(record[0].value)

            if weight in [0, None]:
                weight = 1

            weight1 = None

            try:
                weight1 = UTILS.strToFloat(weight)
            except:
                weight1 = weight

            weights.append(weight1)

        return weights, True if len(weights) == len(names) else False

    def _weights(self, numZonePar, variablesPar, par=False):
        """ Update Sum/Weight """

        if par and numZonePar.value is None or numZonePar.value == 0:
            valuesVar = variablesPar.valueAsText
            weights, eqNam = self._getWeights(variablesPar, 1)
            values = []
            for id, value in enumerate(variablesPar.value):
                record = value
                values.append([record[0].value, weights[id]])
            variablesPar.value = values
            return

        if numZonePar.value:
            if variablesPar.value:
                valuesVar = variablesPar.valueAsText
                weights, eqNam = self._getWeights(variablesPar, 1)
                values = []
                for id, value in enumerate(variablesPar.value):
                    record = value
                    values.append([record[0].value, weights[id]])
                variablesPar.value = values
        elif variablesPar.value:
            valuesVar = variablesPar.valueAsText
            weights, eqNam = self._getWeights(variablesPar, 2)
            values = []

            for id, value in enumerate(variablesPar.value):
                record = value
                variableName = record[0].value
                valuef = record[1]
                valuef = "" if valuef in ["#", None, ""] else valuef
                values.append([variableName, valuef, weights[id]])

            if len(values):
                variablesPar.value = values

    def _isDuplicatedVar(self, valuesVar, checkInput=None):
        """ Get Weight from Value Table """

        nameInput = ""
        if checkInput is not None:
            try:
                info = ARCPY.Describe(checkInput)
                nameInput = info.catalogPath
            except:
                nameInput = ""

        n = len(valuesVar.split(";"))
        names = set()
        for value in valuesVar.split(";"):
            if checkInput is None:
                record = value.split(" ")
                names.add(record[0])
            else:
                try:
                    info = ARCPY.Describe(value)
                    names.add(info.catalogPath)
                    if info.catalogPath == nameInput:
                        return False
                except:
                    names.add(value)

        return True if n == len(names) else False

    def _setList(self, zoneCharacteristics, newList):
        currentValuesStr = zoneCharacteristics.valueAsText
        if currentValuesStr not in [None, "", "#"]:
            da = currentValuesStr.split(";")
            values = []
            for val in da:
                if val in self.constPoly and val in newList:
                    values.append(val)
            zoneCharacteristics.filter.list = newList
            zoneCharacteristics.value = values
        else:
            zoneCharacteristics.filter.list = newList

    def updateParameters(self, parameters):
        """ Update Parameters"""
        inFeatures = parameters[0]
        outputFeatures = parameters[1]
        zoneCreationMethod = parameters[2]
        numberOfZones = parameters[3]
        zoneBuildingCriteriaTarget = parameters[4]
        zoneBuildingCriteria = parameters[5]
        spatialConstraints = parameters[6]
        weightsMatrixFile = parameters[7]
        zoneCharacteristics = parameters[8]
        attributeToConsider = parameters[9]
        distanceToConsider = parameters[10]
        categorialVariable = parameters[11]
        proportionMethod = parameters[12]
        populationSize = parameters[13]
        numberGenerations = parameters[14]
        mutationFactor = parameters[15]
        outputConvergenceTable = parameters[16]

        if categorialVariable.value:
            proportionMethod.enabled = True
        else:
            proportionMethod.enabled = False
            proportionMethod.value = None

        if spatialConstraints.valueAsText != "GET_SPATIAL_WEIGHTS_FROM_FILE":
            weightsMatrixFile.value = None

        if zoneCreationMethod.value == "ATTRIBUTE_TARGET":
            numberOfZones.enabled = False
            numberOfZones.value = None
            zoneBuildingCriteriaTarget.enabled = True
            zoneBuildingCriteria.enabled = False
            zoneBuildingCriteria.value = None
            numberOfZones.value = None

            if zoneBuildingCriteriaTarget.value is not None:
                self._weights(numberOfZones, zoneBuildingCriteriaTarget)

        elif zoneCreationMethod.value == "NUMBER_ZONES_AND_ATTRIBUTE":
            numberOfZones.enabled = True
            zoneBuildingCriteria.enabled = True
            zoneBuildingCriteriaTarget.enabled = False
            zoneBuildingCriteriaTarget.value = None

            if zoneBuildingCriteria.value is not None:
                self._weights(numberOfZones, zoneBuildingCriteria, True)

        elif zoneCreationMethod.value == "NUMBER_OF_ZONES":
            numberOfZones.enabled = True
            zoneBuildingCriteria.enabled = False
            zoneBuildingCriteriaTarget.enabled = False
            zoneBuildingCriteria.value = None
            zoneBuildingCriteriaTarget.value = None

        desc = None
        shapeType = ""
        try:
            desc = ARCPY.Describe(inFeatures.value)
            shapeType = desc.shapeType.upper()
        except:
            desc = None

        if not spatialConstraints.altered:
            if shapeType.upper() == "POLYGON":
                spatialConstraints.value = "CONTIGUITY_EDGES_CORNERS"
            if shapeType.upper() == "POINT":
                spatialConstraints.value = "TRIMMED_DELAUNAY_TRIANGULATION"

        if shapeType.upper() == "POINT":
            spatialConstraints.filter.list = self.pointSpaceTypes

            if zoneCreationMethod.value == "NUMBER_ZONES_AND_ATTRIBUTE":
                zoneCharacteristics.filter.list = self.constPoint

            if zoneCreationMethod.value == "NUMBER_OF_ZONES":
                self._setList(zoneCharacteristics, self.onlyCompact)
                # zoneCharacteristics.filter.list = self.onlyCompact

            if zoneCreationMethod.value == "ATTRIBUTE_TARGET":
                self._setList(zoneCharacteristics, self.constPoint)
                # zoneCharacteristics.filter.list  = self.constPoint

        if shapeType.upper() == "POLYGON":
            spatialConstraints.filter.list = self.allSpaceTypes

            if zoneCreationMethod.value == "NUMBER_ZONES_AND_ATTRIBUTE":
                zoneCharacteristics.filter.list = self.constPoly

            if zoneCreationMethod.value == "NUMBER_OF_ZONES":
                zoneCharacteristics.filter.list = self.constPolyArea

            if zoneCreationMethod.value == "ATTRIBUTE_TARGET":
                zoneCharacteristics.filter.list = self.constPoly

        #### SWM File ####
        if spatialConstraints.value == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            weightsMatrixFile.enabled = True
        else:
            weightsMatrixFile.enabled = False

        return

    def updateMessages(self, parameters):
        """ Update Messages """
        inFeatures = parameters[0]
        outputFeatures = parameters[1]
        zoneCreationMethod = parameters[2]
        numberOfZones = parameters[3]
        zoneBuildingCriteriaTarget = parameters[4]
        zoneBuildingCriteria = parameters[5]
        spatialConstraints = parameters[6]
        weightsMatrixFile = parameters[7]
        zoneCharacteristics = parameters[8]
        attributeToConsider = parameters[9]
        distanceToConsider = parameters[10]
        categorialVariable = parameters[11]
        proportionMethod = parameters[12]
        populationSize = parameters[13]
        numberGenerations = parameters[14]
        mutationFactor = parameters[15]
        outputConvergenceTable = parameters[16]

        if numberOfZones.value is not None or numberOfZones.value == 0:
            if numberOfZones.value < 2:
                numberOfZones.setIDMessage("ERROR", 110267)

        if zoneCreationMethod.value == "ATTRIBUTE_TARGET":
            if zoneBuildingCriteriaTarget.value is None:
                zoneBuildingCriteriaTarget.setIDMessage("ERROR", 530)
            else:
                weights, eqNam = self._getWeights(zoneBuildingCriteriaTarget)

                if not eqNam:
                    zoneBuildingCriteriaTarget.setIDMessage("ERROR", 400)

                for id, value in enumerate(zoneBuildingCriteriaTarget.value):
                    record = value
                    variableName = record[0].value
                    value2 = record[1]
                    weight = record[2]

                    try:
                        value2 = UTILS.strToFloat(value2.strip())
                    except:
                        if value2 in ["", "#", None]:
                            zoneBuildingCriteriaTarget.setIDMessage("ERROR", 530)
                        else:
                            zoneBuildingCriteriaTarget.setIDMessage("ERROR", 891)
                        continue
                    #### Check Weight Value ####
                    check = True
                    try:
                        weight = UTILS.strToFloat(weight)
                    except:
                        if weight in ["", "#", None]:
                            zoneBuildingCriteriaTarget.setIDMessage("ERROR", 530)
                        else:
                            zoneBuildingCriteriaTarget.setIDMessage("ERROR", 891)
                        check = False

                    if check and weight <= 0:
                        zoneBuildingCriteriaTarget.setIDMessage("ERROR", 531)

                    continue


        elif zoneCreationMethod.value == "NUMBER_ZONES_AND_ATTRIBUTE":
            if numberOfZones.value is None or zoneBuildingCriteria.value is None:
                if numberOfZones.value is None:
                    numberOfZones.setIDMessage("ERROR", 530)
                if zoneBuildingCriteria.value is None:
                    zoneBuildingCriteria.setIDMessage("ERROR", 530)

            elif numberOfZones.value is not None and zoneBuildingCriteria.value is not None:
                weights, eqNam = self._getWeights(zoneBuildingCriteria, 1)

                if not eqNam:
                    zoneBuildingCriteria.setIDMessage("ERROR", 400)

                for id, value in enumerate(zoneBuildingCriteria.value):
                    variableName = value[0].value
                    weight = value[1]

                    check = True
                    try:
                        weight = UTILS.strToFloat(weight)
                    except:
                        if weight in ["", "#", None]:
                            zoneBuildingCriteria.setIDMessage("ERROR", 530)
                        else:
                            zoneBuildingCriteria.setIDMessage("ERROR", 891)
                        check = False

                    if check and weight <= 0:
                        zoneBuildingCriteria.setIDMessage("ERROR", 531)

                    continue


        elif zoneCreationMethod.value == "NUMBER_OF_ZONES":
            if numberOfZones.value is None:
                numberOfZones.setIDMessage("ERROR", 530)

        if attributeToConsider.value:
            if not self._isDuplicatedVar(attributeToConsider.valueAsText):
                attributeToConsider.setIDMessage("ERROR", 400)

        if distanceToConsider.value:
            value = None
            if inFeatures.value:
                value = inFeatures.valueAsText

            if not self._isDuplicatedVar(distanceToConsider.valueAsText, value):
                distanceToConsider.setIDMessage("ERROR", 400)

        if categorialVariable.value:
            if proportionMethod.value is None:
                proportionMethod.setIDMessage("ERROR", 530)

        if outputFeatures.value and outputConvergenceTable.value:
            if outputFeatures.valueAsText.upper() == outputConvergenceTable.valueAsText.upper():
                outPath, outName = OS.path.split(outputFeatures.valueAsText)
                outputConvergenceTable.setIDMessage("ERROR", 110275, outName)

        if spatialConstraints.value:
            if spatialConstraints.valueAsText == "GET_SPATIAL_WEIGHTS_FROM_FILE":
                if weightsMatrixFile.value is None:
                    weightsMatrixFile.setIDMessage("ERROR", 530)

        return

    def execute(self, parameters, messages):
        #### User Defined Inputs ####

        inFeatures = parameters[0].valueAsText
        outputFeatures = parameters[1].valueAsText
        zoneCreationMethod = parameters[2].valueAsText
        numberOfZones = UTILS.getNumericParameter(3, parameters)
        zoneBuildingCriteriaTarget = parameters[4].value
        zoneBuildingCriteria = parameters[5].valueAsText
        spatialConstraints = parameters[6].valueAsText
        weightsMatrixFile = parameters[7].valueAsText
        zoneCharacteristics = parameters[8].valueAsText
        attributeToConsider = parameters[9].valueAsText
        distanceToConsider = parameters[10].valueAsText
        categorialVariable = parameters[11].valueAsText
        proportionMethod = parameters[12].value
        populationSize = UTILS.getNumericParameter(13, parameters)
        numberGenerations = UTILS.getNumericParameter(14, parameters)
        mutationFactor = UTILS.getNumericParameter(15, parameters)
        outputConvergenceTable = parameters[16]

        fieldConstraints = None
        if zoneCreationMethod == "ATTRIBUTE_TARGET":
            numRegions = None
            fieldConstraints = zoneBuildingCriteriaTarget
        else:
            fieldConstraints = zoneBuildingCriteria
            numRegions = numberOfZones

        if numRegions in [None, ""]:
            numRegions = None

        constraints = None
        costValues = None
        if fieldConstraints is not None:
            if type(fieldConstraints) == list:
                try:
                    constraints = []
                    for i in fieldConstraints:
                        constraints.append("{0} {1} {2}".format(str(i[0].value), i[1].strip(), i[2]))
                except:
                    constraints = parameters[4].valueAsText.split(";")
            else:
                constraints = fieldConstraints.split(";")

            constraintsClean = []
            weights = []
            varNames = []
            for e in constraints:
                elems = e.split(" ")

                if len(elems) == 3:
                    strItem = ""
                    varNames.append(elems[0])
                    strItem = "{0} >= {1}".format(elems[0], UTILS.strToFloat(elems[1].strip()))
                    constraintsClean.append(strItem)
                    weights.append(UTILS.strToFloat(elems[2]))
                else:
                    strItem = ""
                    varNames.append(elems[0])
                    strItem = "{0} >= {1}".format(elems[0], -1)
                    constraintsClean.append(strItem)
                    weights.append(UTILS.strToFloat(elems[1]))

            constraints = constraintsClean
            costValuesNum = SSDO.NUM.array(weights, dtype=float)
            total = costValuesNum.sum()
            costValuesReCal = costValuesNum / total
            #### Create Dictionary with Name Field - Calculated Weight ####
            costValues = {w.upper(): costValuesReCal[id] for id, w in enumerate(varNames)}

        import SSOptimal as OPT
        import numpy as NUM
        import imp

        imp.reload(OPT)
        ssdo = SSDO.SSDataObject(inFeatures)

        globalGen = OPT.GlobalGeneratorBase(ssdo, constraints,
                                            sizePopulation=populationSize,
                                            mutationFactor=mutationFactor,
                                            outputFC=outputFeatures,
                                            parameterOutput=parameters[1],
                                            otherConstraints=zoneCharacteristics,
                                            spatialConcept=spatialConstraints,
                                            weightsFile=weightsMatrixFile,
                                            costValues=costValues,
                                            applyFunction=attributeToConsider,
                                            proportionField=categorialVariable,
                                            conserveProportion=proportionMethod == 'MAINTAIN_WITHIN_PROPORTION',
                                            numRegions=numRegions,
                                            numGenerations=numberGenerations,
                                            distanceFeatures=distanceToConsider)
        info = globalGen.getSolution()

        if info is None:
            return

        fitness, maxFitness = info

        outputFitTable = None
        generationData = None

        if outputConvergenceTable.value:
            outputFitTable = outputConvergenceTable.valueAsText
            generationData = NUM.arange(globalGen.numGenerations + 1, dtype=NUM.int32)

        if outputFitTable is not None:
            cont = UTILS.DataContainer()
            fieldGeneration = SSDO.CandidateField(name="GENERATION",
                                                  alias=ARCPY.GetIDMessage(84917),
                                                  type="LONG",
                                                  data=generationData)
            yFields = [f.name for f in fitness]
            fitness.append(fieldGeneration)

            cont.generateOutput(outputFitTable, fitness)

            chart = ARCPY.Chart(ARCPY.GetIDMessage(84916))
            chart.type = "line"
            chart.title = ARCPY.GetIDMessage(84916)

            #### Assign Y Axis Field ####
            chart.yAxis.field = yFields
            chart.yAxis.title = ARCPY.GetIDMessage(84918)

            #### Assign X Axis Field ####
            chart.xAxis.field = "GENERATION"
            chart.xAxis.title = ARCPY.GetIDMessage(84917)
            chart.legend.visible = True
            chart.xAxis.minimum = 0
            chart.xAxis.maximum = numberGenerations
            chart.yAxis.minimum = 0
            chart.yAxis.maximum = maxFitness

            outputConvergenceTable.charts = [chart]


class ColocationAnalysis(object):
    def __init__(self):
        self.label = "Colocation Analysis"
        self.decription = "Calculate local Colocation Quotient Wang et al 2016"
        self.category = "Modeling Spatial Relationships"
        self.canRunInBackground = False
        self.helpContext = 9060010
        self.ssdoTarget = None
        self.ssdoSource = None
        self.listTarget = []
        self.listSource = []

    def getParameterInfo(self):
        """Define parameter definitions"""
        #### Local Imports ####
        import os as OS
        import sys as SYS

        templateDir = OS.path.join(OS.path.dirname(SYS.path[0]), "Templates", "Layers")
        fullRLF = OS.path.join(templateDir, "LocalColocationQuotient.lyrx")

        param0 = ARCPY.Parameter(displayName="Input Type",
                                 name="input_type",
                                 datatype="GPString",
                                 parameterType="Required",
                                 direction="Input")
        param0.filter.list = ["SINGLE_DATASET", "DATASETS_WITHOUT_CATEGORIES", "TWO_DATASETS"]
        param0.value = "SINGLE_DATASET"
        param0.displayOrder = 0

        param1 = ARCPY.Parameter(displayName="Input Features of Interest",
                                 name="in_features_of_interest",
                                 datatype="GPFeatureLayer",
                                 parameterType="Required",
                                 direction="Input")
        param1.filter.list = ["Point"]
        param1.displayOrder = 1

        param2 = ARCPY.Parameter(displayName="Output Features",
                                 name="output_features",
                                 datatype="DEFeatureClass",
                                 parameterType="Required",
                                 direction="Output",
                                 symbology=fullRLF)
        param2.displayOrder = 16

        param3 = ARCPY.Parameter(displayName="Field of Interest",
                                 name="field_of_interest",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param3.filter.list = ["Short", "Long", "String", "Text"]
        param3.parameterDependencies = [param1.name]
        param3.displayOrder = 2
        param3.enabled = True

        param4 = ARCPY.Parameter(displayName="Time Field of Interest",  #####Neww
                                 name="time_field_of_interest",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param4.filter.list = ["Date"]
        param4.parameterDependencies = [param1.name]
        param4.displayOrder = 3
        param4.enabled = True

        param5 = ARCPY.Parameter(displayName="Category of Interest",
                                 name="category_of_interest",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param5.displayOrder = 4
        param5.enabled = True

        param6 = ARCPY.Parameter(displayName="Input Neighboring Features",
                                 name="input_feature_for_comparison",
                                 datatype="GPFeatureLayer",
                                 parameterType="Optional",
                                 direction="Input")
        param6.filter.list = ["Point"]
        param6.displayOrder = 5
        param6.enabled = False

        param7 = ARCPY.Parameter(displayName="Field Containing Neighboring Category",
                                 name="field_for_comparison",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param7.filter.list = ["Short", "Long", "String", "Text"]
        param7.parameterDependencies = [param6.name]
        param7.displayOrder = 6
        param7.enabled = False

        param8 = ARCPY.Parameter(displayName="Time Field of Neighboring Features",  ###New
                                 name="time_field_for_comparison",
                                 datatype="Field",
                                 parameterType="Optional",
                                 direction="Input")
        param8.filter.list = ["Date"]
        param8.parameterDependencies = [param6.name]
        param8.displayOrder = 7
        param8.enabled = False

        param9 = ARCPY.Parameter(displayName="Neighboring Category",
                                 name="category_for_comparison",
                                 datatype="GPString",
                                 parameterType="Optional",
                                 direction="Input")
        param9.displayOrder = 8
        param9.enabled = True

        param10 = ARCPY.Parameter(displayName="Neighborhood Type",
                                  name="neighborhood_type",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")

        param10.filter.type = "ValueList"
        param10.filter.list = ['K_NEAREST_NEIGHBORS',
                               'DISTANCE_BAND',
                               'GET_SPATIAL_WEIGHTS_FROM_FILE'
                               ]

        param10.value = 'K_NEAREST_NEIGHBORS'
        param10.displayOrder = 9

        param11 = ARCPY.Parameter(displayName="Number of Neighbors",
                                  name="number_of_neighbors",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param11.filter.type = "Range"
        param11.filter.list = [1, 1000]
        param11.enabled = True
        param11.displayOrder = 10
        param11.value = 8

        param12 = ARCPY.Parameter(displayName="Distance Band",
                                  name="distance_band",
                                  datatype="GPLinearUnit",
                                  parameterType="Optional",
                                  direction="Input")

        param12.filter.list = supportDist
        param12.enabled = False
        param12.displayOrder = 11

        param13 = ARCPY.Parameter(displayName="Weight Matrix File",
                                  name="weights_matrix_file",
                                  datatype="DEFile",
                                  parameterType="Optional",
                                  direction="Input")
        param13.filter.list = ['swm', 'gwt']
        param13.enabled = False
        param13.displayOrder = 12

        param14 = ARCPY.Parameter(displayName="Temporal Relationship Type",  # Newwwww
                                  name="temporal_relationship_type",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")

        param14.filter.type = "ValueList"
        param14.filter.list = ['BEFORE',
                               'AFTER',
                               'SPAN']
        param14.value = 'BEFORE'
        param14.displayOrder = 13

        param15 = ARCPY.Parameter(displayName="Time Step Interval",  # Newww
                                  name="time_step_interval",
                                  datatype="GPTimeUnit",
                                  parameterType="Optional",
                                  direction="Input")
        param15.filter.list = ["Seconds", "Minutes", "Hours", "Days", "Weeks", "Months", "Years"]
        param15.displayOrder = 14

        param16 = ARCPY.Parameter(displayName="Number of Permutations",
                                  name="number_of_permutations",
                                  datatype="GPLong",
                                  parameterType="Optional",
                                  direction="Input")
        param16.filter.type = "Value List"
        param16.filter.list = [99, 199, 499, 999, 9999]
        param16.value = 99
        param16.displayOrder = 15

        param17 = ARCPY.Parameter(displayName="Local Weighting Scheme",  # Newwwww
                                  name="local_weighting_scheme",
                                  datatype="GPString",
                                  parameterType="Optional",
                                  direction="Input")

        param17.filter.type = "ValueList"
        param17.filter.list = ['BISQUARE',
                               'GAUSSIAN',
                               'NONE']
        param17.value = 'GAUSSIAN'
        param17.category = "Additional Options"
        param17.displayOrder = 17

        param18 = ARCPY.Parameter(displayName="Output Table for Global Relationships",
                                  name="output_table",
                                  datatype="DETable",
                                  parameterType="Optional",
                                  direction="Output")
        param18.category = "Additional Options"
        param18.displayOrder = 18

        params = [param0, param1, param2, param3,
                  param4, param5, param6, param7,
                  param8, param9, param10, param11,
                  param12, param13, param14, param15,
                  param16, param17, param18]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        unique_values = ['None']

        inputType = parameters[0]
        inputFC1 = parameters[1]
        outputFC = parameters[2]
        fieldInterest = parameters[3]
        timeFieldInterest = parameters[4]
        catInterest = parameters[5]
        inputFC2 = parameters[6]
        fieldComparison = parameters[7]
        timeFieldComparison = parameters[8]
        catComparison = parameters[9]
        neighborType = parameters[10]
        numberOfNeighbors = parameters[11]
        distanceBand = parameters[12]
        swmFile = parameters[13]
        temporalRelationType = parameters[14]
        timeInterval = parameters[15]
        numPermutations = parameters[16]
        outputTable = parameters[18]
        kernelType = parameters[17]

        if inputType.value == "SINGLE_DATASET":
            enableParametersBy(parameters, [1, 3, 4, 5, 9], [6, 7, 8])

            if timeFieldInterest.value:
                temporalRelationType.enabled = True
                timeInterval.enabled = True
            else:
                temporalRelationType.enabled = False
                timeInterval.enabled = False

        if inputType.value == "TWO_DATASETS":
            enableParametersBy(parameters, [1, 3, 4, 5, 6, 7, 8, 9], [])

        if inputType.value == "DATASETS_WITHOUT_CATEGORIES":
            enableParametersBy(parameters, [1, 6, 4, 8], [3, 5, 7, 9])

        if inputType.value in ["TWO_DATASETS", "DATASETS_WITHOUT_CATEGORIES"]:

            if timeFieldInterest.value and timeFieldComparison.value:
                temporalRelationType.enabled = True
                timeInterval.enabled = True
            else:
                temporalRelationType.enabled = False
                timeInterval.enabled = False

        if inputType.value == "SINGLE_DATASET":
            inputFC2.value = None

        if inputType.value in ["SINGLE_DATASET", "TWO_DATASETS"]:
            if inputFC1.value:
                if fieldInterest.value:
                    try:
                        if self.ssdoTarget is None or self.ssdoTarget.inputFC != inputFC1.valueAsText:
                            self.ssdoTarget = UTILS.BasicReader(inputFC1.value)

                        self.ssdoTarget.obtainData(fieldName=fieldInterest.value.value)
                        unique = UTILS.NUM.unique(self.ssdoTarget.data[fieldInterest.value.value.upper()])
                        uniqueValues = [str(i) for i in unique if str(i) != '']
                        catInterest.filter.list = uniqueValues
                        catComparison.filter.list = uniqueValues

                        if len(uniqueValues) == 0:
                            catInterest.value = None
                            if inputFC2.value is None:
                                catComparison.value = None

                        if catInterest.value is not None and catInterest.value not in uniqueValues:
                            catInterest.value = None

                        if catComparison.value is not None and \
                                catComparison.value not in uniqueValues and \
                                inputFC2.value is None:
                            catComparison.value = None
                    except:
                        catInterest.filter.list = []
                        catComparison.filter.list = []

        if inputType.value == "TWO_DATASETS":
            catComparison.filter.list = []

            if inputFC2.value and fieldComparison.value:
                try:
                    if self.ssdoSource is None or self.ssdoSource.inputFC != inputFC2.valueAsText:
                        self.ssdoSource = UTILS.BasicReader(inputFC2.value)
                    self.ssdoSource.obtainData(fieldName=fieldComparison.value.value)
                    unique = UTILS.NUM.unique(self.ssdoSource.data[fieldComparison.value.value.upper()])
                    uniqueValues = [str(i) for i in unique if str(i) != '']
                    catComparison.filter.list = uniqueValues

                    if len(uniqueValues) == 0:
                        catComparison.value = None

                    if catComparison.value is not None and catComparison.value not in uniqueValues:
                        catComparison.value = None
                except:
                    catComparison.filter.list = []
            else:
                catComparison.filter.list = []
                catComparison.value = None

        if inputType.value == "DATASETS_WITHOUT_CATEGORIES":
            fieldInterest.value = None
            catInterest.value = None
            fieldComparison.value = None
            catInterest.filter.list = []
            catComparison.filter.list = []
            catComparison.value = None

        if timeFieldInterest.value:
            neighborType.filter.list = ['DISTANCE_BAND']
            neighborType.value = 'DISTANCE_BAND'
        else:
            if inputType.value == "SINGLE_DATASET":
                neighborType.filter.list = ['K_NEAREST_NEIGHBORS', 'DISTANCE_BAND', 'GET_SPATIAL_WEIGHTS_FROM_FILE']
            else:
                neighborType.filter.list = ['K_NEAREST_NEIGHBORS', 'DISTANCE_BAND']

        if neighborType.valueAsText == "K_NEAREST_NEIGHBORS":
            numberOfNeighbors.enabled = True
            distanceBand.enabled = False
            distanceBand.value = None
            swmFile.enabled = False
            swmFile.value = None

        if neighborType.valueAsText == "DISTANCE_BAND":
            distanceBand.enabled = True
            numberOfNeighbors.enabled = False
            numberOfNeighbors.value = None
            swmFile.enabled = False
            swmFile.value = None

        if neighborType.valueAsText == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            numberOfNeighbors.enabled = False
            distanceBand.enabled = False
            numberOfNeighbors.value = None
            distanceBand.value = None
            swmFile.enabled = True

        if neighborType.valueAsText == "KNN_THRESHOLD":
            numberOfNeighbors.enabled = True
            distanceBand.enabled = True
            swmFile.enabled = False
            swmFile.value = None

        tableCheck(outputTable)

    def updateMessages(self, parameters):

        inputType = parameters[0]
        inputFC1 = parameters[1]
        outputFC = parameters[2]
        fieldInterest = parameters[3]
        timeFieldInterest = parameters[4]
        catInterest = parameters[5]
        inputFC2 = parameters[6]
        fieldComparison = parameters[7]
        timeFieldComparison = parameters[8]
        catComparison = parameters[9]
        neighborType = parameters[10]
        numberOfNeighbors = parameters[11]
        distanceBand = parameters[12]
        swmFile = parameters[13]
        temporalRelationType = parameters[14]
        timeInterval = parameters[15]
        numPermutations = parameters[16]
        outputTable = parameters[18]
        kernelType = parameters[17]

        if inputType.value in ["TWO_DATASETS", "DATASETS_WITHOUT_CATEGORIES"]:

            if timeFieldInterest.value:
                if not timeFieldComparison.value:
                    timeFieldComparison.setIDMessage("ERROR", 530)
            if timeFieldComparison.value:
                if not timeFieldInterest.value:
                    timeFieldInterest.setIDMessage("ERROR", 530)

        if timeFieldInterest.value:
            if not timeInterval.value:
                timeInterval.setIDMessage("ERROR", 530)

        if inputType.value == "SINGLE_DATASET":
            if not fieldInterest.value:
                fieldInterest.setIDMessage("ERROR", 530)
            else:
                if not catInterest.value:
                    catInterest.setIDMessage("ERROR", 530)
                if not catComparison.value:
                    catComparison.setIDMessage("ERROR", 530)

        if inputType.value == "TWO_DATASETS":
            if fieldInterest.value:
                if not catInterest.value:
                    catInterest.setIDMessage("ERROR", 530)

            if not inputFC2.value:
                inputFC2.setIDMessage("ERROR", 530)
            else:
                if fieldComparison.value:
                    if not catComparison.value:
                        catComparison.setIDMessage("ERROR", 530)

        if inputType.value == "DATASETS_WITHOUT_CATEGORIES":
            if not inputFC2.value:
                inputFC2.setIDMessage("ERROR", 530)

        if distanceBand.value:
            bandSizeUnit = distanceBand.value.value
            try:
                bandSizeParts = bandSizeUnit.split()
                bandSize = UTILS.strToFloat(bandSizeParts[0])

                if bandSize <= 0:
                    distanceBand.setIDMessage("ERROR", 531)
            except:
                pass

        if neighborType.valueAsText == "KNN_THRESHOLD":
            if not numberOfNeighbors.value:
                numberOfNeighbors.setIDMessage("ERROR", 530)
            if not distanceBand.value:
                distanceBand.setIDMessage("ERROR", 530)

        if neighborType.valueAsText == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            if not swmFile.value:
                swmFile.setIDMessage("ERROR", 530)

        if outputFC.value and outputTable.value:
            if outputFC.valueAsText.upper() == outputTable.valueAsText.upper():
                outPath, outName = OS.path.split(outputFC.valueAsText)
                outputTable.setIDMessage("ERROR", 110275, outName)
        pass

    def execute(self, parameters, messages):
        import SSColocation as SSC
        import imp
        imp.reload(SSC)

        kNeighbors = None
        threshold = None
        swmFile = None

        inputFC = UTILS.getTextParameter(1, parameters)
        outputFC = UTILS.getTextParameter(2, parameters)
        field1 = UTILS.getTextParameter(3, parameters, fieldName=True)
        timeField1 = UTILS.getTextParameter(4, parameters, fieldName=True)
        cat1 = UTILS.getTextParameter(5, parameters, fieldName=True)
        inputFC2 = UTILS.getTextParameter(6, parameters)
        field2 = UTILS.getTextParameter(7, parameters, fieldName=True)
        timeField2 = UTILS.getTextParameter(8, parameters, fieldName=True)
        cat2 = UTILS.getTextParameter(9, parameters, fieldName=True)
        method = UTILS.getTextParameter(10, parameters)

        if method == "K_NEAREST_NEIGHBORS":
            kNeighbors = UTILS.getNumericParameter(11, parameters)
            threshold = None

            if kNeighbors is None:
                kNeighbors = -1

        if method == "DISTANCE_BAND":
            threshold = UTILS.getTextParameter(12, parameters)
            kNeighbors = None

            if threshold is None:
                threshold = -1

        if method == "KNN_THRESHOLD":
            kNeighbors = UTILS.getNumericParameter(11, parameters)
            threshold = UTILS.getTextParameter(12, parameters)

        if method == "GET_SPATIAL_WEIGHTS_FROM_FILE":
            swmFile = UTILS.getTextParameter(13, parameters)
            kNeighbors = None
            threshold = None

        typeMethod = UTILS.getTextParameter(14, parameters)
        timeInterval = UTILS.getTextParameter(15, parameters)

        permutations = UTILS.getNumericParameter(16, parameters)
        if permutations is None:
            permutations = 99

        kernelType = UTILS.getTextParameter(17, parameters)
        outputTable = UTILS.getTextParameter(18, parameters)

        if kernelType == "GAUSSIAN":
            kernelType = 0

        if kernelType == "BISQUARE":
            kernelType = 1

        if kernelType == "NONE":
            kernelType = 2

        if kernelType is None:
            kernelType = 0

        seed = 10
        #### Outputs ####
        UTILS.checkOutputPath(outputFC, "FC")
        UTILS.checkOutputPath(outputTable, "TABLE")

        ssdo1 = SSDO.SSDataObject(inputFC, useChordal=True)
        ssdo2 = None

        if inputFC2 is not None:
            ssdo2 = SSDO.SSDataObject(inputFC2, explicitSpatialRef=ssdo1.spatialRef,
                                      useChordal=True, silentWarnings=True)

        coloq = SSC.ColocationQuotient(ssdo1, field1, ssdo2, field2, seed,
                                       cat1, cat2, outputFC, swmFile,
                                       timeField1, timeField2,
                                       typeMethod, timeInterval)

        #### Calculate Local Colocation ####
        data, index1, idCats, member = coloq.getLocalValues(permutations, threshold, kNeighbors, kernelType)
        coloq.createOutputLocalOutput(data, index1, idCats, member)

        #### Calculate Global Colocation ####
        coloq.getGlobalValues(permutations, outputTable, parameters=parameters)

