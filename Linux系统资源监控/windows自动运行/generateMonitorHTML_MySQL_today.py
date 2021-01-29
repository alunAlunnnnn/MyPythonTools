import pyecharts.options as opts
from pyecharts.charts import Line
import pymysql
import sys
import datetime

# sqlite params
tableName = "MYSYS_STATUS"
cpuField = "CPU_USE"
memField = "MEM_USE"
timeField = "RTIME"

# mysql params
ip = "192.168.10.149"
port = 3306
username = "sysmon"
password = "0403"
db = "iserver_monitor"
charset = "utf8"

# mysql
conn = pymysql.connect(
    host=ip,
    port=port,
    user=username,
    password=password,
    db=db,
    charset=charset,
    cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()

today = str(datetime.date.today())
sqlExp = ("select CPU_USE, MEM_USE, RTIME from MYSYS_STATUS where rtime between " +
          "str_to_date(" + "'" + today + " 00:00:00" + "'" + ", '%Y-%m-%d %H:%i:%s') and str_to_date(" +
          "'" + today + " 23:59:59" + "', '%Y-%m-%d %H:%i:%s');")
print(sqlExp)
cur.execute(sqlExp)
datas = cur.fetchall()

conn.close()
print(datas)

cpuUseLst, memUseLst, RTIME = [], [], []

for eachRow in datas:
    cpuUse = eachRow['CPU_USE']
    memUse = eachRow['MEM_USE']
    rTime = str(eachRow['RTIME'])
    # sys.exit()
    cpuUseLst.append(cpuUse)
    memUseLst.append(memUse)
    RTIME.append(rTime)

# 使用pyecharts画图
(
    # 折线图对象
    Line(opts.InitOpts(
        bg_color="#1A1835",
    ))
        # 设置图形的全局参数
        .set_global_opts(

        tooltip_opts=opts.TooltipOpts(is_show=True),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(
                color='#90979c'
            )
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="rgba(204,187,225,0.5)"
                )
            ),
            splitline_opts=opts.SplitLineOpts(
                is_show=False
            ),
            axistick_opts=opts.AxisTickOpts(
                is_show=False
            )
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(
                is_show=True
            ),
            splitline_opts=opts.SplitLineOpts(
                is_show=False
            ),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="rgba(204,187,225,0.5)"
                )
            ),

        ),
        datazoom_opts=opts.DataZoomOpts(
            is_show=True,
        )
    )
        .add_xaxis(xaxis_data=RTIME)
        .add_yaxis(
        series_name="CPU使用率",
        y_axis=cpuUseLst,
        symbol="circle",
        symbol_size=10,
        is_symbol_show=True,
        label_opts=opts.LabelOpts(is_show=True),
        itemstyle_opts=opts.ItemStyleOpts(
            color="#6f7de3"
        ),
        markpoint_opts=opts.MarkPointOpts(
            label_opts=opts.LabelOpts(
                color='#fff'
            ),
            data=[opts.MarkPointItem(
                type_='max',
                name='最大值'
            ), opts.MarkPointItem(
                type_='min',
                name='最小值'
            )]
        )
    )
        .add_yaxis(
        series_name="内存使用率",
        y_axis=memUseLst,
        symbol="circle",
        symbol_size=10,
        is_symbol_show=True,
        label_opts=opts.LabelOpts(is_show=True),
        itemstyle_opts=opts.ItemStyleOpts(
            color="#c257F6"
        ),
        markpoint_opts=opts.MarkPointOpts(
            label_opts=opts.LabelOpts(
                color='#fff'
            ),
            data=[opts.MarkPointItem(
                type_='max',
                name='最大值'
            ), opts.MarkPointItem(
                type_='min',
                name='最小值'
            )]
        )
    )
        .render("sysmonitor.html")
)
