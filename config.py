# -*- coding: utf-8 -*-
"""
数据分析师岗位分析看板配置文件
"""

# 数据文件配置
DATA_FILE = 'DS_raw.csv'
DATA_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']

# 数据分析师岗位关键词
DS_KEYWORDS = ['数据分析', '数据挖掘', '数据科学', '商业分析', 'BI', '数据运营', '数据工程师']

# 异常值处理配置
OUTLIER_METHODS = ['iqr', 'zscore']
DEFAULT_OUTLIER_METHOD = 'iqr'
DEFAULT_OUTLIER_MULTIPLIER = 1.5

# 企业评分配置
SCORE_WEIGHTS = {
    '薪资评分': 25,
    '规模评分': 20,
    '头腰尾评分': 15,
    'DS团队评分': 15,
    '占比评分': 10,
    '稳定性评分': 15
}

# 头腰尾评分映射
HEAD_TAIL_SCORES = {'头': 15, '腰': 10, '尾': 5}

# 规模评分配置
OPTIMAL_SIZE_RANGE = (1000, 10000)  # 最优规模范围
OPTIMAL_RATIO_RANGE = (2, 8)  # 最优DS占比范围

# 图表配置
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# 页面配置
PAGE_CONFIG = {
    'page_title': '数据分析师岗位综合分析看板',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# 数据筛选配置
DEFAULT_FILTERS = {
    'max_industries': 10,
    'max_cities': 10,
    'default_remove_outliers': True
}

# 排名配置
RANKING_OPTIONS = {
    'top_n_options': [10, 20, 50, 100],
    'default_top_n': 20
}

# 导出配置
EXPORT_CONFIG = {
    'encoding': 'utf-8-sig',
    'date_format': '%Y%m%d_%H%M%S'
} 