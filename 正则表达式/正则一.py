def splitStr(data):
    splitIndex = []
    for i, eachStr in enumerate(data):
        if eachStr == '\"':
            print(i)
            splitIndex.append(i)
    print(splitIndex)
    print(len(splitIndex))

    for each in splitIndex:
        print(data[each])

    # 确保数据有成对的引号
    assert len(splitIndex) % 2 == 0, "引号数量不成对"

    # 有引号
    if len(splitIndex) > 0:
        resList = []
        for i, each in enumerate(splitIndex):
            print(i, each, len(data)-1)
            # 情况一，引号不开头也不结尾
            if splitIndex[0] != 0 and splitIndex[-1] != len(data) - 1:
                # 第一个引号
                if i == 0:
                    # 引号外的数据
                    data1 = data[0:each][:-1]
                    resList += data1.split(",")

                # 最后一个引号
                elif i == len(splitIndex) - 1:
                    # 最后一个引号内的数据
                    data2 = data[splitIndex[i - 1]: each + 1]
                    resList.append(data2)
                    # 最后一个引号外的数据
                    data1 = data[each + 2:]
                    resList += data1.split(",")

                # 第二个开始到倒数第二个引号之间
                else:
                    # 成对引号的第二个，数据为引号内数据
                    if i % 2 != 0:
                        end = each + 1
                        data1 = data[splitIndex[i - 1]: end]
                        resList.append(data1)
                    # 成对引号的第一个，数据为引号外数据
                    else:
                        start = splitIndex[i - 1] + 2
                        data1 = data[start: each][:-1]
                        if data1 != "":
                            resList += data1.split(",")

            # 情况二，引号开头不结尾
            elif splitIndex[0] == 0 and splitIndex[-1] != len(data) - 1:
                # 第一个引号
                if i == 0:
                    # 引号外的数据
                    data1 = data[0: splitIndex[1] + 1]
                    resList.append(data1)

                # 最后一个引号
                elif i == len(splitIndex) - 1:
                    # 最后一个引号内的数据
                    data2 = data[splitIndex[i - 1]: each + 1]
                    resList.append(data2)
                    # 最后一个引号外的数据
                    data1 = data[each + 2:]
                    resList += data1.split(",")

                # 第二个开始到倒数第二个引号之间
                else:
                    # 成对引号的第二个，数据为引号内数据
                    if i % 2 != 0:
                        if i == 1:
                            continue
                        end = each + 1
                        data1 = data[splitIndex[i - 1]: end]
                        resList.append(data1)
                    # 成对引号的第一个，数据为引号外数据
                    else:
                        start = splitIndex[i - 1] + 2
                        data1 = data[start: each][:-1]
                        if data1 != "":
                            resList += data1.split(",")

            # 情况三，引号结尾不开头
            elif splitIndex[0] != 0 and splitIndex[-1] == len(data) - 1:
                # 第一个引号
                if i == 0:
                    # 引号外的数据
                    data1 = data[0:each][:-1]
                    resList += data1.split(",")

                # 最后一个引号
                elif i == len(splitIndex) - 1:
                    # 最后一个引号内的数据
                    data2 = data[splitIndex[i - 1]:]
                    resList.append(data2)

                # 第二个开始到倒数第二个引号之间
                else:
                    # 成对引号的第二个，数据为引号内数据
                    if i % 2 != 0:
                        end = each + 1
                        data1 = data[splitIndex[i - 1]: end]
                        resList.append(data1)
                    # 成对引号的第一个，数据为引号外数据
                    else:
                        start = splitIndex[i - 1] + 2
                        data1 = data[start: each][:-1]
                        if data1 != "":
                            resList += data1.split(",")

            # 情况四，引号开头并结尾
            elif splitIndex[0] == 0 and splitIndex[-1] == len(data) - 1:
                print(1)
                # 第一个引号
                if i == 0:
                    # 引号外的数据
                    data1 = data[0: splitIndex[1] + 1]
                    resList.append(data1)

                # 最后一个引号
                elif i == len(splitIndex) - 1:
                    # 最后一个引号内的数据
                    data2 = data[splitIndex[i - 1]:]
                    resList.append(data2)

                # 第二个开始到倒数第二个引号之间
                else:
                    # 成对引号的第二个，数据为引号内数据
                    if i % 2 != 0:
                        if i == 1:
                            continue
                        end = each + 1
                        data1 = data[splitIndex[i - 1]: end]
                        resList.append(data1)
                    # 成对引号的第一个，数据为引号外数据
                    else:
                        start = splitIndex[i - 1] + 2
                        data1 = data[start: each][:-1]
                        if data1 != "":
                            resList += data1.split(",")

    # 情况五，无引号的情况
    else:
        resList = data.split(",")
    return resList


# 传入字符
data = '"alun",,,0001c2dba905406b9c03077cfe6c81a3,8431b13f9149452c8d550756f4c919f8,CXA8337,B5278,NULL,8400,ZSAM,ZHHH,20200706004500,20200706005300,20200706004500,4,25,12,,1,23,45,true,2,DO,,,"DO-436,P451-269,P47-204,XUVGI-652,P252-186,KHN-631,PEXEK-207,LAPEN-143,TULMU-345,XSH-0","ZSSSZR12-665,ZSAMAP01-0,ZSSSZR09-465,ZSAMZR02-0,ZSSSZR30-0,ZSFZAP01-0,ZGGGZR16-307,ZSSSZR20-0,ZSSSZR29-0,ZSAMZR04-0","ZSSSZR12-1561,ZSAMAP01-0,ZSSSZR09-0,ZSAMZR02-0,ZSSSZR30-0,ZSFZAP01-0,ZGGGZR16-2728,ZSSSZR20-909,ZSSSZR29-0,ZSAMZR04-0","ZSSSZR12-P252,ZSAMAP01-ZSAM,ZSSSZR09-DO,ZSAMZR02-ZSAM,ZSSSZR30-ZSAM,ZSFZAP01-DO,ZGGGZR16-TULMU,ZSSSZR20-XUVGI,ZSSSZR29-ZSAM,ZSAMZR04-DO",111111,"ZSSSZR12-LAPEN,ZSAMAP01-ZSAM,ZSSSZR09-P47,ZSAMZR02-ZSAM,ZSSSZR30-ZSAM,ZSFZAP01-DO,ZGGGZR16-XSH,ZSSSZR20-XUVGI,ZSSSZR29-DO,ZSAMZR04-DO",3296078301544f36bf4384232d6c7348,ZSAM,20200705132900,20200705143000,20200705141500,20200705140900,1,20200706005500,20200706005500,20200706010100,NULL,1,20200706010500,NULL,B737,2,,NULL,NULL,20,1,DO-ZSAM01,NULL,NULL,,,,NML,0,NULL,NULL,NULL,NULL,20200706104539,NULL,NULL,NULL,1,10,NULL,"alun"'
# data = ',,,0001c2dba905406b9c03077cfe6c81a3,8431b13f9149452c8d550756f4c919f8,CXA8337,B5278,NULL,8400,ZSAM,ZHHH,20200706004500,20200706005300,20200706004500,4,25,12,,1,23,45,true,2,DO,,,"DO-436,P451-269,P47-204,XUVGI-652,P252-186,KHN-631,PEXEK-207,LAPEN-143,TULMU-345,XSH-0","ZSSSZR12-665,ZSAMAP01-0,ZSSSZR09-465,ZSAMZR02-0,ZSSSZR30-0,ZSFZAP01-0,ZGGGZR16-307,ZSSSZR20-0,ZSSSZR29-0,ZSAMZR04-0","ZSSSZR12-1561,ZSAMAP01-0,ZSSSZR09-0,ZSAMZR02-0,ZSSSZR30-0,ZSFZAP01-0,ZGGGZR16-2728,ZSSSZR20-909,ZSSSZR29-0,ZSAMZR04-0","ZSSSZR12-P252,ZSAMAP01-ZSAM,ZSSSZR09-DO,ZSAMZR02-ZSAM,ZSSSZR30-ZSAM,ZSFZAP01-DO,ZGGGZR16-TULMU,ZSSSZR20-XUVGI,ZSSSZR29-ZSAM,ZSAMZR04-DO",111111,"ZSSSZR12-LAPEN,ZSAMAP01-ZSAM,ZSSSZR09-P47,ZSAMZR02-ZSAM,ZSSSZR30-ZSAM,ZSFZAP01-DO,ZGGGZR16-XSH,ZSSSZR20-XUVGI,ZSSSZR29-DO,ZSAMZR04-DO",3296078301544f36bf4384232d6c7348,ZSAM,20200705132900,20200705143000,20200705141500,20200705140900,1,20200706005500,20200706005500,20200706010100,NULL,1,20200706010500,NULL,B737,2,,NULL,NULL,20,1,DO-ZSAM01,NULL,NULL,,,,NML,0,NULL,NULL,NULL,NULL,20200706104539,NULL,NULL,NULL,1,10,NULL,"alun"'
# data = ',,,0001c2dba905406b9c03077cfe6c81a3,8431b13f9149452c8d550756f4c919f8,CXA8337,B5278,NULL,8400,ZSAM,ZHHH,20200706004500,20200706005300,20200706004500,4,25,12,,1,23,45,true,2,DO,,,'

res = splitStr(data)
print(res)
