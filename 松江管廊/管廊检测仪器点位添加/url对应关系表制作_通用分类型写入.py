import arcgis
import arcpy
from arcgis.gis import server

# portal url messages
portalUrl = "https://hispatial107.com/arcgis/"
serverlUrl = "https://hispatial107.com/server/"
serverAdminlUrl = "https://hispatial107.com/server/admin"
tokenlUrl = "https://hispatial107.com/server/tokens/generateToken"
portalAdmin = "portaladmin"
serverAdmin = "siteadmin"
portalPasaw = "Hs_123456"

# sing in portal
gisClient = arcgis.gis.GIS(portalUrl, portalAdmin, portalPasaw, verify_cert=False)

# # portal contents
# contents = gisClient.content
#
# #
# res = contents.advanced_search("*")
# print(res)
# services = res["results"]


ser = server.Server(url=serverAdminlUrl, tokenlUrl=tokenlUrl, username=serverAdmin, password=portalPasaw)



