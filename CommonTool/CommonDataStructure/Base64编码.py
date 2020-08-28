import base64
testStr = 'abcd'
print(base64.b64encode(testStr.encode()))

alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'


def myBase64(src):

    # 最终返回的二进制字节码序列
    res = bytearray()

    # 获取输入的字符的字节长度，判断要从哪断开
    length = len(src)

    # 初始化一个r，用于记录输入的src最后需要补几个0
    # 才能补齐为三个字节
    r = 0

    # 进行字节分组，分为每三个字节一组
    for offset in range(0, length, 3):
        # 将所有可以组成3个字节的数据分组，避免分组中出现空
        if offset + 3 <= length:
            triple = src[offset:offset + 3]
        else:
            # 将剩下的不足3个字节的数据单独分组
            triple = src[offset:]

            # 记录需要给最后的字节补几个0x00
            r = 3 - len(triple)

            # 给最后的分组补充0x00
            triple = triple + '\x00' * r

        # 1、通过triple.encode()将字符转为字节（bytes）
        # 2、通过大端模式（视系统而定， 为了保证数据的顺序不会反过来），将数据从内存中读出
        # 3、将bytes数据转换为十进制的数值 int.from_bytes()
        b = int.from_bytes(triple.encode(), 'big')

        # 通过对二进制的数据进行移位操作，来将 3个字节 共24个bit 重组为 4个 6bit的数据
        #    由于使用的是大端读取的数据，所以数据的顺序是从左至右
        #    此处将数据 b（代表3个一组的字符数据的字节码的10进制数） 进行移位（操作其二进制数据），以重组数据bit
        for i in range(18, -1, -6):
            # 第一次移动，只保留最左侧的6位
            if i == 18:
                # index为移位重组为6bit之后，其二进制数据所对应的整数，此数即为Base64编码表中 字符的索引值
                index = b >> i
            else:
                # 当后面移动时，每次移动6n位，再通过 & 为与运算符，保留最后的6位，其余均为补位0或 & 运算后的0
                index = b >> i & 0x3F # 0x3F 为 0b0011 1111，用于仅保留移位后最右侧的6位二进制数

            # alphabet为Base64对应表
            res.append(alphabet[index])

        # 此处通过上面记录的补了几个0x00，将其替换为 "=" 进行标识
        for i in range(1, r+1):
            # 0x3D为 = 的ascii码
            res[-i] = 0x3D

    return res
testStr = 'abcd'
print(myBase64(testStr))


