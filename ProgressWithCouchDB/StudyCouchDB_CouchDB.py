import couchdb, gzip
from couchdb import util

# ssl._create_default_https_context = ssl._create_unverified_context

# couchPath = 'https://hispatial.njcim.gis:29081'
# http://HISPATIAL108.com:29080/_utils/#login
couchPath = 'https://HISPATIAL108.com:29081'
admin = 'admin_hdc8t'
password = '08f24atscy'
Dataindex = 'small_slpk_0_0947fbe54f3f469bbb15ae4949aa45fc'



couchPath = 'https://hispatial107.com:29081'
admin = 'admin_whkc9'
password = '1h1sr35bn2'
Dataindex = 'small_slpk_0_d7aeeed6ea424dd8a33af59947e5ed17'

dbServer = couchdb.Server("https://" + admin + ":" + password + "@" + couchPath.split('https://')[1])

# disable the ssl verify
dbServer.resource.session.disable_ssl_verification()

mydb = dbServer[Dataindex]


# def unzipGZ(gzdata):
#     with gzip.open(gzdata, "rb") as gdata:
#         gzRes = gdata.read()
#     with open("D:/a/te.dds")

with open(r"D:\a\b")



for each in mydb:
    # if str(each) == "nodes_306_resources":
    #     # get doc object
    #     doc = mydb.get(each)
    #
    #     # get attachment from db object
    #     # attFile = mydb.get_attachment(doc, "nodes_306_textures_0")
    #     # with open("D:/a/test.jpg", "wb") as f:
    #     #     f.write( attFile.read() )
    #
    #     # todo compress the photo(.jpg and .dds)
    #
    #     with open("D:/a/timg.jpg", "rb") as f:
    #         data = f.read()
    #     # upload the photo into couchdb
    #     mydb.put_attachment(doc, data, "nodes_306_textures_0", "image/jpg")

    if "_resources" in str(each):
        doc = mydb.get(each)
        num = each.split("_")[1]
        with open("D:/a/timg.jpg", "rb") as f:
            data = f.read()
        # upload the photo into couchdb
        mydb.put_attachment(doc, data, "nodes_%s_textures_0" % num, "image/jpg")