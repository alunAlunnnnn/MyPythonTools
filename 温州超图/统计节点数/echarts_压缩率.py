import pyecharts.options as opts
from pyecharts.charts import Line

x_axis = ["原始数据", "图斑抽稀", "节点抽稀"]
y_data_tb = [0, 50.03, 50.03]
y_data_jd = [0, 26.62, 45.35]

c = (
    Line(
        init_opts=opts.InitOpts(width="800px", height="500px")
    )
    .add_xaxis(x_axis)
    .add_yaxis("图斑压缩率", y_data_tb, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    .add_yaxis("节点压缩率", y_data_jd, areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    .set_global_opts(title_opts=opts.TitleOpts(title="数据压缩率"))
    .render("jdcx.html")
)
