import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.render import make_snapshot
import sqlite3
from snapshot_selenium import snapshot


db = "./db/sysStatus.db"
conn = sqlite3.connect(db)
cur = conn.cursor()
datas = cur.execute("select CPU_USE, MEM_USE, RTIME from MYSYS_STATUS").fetchall()
conn.close()
print(datas)

cpuUseLst, memUseLst, RTIME = zip(*datas)

print(cpuUseLst)
print(memUseLst)
print(RTIME)

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

# # 截图到本地
# lineChart = Line(opts.InitOpts(
#         bg_color="#1A1835",
#     )).set_global_opts(
#
#         tooltip_opts=opts.TooltipOpts(is_show=True),
#         legend_opts=opts.LegendOpts(
#             textstyle_opts=opts.TextStyleOpts(
#                 color='#90979c'
#             )
#         ),
#         xaxis_opts=opts.AxisOpts(
#             type_="category",
#             axisline_opts=opts.AxisLineOpts(
#                 linestyle_opts=opts.LineStyleOpts(
#                     color="rgba(204,187,225,0.5)"
#                 )
#             ),
#             splitline_opts=opts.SplitLineOpts(
#                 is_show=False
#             ),
#             axistick_opts=opts.AxisTickOpts(
#                 is_show=False
#             )
#         ),
#         yaxis_opts=opts.AxisOpts(
#             type_="value",
#             axistick_opts=opts.AxisTickOpts(
#                 is_show=True
#             ),
#             splitline_opts=opts.SplitLineOpts(
#                 is_show=False
#             ),
#             axisline_opts=opts.AxisLineOpts(
#                 linestyle_opts=opts.LineStyleOpts(
#                     color="rgba(204,187,225,0.5)"
#                 )
#             ),
#
#         ),
#         datazoom_opts=opts.DataZoomOpts(
#             is_show=True,
#         )
#     ).add_xaxis(xaxis_data=RTIME).add_yaxis(
#         series_name="CPU使用率",
#         y_axis=cpuUseLst,
#         symbol="circle",
#         symbol_size=10,
#         is_symbol_show=True,
#         label_opts=opts.LabelOpts(is_show=False),
#         itemstyle_opts=opts.ItemStyleOpts(
#             color="#6f7de3"
#         ),
#         markpoint_opts=opts.MarkPointOpts(
#             label_opts=opts.LabelOpts(
#                 color='#fff'
#             ),
#             data=[opts.MarkPointItem(
#                 type_='max',
#                 name='最大值'
#             ), opts.MarkPointItem(
#                 type_='min',
#                 name='最小值'
#             )]
#         )
#     ).add_yaxis(
#         series_name="内存使用率",
#         y_axis=memUseLst,
#         symbol="circle",
#         symbol_size=10,
#         is_symbol_show=True,
#         label_opts=opts.LabelOpts(is_show=False),
#         itemstyle_opts=opts.ItemStyleOpts(
#             color="#c257F6"
#         ),
#         markpoint_opts=opts.MarkPointOpts(
#             label_opts=opts.LabelOpts(
#                 color='#fff'
#             ),
#             data=[opts.MarkPointItem(
#                 type_='max',
#                 name='最大值'
#             ), opts.MarkPointItem(
#                 type_='min',
#                 name='最小值'
#             )]
#         )
#     )
#
#
# make_snapshot(snapshot, lineChart.render(), "systemInfo.png")