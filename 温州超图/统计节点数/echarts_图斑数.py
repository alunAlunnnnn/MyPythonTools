import pyecharts.options as opts
from pyecharts.charts import Bar, Line


colors = ["#5793f3", "#d14a61", "#675bba"]
x_data = ["原始", "图斑抽稀", "节点抽稀"]
x_data_line = ["原始图斑数", "图斑抽稀图斑数", "节点抽稀图斑数"]
legend_list = ["图斑数", "图斑数压缩率"]
evaporation_capacity = [
    413114,
    206667,
    206667,
]
rainfall_capacity = [
    4427424,
    3248868,
    2375176,
]

bar = (
    Bar(
        init_opts=opts.InitOpts(width="1460px", height="720px")
        # init_opts=opts.InitOpts(width="800px", height="500px")
    )
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(
        series_name="图斑数",
        y_axis=evaporation_capacity,
        yaxis_index=0,
        color=colors[1],
    )
    .add_yaxis(
        series_name="节点数",
        y_axis=rainfall_capacity,
        yaxis_index=1,
        color=colors[0],
    )
    .extend_axis(
        yaxis=opts.AxisOpts(
            name="图斑数",
            type_="value",
            min_=200000,
            max_=500000,
            position="right",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[1])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value} 个"),
        )
    ).extend_axis(
        yaxis=opts.AxisOpts(
            name="节点数",
            type_="value",
            min_=2000000,
            max_=5000000,
            position="left",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[0])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value} 个"),
        )
    )
    .set_global_opts(
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="节点数",
            # min_=200000,
            # max_=500000,
            position="right",
            offset=80,
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[0])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value} 个"),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
    )
)


bar.render("图斑数统计.html")
