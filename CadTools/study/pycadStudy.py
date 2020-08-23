import shapefile

data = r'D:\pyshpTest\gd2d_FeatureVerticesToPoints4'

shp = shapefile.Reader(data)

print(shp)

print(shp.fields)

print(shp.shapeType)
print(shp.shapeTypeName)
print(shp.bbox)


shapes = shp.shapes()
print(shapes)

shape0 = shp.shape()
print(shape0)

print(['%.3f' % coord for coord in shape0.bbox])
print(shape0.parts)

# geoj = shape0.__geo_interface__
# print(geoj)


print(shp.records())


# def cal(x1, y1, x2, y2):
#     k = ( y2 - y1 ) / ( x2 - x1 )
#     b = y1 - (k * x1)
#     return 'y = (%s) * x + (%s)' % (k ,b)
#
# print(cal(9933831.7318, 3706653.6313, 15330719.419, 6108565.1844))
# print( 0.44505494505596305 * 12632275.5754 - 714447.3042914313)