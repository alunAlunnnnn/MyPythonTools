# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 21:51:12 2020

@author: liyunfei
原始代码来自于: https://stackoverflow.com/questions/29678510/convert-21-equirectangular-panorama-to-cube-map/29681646#29681646
"""

from PIL import Image
from math import pi, sin, cos, tan, atan2, hypot, floor
from numpy import clip


# get x,y,z coords from out image pixels coords
# i,j are pixel coords
# faceIdx is face number
# faceSize is edge length
def outImgToXYZ(i, j, faceIdx, faceSize):
    """此函数被lyf修改过,以适应cesium skybox的贴图
    """
    a = 2.0 * float(i) / faceSize
    b = 2.0 * float(j) / faceSize

    if faceIdx == 0:  # back
        # (x,y,z) = (-1.0, 1.0 - a, 1.0 - b)
        (x, y, z) = (-1.0, 1.0 - b, a - 1.0)
    elif faceIdx == 1:  # left
        (x, y, z) = (a - 1.0, -1.0, 1.0 - b)
    elif faceIdx == 2:  # front
        # (x,y,z) = (1.0, a - 1.0, 1.0 - b)
        (x, y, z) = (1.0, 1.0 - b, 1.0 - a)
    elif faceIdx == 3:  # right
        # (x,y,z) = (1.0 - a, 1.0, 1.0 - b)
        (x, y, z) = (a - 1.0, 1.0, b - 1.0)
    elif faceIdx == 4:  # top
        # (x,y,z) = (b - 1.0, a - 1.0, 1.0)
        (x, y, z) = (a - 1.0, 1.0 - b, 1.0)
    elif faceIdx == 5:  # bottom
        # (x,y,z) = (1.0 - b, a - 1.0, -1.0)
        (x, y, z) = (1.0 - a, 1.0 - b, -1.0)

    return (x, y, z)


# convert using an inverse transformation
def convertFace(imgIn, imgOut, faceIdx):
    inSize = imgIn.size
    outSize = imgOut.size
    inPix = imgIn.load()
    outPix = imgOut.load()
    faceSize = outSize[0]

    for xOut in range(faceSize):
        # print
        print("Current face: %s   progress: %s %%" % (faceIdx, floor(xOut / faceSize * 100)))

        for yOut in range(faceSize):
            (x, y, z) = outImgToXYZ(xOut, yOut, faceIdx, faceSize)
            theta = atan2(y, x)  # range -pi to pi
            r = hypot(x, y)
            phi = atan2(z, r)  # range -pi/2 to pi/2

            # source img coords
            uf = 0.5 * inSize[0] * (theta + pi) / pi
            vf = 0.5 * inSize[0] * (pi / 2 - phi) / pi

            # Use bilinear interpolation between the four surrounding pixels
            ui = floor(uf)  # coord of pixel to bottom left
            vi = floor(vf)
            u2 = ui + 1  # coords of pixel to top right
            v2 = vi + 1
            mu = uf - ui  # fraction of way across pixel
            nu = vf - vi

            # Pixel values of four corners
            A = inPix[ui % inSize[0], int(clip(vi, 0, inSize[1] - 1))]
            B = inPix[u2 % inSize[0], int(clip(vi, 0, inSize[1] - 1))]
            C = inPix[ui % inSize[0], int(clip(v2, 0, inSize[1] - 1))]
            D = inPix[u2 % inSize[0], int(clip(v2, 0, inSize[1] - 1))]

            # interpolate
            (r, g, b) = (
                A[0] * (1 - mu) * (1 - nu) + B[0] * (mu) * (1 - nu) + C[0] * (1 - mu) * nu + D[0] * mu * nu,
                A[1] * (1 - mu) * (1 - nu) + B[1] * (mu) * (1 - nu) + C[1] * (1 - mu) * nu + D[1] * mu * nu,
                A[2] * (1 - mu) * (1 - nu) + B[2] * (mu) * (1 - nu) + C[2] * (1 - mu) * nu + D[2] * mu * nu)

            outPix[xOut, yOut] = (int(round(r)), int(round(g)), int(round(b)))


## ★★★
## 由使用者自行提供原图的路径fp，此原图应为星空背景的2D图，在地心天球坐标系下，且投影方式为
##   等距圆柱投影（ plate carrée projection /Cylindrical-Equidistant）。
# 注意fp的路径，最后此代码文件与原图在同一文件夹内

# fp = "TychoSkymapII.t5_04096x02048.tif"
# fp = 'TychoSkymapII.t3_08192x04096.tif'
# fp = 'starmap_2020_8k.png'
# fp = 'TychoSkymapII.t5_16384x08192.jpg'
fp = r"D:\codeProjcet\ArcGISProPycharm\myScript\自用工具_github\温州超图\图片转天空盒\data\process\44_UP.jpg"

imgIn = Image.open(fp)
inSize = imgIn.size
# 立方体图片的宽度默认为源图片长度的1/4
faceSize = int(inSize[0] / 4)
components = fp.rsplit('.', 1)

# 立方体贴图6个面的编号与cesium贴图名称后缀的关系(lyf调整)
FACE_NAMES = {
    0: '100_BK.jpg',  # back
    1: '100_LF.jpg',  # left
    2: '100_FR.jpg',  # front
    3: '100_RT.jpg',  # right
    4: '44_UP.jpg',  # top
    5: '100_DN.jpg'  # bottom'
}

# 循环生成六个面的贴图，贴图格式为jpg
for face in range(6):
    print("face:", face)
    imgOut = Image.new("RGB", (faceSize, faceSize), "black")
    convertFace(imgIn, imgOut, face)
    imgOut.save(components[0] + "_" + FACE_NAMES[face] + ".jpg")

print('complete!!!')
