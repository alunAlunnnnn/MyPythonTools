# coding: utf-
# author:xupf esrichina
# time:20200204
# description:custom write files into couchdb and write log when meet errors
# version:i3s 1.6 & 1.7 3DObject IntegratedMesh
# mod:20200219

import os, gzip, sys, subprocess, json
import couchdb
import ssl
import json, shutil, zipfile
from threading import Thread
import multiprocessing

ssl._create_default_https_context = ssl._create_unverified_context

jishu = 0
Messagenum = 0


def async2(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
        ques.append(thr)

    return wrapper


# @async
def writeNode(jobs, jobpath, content):
    try:
        global jishu
        for job in jobs:
            jishu += 1
            if jishu % 500 == 0:
                tttttt = str(jishu / arcpy_AddMessagenum * 100) + "%"
                print(tttttt)
            flag = job.split('/')
            nodename = flag[1]
            filetype = flag[2]
            pd = filetype[0]
            resources = 'nodes_' + nodename + '_resources'
            try:
                d[resources] = {}
            except:
                pass
            # 3dNodeIndexDocument.json.gz
            if pd == '3':
                featureFile = slpkfile.read(job)
                file_content = gzip.decompress(featureFile)
                featureJson = json.loads(file_content)
                indexname = 'nodes_' + nodename
                d[indexname] = featureJson

            # attributes
            elif pd == 'a':
                indexname = 'nodes_' + nodename
                resources = indexname + '_resources'
                attname = indexname + '_attributes_' + flag[3] + "_0"
                featureFile = slpkfile.read(job)
                d.put_attachment(
                    d[resources], featureFile, attname,
                    'content-type: application/octet-stream; charset=binary'
                )
            # features
            elif pd == 'f':
                indexname = 'nodes_' + nodename
                featureFile = slpkfile.read(job)
                file_content = gzip.decompress(featureFile)
                featureJson = json.loads(file_content)
                feaname = indexname + '_features_0'
                d[feaname] = featureJson
            # geometries
            elif pd == 'g':
                indexname = 'nodes_' + nodename
                resources = indexname + '_resources'
                geoname = indexname + '_geometries_' + flag[-1][0]
                featureFile = slpkfile.read(job)
                d.put_attachment(
                    d[resources], featureFile, geoname,
                    'content-type: application/octet-stream; charset=binary')
            # shared
            elif pd == 's':
                indexname = 'nodes_' + nodename
                sharedname = indexname + '_shared'
                featureFile = slpkfile.read(job)
                file_content = gzip.decompress(featureFile)
                featureJson = json.loads(file_content)
                d[sharedname] = featureJson
            # textures
            elif pd == 't':
                indexname = 'nodes_' + nodename
                resources = indexname + '_resources'
                featureFile = slpkfile.read(job)
                texname = indexname + '_textures_' + flag[-1].split('.')[0]
                d.put_attachment(d[resources], featureFile, texname,
                                 'content-type: image/jpg')

    except Exception as ms:
        print(ms)
        content['nodeindex'] = jobs.index(job)
        with open(jobpath, 'w') as wf:
            jscontent = json.dumps(content)
            wf.write(jscontent)


# @async2
def writePage(jobs, jobpath, left, right):
    try:
        global jishu
        for job in jobs:
            jishu += 1
            if jishu % 100 == 0:
                tttttt = str(jishu / arcpy_AddMessagenum * 100) + "%"
                print(tttttt)
            featureFile = slpkfile.read(job)
            featureContent = gzip.decompress(featureFile)
            featureJson = json.loads(featureContent)
            indexname = 'nodepage_' + job.split('/')[1].split('.')[0]
            d[indexname] = featureJson
    except Exception as ms:
        print(ms)
        try:
            wf = open(jobpath, 'r')
            cont = json.loads(wf.read())
            wf.close()
        except:
            cont = {}
        cont['pageleft'] = left
        cont['pageright'] = right
        cont['pageindex'] = jobs.index(job)
        temp = json.dumps(cont)
        wf = open(jobpath, 'w')
        wf.write(temp)
        wf.close()


if __name__ == "__main__":
    ################
    db = couchdb.Server("https://admin:admin@ag.njcim.gis06:29081")
    d = db["obj_slpk_0_7cb18c64b5784e31af0a5889253e4281"]
    ques = []
    slpk = r'D:\data\qh_objtest.slpk'
    cpu_nums = 8
    per = 0
    # couchPath=arcpy.GetParameterAsText(0)
    # admin=arcpy.GetParameterAsText(1)
    # password=arcpy.GetParameterAsText(2)
    # Dataindex=arcpy.GetParameterAsText(3)

    # db=couchdb.Server("https://"+admin+":"+password+"@"+couchPath.split('https://')[1])
    # d=db[Dataindex]
    # slpk =arcpy.GetParameterAsText(4)
    # cpu_nums =int(arcpy.GetParameter(5))
    # ques = []

    ############## get sceneLayer
    print("powered by esri xupf\n")
    print("start write node files\n")
    nodes = []
    nodepages = []
    slpkfile = zipfile.ZipFile(slpk, 'r', zipfile.ZIP_STORED)
    slpklist = slpkfile.namelist()

    for slpkl in slpklist:
        if slpkl[:5] == 'nodes':
            nodes.append(slpkl)
        elif slpkl[:5] == 'nodep':
            nodepages.append(slpkl)

    print('nodes sum:')
    print(len(nodes))
    # multi node working
    logs = os.path.join(sys.path[0], 'logs')
    if os.path.exists(logs):
        shutil.rmtree(logs)
    os.mkdir(logs)

    num = len(nodes)
    arcpy_AddMessagenum = len(nodepages) + num
    pernode = int(num / cpu_nums)
    for i in range(per, per + 1):
        content = {"Thread": i}
        print('Thread:')
        print(i)
        jobpath = os.path.join(logs, "job_%d.json" % i)
        left = i * pernode
        right = left + pernode
        if i == cpu_nums - 1:
            content["nodeleft"] = left
            content["noderight"] = 0
            jobs = nodes[left:]
        else:
            content["nodeleft"] = left
            content["noderight"] = right
            jobs = nodes[left:right]
        # with open(jobpath, 'w') as wf:
        #     jscontent=json.dumps(content)
        #     wf.write(jscontent)
        ###########
        writeNode(jobs, jobpath, content)
    # for que in ques:
    #     que.join()
    # ques.clear()

    num = len(nodepages)
    pernode = int(num / cpu_nums)
    print('write nodepages')
    for i in range(per, per + 1):
        print('Thread:')
        print(i)
        jobpath = os.path.join(logs, "job_%d.json" % i)
        left = i * pernode
        right = left + pernode
        if i == cpu_nums - 1:
            jobs = nodepages[left:]
            right = 0
        else:
            jobs = nodepages[left:right]
        writePage(jobs, jobpath, left, right)

    # for que in ques:
    #     que.join()
    slpkfile.close()
    print('Finish!')





