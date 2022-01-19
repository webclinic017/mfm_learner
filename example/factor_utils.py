import logging

from sklearn import preprocessing

from utils import utils

logger = logging.getLogger(__name__)


def winsorize(se):
    """
    缩尾处理
    把分数为97.5%和2.5%之外的异常值替换成分位数值
    :param se:
    :return:
    """
    q = se.quantile([0.025, 0.975])
    """
    quantile：
        >>> s = pd.Series([1, 2, 3, 4])
        >>> s.quantile([.25, .5, .75])
        0.25    1.75
        0.50    2.50
        0.75    3.25    
    """
    if isinstance(q, pd.Series) and len(q) == 2:
        se[se < q.iloc[0]] = q.iloc[0]
        se[se > q.iloc[1]] = q.iloc[1]
    return se


def standardize(se):
    """标准化"""
    se_std = se.std()
    se_mean = se.mean()
    return (se - se_mean) / se_std


def fill_nan(se):
    return se.fillna(se.dropna().mean())


def proprocess(factors):
    print(factors)
    factors = factors.groupby(level='datetime').apply(fill_nan)  # 填充NAN
    factors = factors.groupby(level='datetime').apply(winsorize)  # 去极值
    factors = factors.groupby(level='datetime').apply(standardize)  # 标准化
    logger.debug("规范化预处理完因子，%d行", len(factors))
    return factors


# encoding=utf-8
# 数据处理

import numpy as np
import pandas as pd
from pandas import DataFrame


def to_panel_of_stock_columns(df):
    """
    从列为[日期|股票|值]，转换成，[日期|股票1|股票2|...|股票n]的panel数据
    从
        --------------------------------
        date        stock       value
        2012-06-24  000001.SH   0.1234
        2012-06-27  000001.SH   0.5678
        ...         ...         ...
        2012-06-24  000002.SH   0.5678
        ...         ...         ...
        --------------------------------
    转成
        ---------------------------------------------------------------------------------------------
        　　　　　　　000001.SZ	000002.SZ	000008.SZ	000009.SZ	000027.SZ	000039.SZ	000060.SZ
        date
        2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832	0.214377	0.068445
        2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890	0.202724	0.081748
        2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691	0.122554	0.042489
        2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805	0.053339	0.079592
        2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902	0.077293	-0.050667
        ---------------------------------------------------------------------------------------------

    的Panel数据
    """
    if type(df) == DataFrame:
        df = df.iloc[:, 0]  # 把dataframe转成series，这样做的缘故是，unstack的时候，可以避免复合列名，如 ['clv','003859.SH']
    df = df.unstack()
    return df


def fill_inf(df):
    return df.replace([np.inf, -np.inf], np.nan)


def fill_nan(df, by="no"):
    if by == "no": return df
    if by == "mean":
        return df.fill(df.mean())
    if by == "median":
        return df.fill(df.median())
    raise ValueError("无法识别的填充NAN的类型：" + by)


def zscore(df):
    """使用sklean的方法，归一化"""
    df.iloc[:, 0] = preprocessing.scale(df[:, 0])  # z-score 规范化
    return df


def _mask_df(df, mask):
    mask = mask.astype(bool)
    df[mask] = np.nan
    return df


def _mask_non_index_member(df, index_member=None):
    if index_member is not None:
        index_member = index_member.astype(bool)
        return _mask_df(df, ~index_member)
    return df


#
# # 横截面标准化 - 对Dataframe数据
# def standardize(factor_df, index_member=None):
#     """
#     对因子值做z-score标准化-算样本方差选择自由度为n-1
#     :param index_member:
#     :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
#                       形如:
#                                   　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
#                         date
#                         2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
#                         2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
#                         2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
#                         2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
#                         2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902
#     :return:z-score标准化后的因子值(pandas.Dataframe类型),index为datetime, colunms为股票代码。
#     """
#
#     factor_df = fill_inf(factor_df)
#     factor_df = _mask_non_index_member(factor_df, index_member)
#     return factor_df.sub(factor_df.mean(axis=1), axis=0).div(factor_df.std(axis=1), axis=0)


# # 横截面去极值 - 对Dataframe数据
# def winsorize(factor_df, alpha=0.05, index_member=None):
#     """
#     对因子值做去极值操作
#     :param index_member:
#     :param alpha: 极值范围
#     :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
#                       形如:
#                                   　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
#                         date
#                         2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
#                         2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
#                         2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
#                         2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
#                         2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902
#     :return:去极值后的因子值(pandas.Dataframe类型),index为datetime, colunms为股票代码。
#     """
#
#     def winsorize_series(se):
#         q = se.quantile([alpha / 2, 1 - alpha / 2])
#         se[se < q.iloc[0]] = q.iloc[0]
#         se[se > q.iloc[1]] = q.iloc[1]
#         return se
#
#     factor_df = fill_inf(factor_df)
#     factor_df = _mask_non_index_member(factor_df, index_member)
#     return factor_df.apply(lambda x: winsorize_series(x), axis=1)


# 横截面去极值 - 对Dataframe数据
def mad(factor_df, index_member=None):
    """
    对因子值做去极值操作
    :param index_member:
    :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
                      形如:
                                  　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
                        date
                        2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
                        2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
                        2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
                        2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
                        2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902
    :return:去极值后的因子值(pandas.Dataframe类型),index为datetime, colunms为股票代码。
    """

    def _mad(series):
        if series.dropna().size == 0:
            return series
        median = series.median()
        tmp = (series - median).abs().median()
        return series.clip(median - 5 * tmp, median + 5 * tmp)

    factor_df = fillinf(factor_df)
    factor_df = _mask_non_index_member(factor_df, index_member)
    return factor_df.apply(lambda x: _mad(x), axis=1)


def rank_with_mask(df, axis=1, mask=None, normalize=False, method='min'):
    """

    Parameters
    ----------
    df : pd.DataFrame
    axis : {0, 1}
    mask : pd.DataFrame
    normalize : bool
    method : {'min', 'average', 'max', 'dense'}

    Returns
    -------
    pd.DataFrame

    Notes
    -----
    If calculate rank, use 'min' method by default;
    If normalize, result will range in [0.0, 1.0]

    """
    not_nan_mask = (~df.isnull())

    if mask is None:
        mask = not_nan_mask
    else:
        mask = np.logical_and(not_nan_mask, mask)

    rank = df[mask].rank(axis=axis, na_option='keep', method=method)

    if normalize:
        dividend = rank.max(axis=axis)
        SUB = 1
        # for dividend = 1, do not subtract 1, otherwise there will be NaN
        dividend.loc[dividend > SUB] = dividend.loc[dividend > SUB] - SUB
        rank = rank.sub(SUB).div(dividend, axis=(1 - axis))
    return rank


# 横截面排序并归一化
def rank_standardize(factor_df, index_member=None):
    """
    输入因子值, 将因子用排序分值重构，并处理到0-1之间(默认为升序——因子越大 排序分值越大(越好)
        :param index_member:
        :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
                      形如:
                                  　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
                        date
                        2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
                        2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
                        2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
                        2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
                        2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902

    :return: 排序重构后的因子值。 取值范围在0-1之间
    """
    factor_df = fillinf(factor_df)
    factor_df = _mask_non_index_member(factor_df, index_member)
    return rank_with_mask(factor_df, axis=1, normalize=True)


def check_factor_format(df, index_type='date'):
    """
    index_type: 索引烈性，有两种格式：'date','date_code'
    烦死了，每次因子格式都不知道对不对，我写个函数来强制检查
    因子界面表示，有两种格式：
        格式1：索引是[date,code], 列是[value] ===> 对应 index_type='date'
        格式2：索引是[date], 列是[code1,code2,code3] ====> 对应 index_type='date_code'
    """
    index_num = 1 if index_type == 'date' else 2
    return len(df.index.names) == index_num


# 将因子值加一个极小的扰动项,用于对quantile做区分
def get_disturbed_factor(factor_df):
    """
    将因子值加一个极小的扰动项,用于对quantile区分
    :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
                      形如:
                                  　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
                        date
                        2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
                        2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
                        2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
                        2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
                        2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902

    :return: 重构后的因子值,每个值加了一个极小的扰动项。
    """
    return factor_df + np.random.random(factor_df.shape) / 1000000000


# 检查数据中是否含有任何缺失值
def is_any_nan(df):
    return df.isnull().values.any()


# 参考：https://mp.weixin.qq.com/s/WW3up8JwCIx0PwkpSx-oyg
def nan_sum(df):
    # 查看每列数据缺失值情况
    df.isnull().sum()


def nan_count(df, fields):
    # df[fields].
    pass


def pct_chg(prices, days=1):
    """
    计算收益率
    """
    return (prices.shift(-days) - prices) / prices  # 向后错days天


# 行业、市值中性化 - 对Dataframe数据，参考自jaqs_fxdayu代码
def neutralize(factor_df,
               group,
               float_mv=None,
               index_member=None):
    """
    对因子做行业、市值中性化，实际上是用市值来来做回归。
    因为有很多天数据，所以，这个F和X是一个[Days]的一个向量，回归出的e，是一个[days]的残差向量
    注意，在做行业中性化的时候，F实际上不是一个向量了，而是是一个行业宽度的一个矩阵[days,industies]，但是残差还是一个[days]向量
    -------------
    X = w * F + e
    X就是市值
    F为需要被市值中性化的因子
    e，就是去市值中性化后的结果，即，回归残差

    :param index_member:
    :param group:　行业分类(pandas.Dataframe类型),index为datetime, colunms为股票代码
                   行业分类（也可以是其他分组方式）。日期为索引,证券品种为columns的二维表格,对应每一个品种在某期所属的分类
                        date        code        industry
                        2016-06-24	000123.SH   23
                        2016-06-24	000124.SH   23
                        2016-06-24	000125.SH   22
                        2016-06-24	000126.SH   22
    :param factor_df: 因子值 (pandas.Dataframe类型),index为datetime, colunms为股票代码。
                      形如:
                        code       　AAPL	　　　     BA	　　　CMG	　　   DAL	      LULU	　　
                        date
                        2016-06-24	0.165260	0.002198	0.085632	-0.078074	0.173832
                        2016-06-27	0.165537	0.003583	0.063299	-0.048674	0.180890
                        2016-06-28	0.135215	0.010403	0.059038	-0.034879	0.111691
                        2016-06-29	0.068774	0.019848	0.058476	-0.049971	0.042805
                        2016-06-30	0.039431	0.012271	0.037432	-0.027272	0.010902
    :param float_mv: 流通市值因子(pandas.Dataframe类型),index为datetime, colunms为股票代码．为空则不进行市值中性化
    :return: 中性化后的因子值(pandas.Dataframe类型),index为datetime, colunms为股票代码。
    """

    def _ols_by_numpy(x, y):
        # least-squares，最小二乘，m是回归系数：y = m * x
        m = np.linalg.lstsq(x, y)[0]
        # 得到残差
        resid = y - (x @ m)
        return resid

    def _generate_cross_sectional_residual(data):
        """
        就是把industry，变成one-hot，然后和signal做多元回归，求残差
        --------------------------------------------------
        date        code        signal          industry
        2016-06-24	000123.SH   1.1             23
        2016-06-24	000124.SH   1.2             23
        2016-06-24	000125.SH   1.3             22
        2016-06-24	000126.SH   1.4             22
        :param data:
        :return:
        """
        for _, X in data.groupby(level=0):
            signal = X.pop("signal")  # pop这写法骚啊，就是单独取一列的意思，和X['pop']一个意思，不过，还包含了删除这列
            """
            pd.get_dummies(['A','B','A','C'])
               A  B  C
            0  1  0  0
            1  0  1  0
            2  1  0  0
            3  0  0  1
            """
            X = pd.concat([X, pd.get_dummies(X.pop("industry"))], axis=1)
            """
            signal(factor value因子值) = w1*0 + ... wi*1 + ... wn*0 + e
            我们用行业的one-hot作为x，去多元回归因子值y，剩余的残差e，就是我们需要的
            """
            signal = pd.Series(_ols_by_numpy(X.values, signal), index=signal.index, name=signal.name)
            # 靠，为何要用yield，看着晕，其实就是每行都处理的意思
            yield signal

    data = []

    # 准备因子数据
    assert check_factor_format(factor_df, index_type='date_code')
    assert len(factor_df.columns) == 1, factor_df.columns
    data.append(utils.dataframe2series(factor_df).rename("signal"))

    # 获取对数流动市值，并去极值、标准化。市值类因子不需进行这一步
    if float_mv is not None:
        float_mv = standardize(mad(np.log(float_mv), index_member=index_member), index_member).stack().rename("style")
        data.append(float_mv)

    # 行业中性化处理
    assert check_factor_format(group, index_type='date_code')
    assert len(group.columns) == 1
    industry_standard = utils.dataframe2series(group).rename("industry")
    data.append(industry_standard)
    data = pd.concat(data, axis=1).dropna()  # 按列(axis=1)合并，其实是贴到最后一列上，这里是把
    residuals = pd.concat(_generate_cross_sectional_residual(data))

    """"
    中性化结果：
    date      code
    20200102  300433.SZ   -5.551115e-17
              300498.SZ    0.000000e+00
              600000.SH    1.110223e-16
    """
    return residuals
