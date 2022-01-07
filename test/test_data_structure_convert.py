import pandas as pd
"""
# 测试资产、因子信息转换

格式1：
            　　　　　　　　　　　BP	　　　CFP	　　　EP	　　ILLIQUIDITY	REVS20	　　　SRMI	　　　VOL20
            date
            2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
            2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
            2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
            2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
            2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667

格式2：
    一个因子形如：
        date        stock       factor_value
        2012-06-24  000001.SH   0.1
        2012-06-27  000001.SH   0.5
        2012-06-24  000002.SH   0.12
        2012-06-27  000002.SH   0.56
        2012-06-24  000003.SH   0.123
        2012-06-27  000003.SH   0.567
"""

data1 = [
    ['000001.SZ','2016-06-24',0.165260,0.002198,0.085632,-0.078074,0.173832,0.214377,0.068445],
    ['000001.SZ','2016-06-27',0.165537,0.003583,0.063299,-0.048674,0.180890,0.202724,0.081748],
    ['000001.SZ','2016-06-28',0.135215,0.010403,0.059038,-0.034879,0.111691,0.122554,0.042489],
    ['000002.SH','2016-06-24',0.068774,0.019848,0.058476,-0.049971,0.042805,0.053339,0.079592],
    ['000002.SH','2016-06-27',0.039431,0.012271,0.037432,-0.027272,0.010902,0.077293,-0.050667],
    ['000002.SH','2016-06-28',0.039431,0.012271,0.037432,-0.027272,0.010902,0.077293,-0.050667],
    ['000002.SH','2016-06-29',0.039431,0.012271,0.037432,-0.027272,0.010902,0.077293,-0.050667]
]
data1 = pd.DataFrame(data1,columns=["code","datetime","BP","CFP","EP","ILLIQUIDITY","REVS20","SRMI","VOL20"])
data1 = data1.set_index(["code","datetime"])
print("数据：")
print(data1)
print("------------")
data1 = data1.stack()
print("列转成行：")
data1.index.names = ['trade_date','stock']
print(data1)
print("索引",data1.index.names)

print("------------------------------------------------------")
data2 = [
    ['2012-06-24','000001.SH', 0.1],
    ['2012-06-27','000001.SH', 0.5],
    ['2012-06-24','000002.SH', 0.12],
    ['2012-06-27','000002.SH', 0.56],
    ['2012-06-24','000003.SH', 0.123],
    ['2012-06-27','000003.SH', 0.567],
    ['2012-06-24','000004.SH', 0.1234],
]
data2 = pd.DataFrame(data2,columns=["trade_date","stock","factor"])
data2 = data2.set_index(["trade_date","stock"])
print("数据：")
print(data2)
print("索引",data2.index.names)
print("------------")
data2 = data2.iloc[:,0]# 把dataframe转成series，这样做，unstack的时候，就不会出现复合列名
data2 = data2.unstack()
print("unstack行转成列：(包含NAN)")
print(data2)
print("索引:",data2.index.names)
print("列名:",list(data2.columns))
print("------------")
print("再次，多列转成行by stack")
data2 = data2.stack()
print(data2)
print("索引:",data2.index.names)

# python test_data_structure_convert.py