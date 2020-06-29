import os, gzip
from PIL import Image




# 3dNodeIndexDocument.json
def uncompressGzData(baseDir):
    subDirList = os.listdir(baseDir)
    for i, each in enumerate(subDirList):
        if i % 50 == 0:
            print(i)

        indexDocDir = os.path.join(baseDir, each)
        indexDoc = [ eachData for eachData in os.listdir(indexDocDir) if '3dNodeIndexDocument.json' in eachData][0]
        docData = os.path.join(indexDocDir, indexDoc)
        savData = os.path.join(indexDocDir, indexDoc[:-3])
        with gzip.open(docData, 'rb') as f:
            data = f.read()
        with open(savData, 'wb') as f:
            f.write(data)


def compressJPG(baseDir, nodesId, jpgFile):
    pass


def getResourceFromNodePagesIndex(nodePagesDir, targetLevel):
    targetLevel = int(targetLevel)
    if targetLevel == 1:
        minIndex = 1
        maxIndex = 4
    else:
        minIndex = 1 + 4 ** (targetLevel - 1)
        maxIndex = 4 + 4 ** (targetLevel - 1)

    # if maxIndex



def main():
    pass



nodesDir = r'E:\slpk\max\nodes'
compressLevel = [i for i in range(1, 21)]
# esri official slpk v1.7 _ level 1~2
# compressLevelNodes = [16, 37, 58, 79, 0, 5, 10, 15, 21, 26, 31, 36, 42, 47, 52, 57, 63, 68, 73, 78]
# esri official slpk v1.7 _ level 1
# compressLevelNodes = [16, 37, 58, 79]
compressLevelNodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 42, 43, 44, 48, 49, 50, 51, 52, 53, 54, 55, 58, 59, 61, 64, 65, 66, 67, 68, 69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 82, 86, 91, 96, 97, 98, 102, 103, 106, 109, 110, 111, 112, 113, 114, 115, 116, 119, 120, 121, 122, 123, 124, 125, 126, 131, 133, 135, 136, 137, 138, 139, 140, 141, 142, 144, 149, 150, 151, 152, 153, 154, 155, 156, 160, 163, 164, 165, 166, 167, 168, 169, 170, 172, 175, 176, 178, 179, 180, 182, 183, 184, 185, 186, 187, 188, 189, 191, 192, 193, 194, 195, 196, 197, 198, 203, 208, 209, 211, 215, 220, 225, 226, 227, 228, 229, 230, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 243, 244, 245, 246, 247, 248, 249, 250, 252, 253, 254, 255, 256, 257, 258, 259, 261, 262, 263, 264, 265, 266, 267, 268, 271, 272, 273, 274, 275, 276, 277, 278, 281, 282, 283, 284, 285, 286, 287, 288, 291, 292, 293, 294, 295, 296, 297, 298, 303, 306, 311, 312, 313, 314, 315, 316, 317, 318, 320, 321, 322, 323, 324, 325, 326, 327, 330, 331, 332, 333, 334, 335, 336, 337, 341, 342, 343, 344, 345, 346, 347, 348, 351, 352, 354, 359, 360, 361, 362, 363, 364, 365, 366, 369, 370, 371, 372, 373, 374, 375, 376, 381, 382, 383, 384, 385, 386, 387, 388, 392, 395, 396, 401, 405, 406, 407, 408, 409, 410, 411, 412, 414, 415, 416, 417, 418, 419, 420, 421, 426, 431, 432, 435, 436, 437, 438, 439, 440, 441, 442, 444, 445, 446, 447, 448, 449, 450, 451, 453, 454, 459, 461, 463, 466, 467, 468, 469, 470, 471, 472, 473, 476, 477, 478, 479, 480, 481, 482, 483, 485, 486, 487, 488, 489, 490, 491, 492, 495, 498, 499, 500, 501, 502, 503, 504, 505, 510, 511, 512, 513, 514, 515, 516, 517, 519, 522, 523, 524, 525, 526, 527, 528, 529, 532, 533, 534, 535, 536, 537, 538, 539, 541, 542, 543, 544, 545, 546, 547, 548, 550, 551, 552, 553, 554, 555, 556, 557, 559, 560, 561, 562, 563, 564, 565, 566, 568, 569, 570, 571, 572, 573, 574, 575, 577, 578, 579, 580, 581, 582, 583, 584, 586, 587, 588, 589, 590, 591, 592, 593]
textureDir = 'textures'

for each in compressLevelNodes:
    if os.path.exists(os.path.join(nodesDir, str(each), textureDir)):
        targetDir = os.path.join(nodesDir, str(each), textureDir)
        try:
            os.remove(os.path.join(targetDir, '0_0_1.bin.dds.gz'))
        except:
            pass

        try:
            os.remove(os.path.join(targetDir, '0.jpg'))
        except:
            pass

        # copy a .jpg file to target dir
        repImg = Image.open(os.path.join(r'D:\a', 'timg_4m.jpg'))
        repImg.save(os.path.join(targetDir, '0.jpg'))

        # compress jpg image
        img = Image.open(os.path.join(targetDir, '0.jpg'))
        img.save(os.path.join(targetDir, '0_com.jpg'), quality=1)
        del img

        newImg = Image.open(os.path.join(targetDir, '0_com.jpg'))
        os.system('D:/softs/soft/ddsInstall/nvdxt.exe -file %s -output %s -dxt1a -nomipmap' % (os.path.join(targetDir, '0_com.jpg'), os.path.join(targetDir, '0_0_1.bin.dds')))

        del newImg
        try:
            os.remove(os.path.join(targetDir, '0_com.jpg'))
        except:
            pass

        # write to gz
        with open(os.path.join(targetDir, '0_0_1.bin.dds'), 'rb') as f:
            data = f.read()
        with gzip.open(os.path.join(targetDir, '0_0_1.bin.dds.gz'), 'wb') as g:
            g.write(data)

        try:
            os.remove(os.path.join(targetDir, '0_0_1.bin.dds'))
        except:
            pass






