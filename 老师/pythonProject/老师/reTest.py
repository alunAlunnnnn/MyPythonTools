import re

myStr = 'MULTILINESTRING ((104.99989458194595 35.000122367747998, 104.99992016115176 35.000121772882743, 104.99993443791779 35.00011522936498, 104.99996120685411 35.000101547464197, 104.99998976038617 35.00008727069816, 105.00001771905299 35.000068829875367, 105.00003021122328 35.000055147974585, 105.00003318554953 35.000043845534805, 105.0000212882445 35.000034922556033, 105.00000225255646 35.00003789688229, 104.99999630390394 35.000051578783079, 105.0000004679607 35.000065260683861, 105.00002188310975 35.000080727180396, 105.00004865204606 35.000083701506654, 105.00007125692562 35.000067045279614, 105.00009314796685 35.000054672082378, 105.00010873343646 35.000034922556033, 105.00013193318127 35.00001648173324, 105.00015394319557 34.999996851179944, 105.00016940969211 34.999968297647875, 105.00017178915311 34.99995759007335, 105.00017416861412 34.999936174924301, 105.00015929698283 34.999929036541282, 105.00013966642953 34.999939744115807, 105.00013014858551 34.999955805477597, 105.00013550237277 34.99996948737838, 105.00016762509635 34.999977815491896, 105.00019855808944 34.999972461704637, 105.00022413729525 34.999959374669103, 105.00024138838754 34.99994152871156, 105.00025685488407 34.999932010867539, 105.00027648543737 34.999925467349769, 105.00030920302619 34.999925467349769, 105.00033299763625 34.999927846810778))'

obj = re.search('[\(].*', myStr)
print(obj)
print(obj.group()[2:-2])
print(obj.group())
print(type(obj.group()))
subStr = " " + obj.group()[2:-2]
# subStr = obj.group()[2:-2]
sub1 = subStr.split(",")
tempList = [each[1:] for each in subStr.split(",") if each.startswith(" ")]

sub2 = [tuple(map(float, each.split(" "))) for each in tempList]
print(sub2)
for x, y in sub2:
    print(x, y)