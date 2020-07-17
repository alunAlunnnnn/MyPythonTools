import requests, os, sys, json, time
import arcpy


arcpy.env.overwriteOutput = True

def AddFields(inFC):
    FieldList = [{
            "name": "OBJECTID_1",
            "alias": "OBJECTID_1",
            "type": "esriFieldTypeOID"
        }, {
            "name": "OBJECTID",
            "alias": "OBJECTID",
            "type": "esriFieldTypeDouble"
        }, {
            "name": "ENTIID",
            "alias": "ENTIID",
            "type": "esriFieldTypeString",
            "length": 30
        }, {
            "name": "NAME",
            "alias": "NAME",
            "type": "esriFieldTypeString",
            "length": 200
        }, {
            "name": "ENTICLASSI",
            "alias": "ENTICLASSI",
            "type": "esriFieldTypeString",
            "length": 15
        }, {
            "name": "HYCLASSID",
            "alias": "HYCLASSID",
            "type": "esriFieldTypeString",
            "length": 50
        }, {
            "name": "BORNTIME",
            "alias": "BORNTIME",
            "type": "esriFieldTypeDate",
            "length": 8
        }, {
            "name": "ENDTIME",
            "alias": "ENDTIME",
            "type": "esriFieldTypeDate",
            "length": 8
        }, {
            "name": "IDBDATE",
            "alias": "IDBDATE",
            "type": "esriFieldTypeDate",
            "length": 8
        }, {
            "name": "ADRESS",
            "alias": "ADRESS",
            "type": "esriFieldTypeString",
            "length": 200
        }, {
            "name": "FLOOR",
            "alias": "FLOOR",
            "type": "esriFieldTypeDouble"
        }, {
            "name": "QSDW",
            "alias": "QSDW",
            "type": "esriFieldTypeString",
            "length": 50
        }, {
            "name": "SHAPE_LENG",
            "alias": "SHAPE_LENG",
            "type": "esriFieldTypeDouble"
        }
    ]

    for each in FieldList:
        fieldName = each['name']
        fieldAlias = each['alias']
        fieldType = each['type']
        typeMap = {'esriFieldTypeOID': 'DOUBLE', 'esriFieldTypeDouble': 'DOUBLE',
                   'esriFieldTypeString': 'TEXT', 'esriFieldTypeDate': 'DATE',
                   }
        newFieldType = typeMap[fieldType]
        if each.get('length'):
            fieldLength = each['length']
            arcpy.AddField_management(inFC, fieldName, newFieldType, field_length=fieldLength)
        else:
            arcpy.AddField_management(inFC, fieldName, newFieldType)

    return inFC


def CreateFeatureClass(outputPath, outputName):
    sr = arcpy.SpatialReference(4326)
    inFC = arcpy.CreateFeatureclass_management(outputPath, outputName, 'POLYGON', spatial_reference=sr)
    AddFields(inFC)
    return inFC

outputPath = r'E:\长江镇数据爬取\长江镇数据创建'
outputName = 'cjz_FeaSer'

data = CreateFeatureClass(outputPath, outputName)

fieldList = ['OBJECTID_1', 'OBJECTID', 'ENTIID', 'NAME', 'ENTICLASSI', 'HYCLASSID', 'BORNTIME', 'ENDTIME', 'IDBDATE', 'ADRESS', 'FLOOR', 'QSDW', 'SHAPE_LENG']

inField = ['SHAPE@', 'OBJECTID_1', 'OBJECTID', 'ENTIID', 'NAME', 'ENTICLASSI', 'HYCLASSID', 'BORNTIME', 'ENDTIME', 'IDBDATE', 'ADRESS', 'FLOOR', 'QSDW', 'SHAPE_LENG']

i = 1
a = True
# with open(r'E:\长江镇数据爬取\plg.txt', 'w', encoding='utf-8') as f:
with arcpy.da.InsertCursor(data, inField) as cur:
    dataList = []
    while i < 3000:
        time.sleep(2)
        baseurl = 'http://geowork.wicp.vip:25081/arcgis/rest/services/rugao/rugaocjz/FeatureServer/0/query?where=OBJECTID_1%3E%3D{}+AND+OBJECTID_1%3C{}&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=*&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&gdbVersion=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&multipatchOption=&f=json'.format(i, i+999)
        i += 999

        # para = {
        #     'f': 'json',
        #     'layerDefs': [{'layerId': 0, 'where': '1=1', 'outFields': '*'}],
        #     }

        res = requests.get(baseurl)

        print(res.text)
        jsonData = json.loads(res.text)
        # oOID = jsonData['objectIdFieldName']
        # oFields = jsonData.get('features', 'alun')
        oFeatures = jsonData['features']
        for eachFea in oFeatures:
            oCoord = eachFea['geometry']['rings']
            oAttr = eachFea['attributes']
            # print(oCoord)

            # create feature
            for eachPlg in oCoord:
                # print([eachPnt for eachPnt in eachPlg])
                insertFc = arcpy.Polygon(arcpy.Array([arcpy.Point(*eachPnt) for eachPnt in eachPlg]))
                print([eachPnt for eachPnt in eachPlg])
                dataList.append(insertFc)
            fcList = [insertFc]

            # set attributes
            attrList = [oAttr[eachF] for eachF in fieldList]

            # row list
            rowList = fcList + attrList
            # print(rowList)
            cur.insertRow(rowList)

        # f.write(res.text)
        # f.write('\n')
    arcpy.CopyFeatures_management(dataList, r'E:\长江镇数据爬取\长江镇数据创建\alun.shp')
