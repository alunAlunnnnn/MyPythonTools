for j in range(df2_rowNum):
    df2_rowDataList = df2.iloc[i].values

    # 获取 df1 当前数据的范围
    df2_extent = (df2_rowDataList[10], df2_rowDataList[12],
                  df2_rowDataList[11], df2_rowDataList[13])
    df2_gj = df2_rowDataList[2]
    df2_firstPnt = (df2_rowDataList[3], df2_rowDataList[4], df2_rowDataList[5])
    df2_lastPnt = (df2_rowDataList[6], df2_rowDataList[7], df2_rowDataList[8])

    line1 = lineEquation(df2_firstPnt, df2_lastPnt, df2_extent)