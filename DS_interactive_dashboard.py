import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="数据分析师岗位综合分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        # 尝试不同的编码方式
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('DS_raw.csv', encoding=encoding)
                # 检查是否成功读取到数据
                if len(df) > 0 and len(df.columns) > 0:
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                st.warning(f"使用 {encoding} 编码时出错: {str(e)}")
                continue
        
        if df is None or len(df) == 0:
            st.error("无法读取数据文件，请检查文件编码")
            return None
        
        # 显示原始列名
        
        
        # 直接使用成功加载的数据，跳过编码检测
        
        
        # 标准化列名
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if '行业' in col or 'industry' in col_lower:
                column_mapping[col] = '行业'
            elif '岗位' in col or 'position' in col_lower or 'job' in col_lower:
                column_mapping[col] = '岗位'
            elif '公司' in col and '名称' in col:
                column_mapping[col] = '公司名称'
            elif '公司' in col and '主名' in col:
                column_mapping[col] = '公司主名'
            elif '员工' in col and '人数' in col:
                column_mapping[col] = '员工人数'
            elif '收入' in col and '年' in col:
                column_mapping[col] = '平均年收入'
            elif '在职' in col and '人数' in col:
                column_mapping[col] = '在职人数'
            elif '在职' in col and '天数' in col:
                column_mapping[col] = '平均在职天数'
            elif '头腰尾' in col:
                column_mapping[col] = '头腰尾'
            elif '城市' in col or 'city' in col_lower:
                column_mapping[col] = '城市'
            elif '规模' in col:
                column_mapping[col] = '规模'
            elif '企业' in col and '性质' in col:
                column_mapping[col] = '企业性质'
            elif '成立' in col and '日期' in col:
                column_mapping[col] = '成立日期'
            elif '工作' in col and '数' in col:
                column_mapping[col] = '平均工作数'
            elif '工商' in col and '类型' in col:
                column_mapping[col] = '企业工商类型'
        
        # 应用列名映射
        if column_mapping:
            df = df.rename(columns=column_mapping)
            
        
        # 显示处理后的列名
        
        
        # 检查必要的列是否存在
        required_columns = ['岗位', '行业']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"缺少必要的列: {missing_columns}")
            st.info("可用列: " + ", ".join(df.columns.tolist()))
            return None
        
        return df
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None

def detect_and_remove_outliers(df, column, method='iqr', multiplier=1.5, remove_outliers=True):
    """检测和移除异常值"""
    if column not in df.columns:
        return df
    
    # 转换为数值类型
    df[column] = pd.to_numeric(df[column], errors='coerce')
    
    # 移除0值和负值
    df = df[df[column] > 0]
    
    # 如果不进行异常值处理，直接返回
    if not remove_outliers:
        return df
    
    if method == 'iqr':
        # IQR方法
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        df_clean = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    elif method == 'zscore':
        # Z-score方法
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        df_clean = df[z_scores < multiplier]
    else:
        df_clean = df
    
    return df_clean

def filter_ds_jobs(df):
    """筛选数据分析师相关岗位"""
    ds_keywords = ['数据分析', '数据挖掘', '数据科学', '商业分析', 'BI', '数据运营', '数据工程师']
    ds_mask = df['岗位'].str.contains('|'.join(ds_keywords), na=False, case=False)
    return df[ds_mask].copy()

def create_salary_analysis(df_filtered, remove_outliers=True):
    """薪资分析"""
    if remove_outliers:
        df_salary = detect_and_remove_outliers(df_filtered, '平均年收入', remove_outliers=True)
    else:
        df_salary = detect_and_remove_outliers(df_filtered, '平均年收入', remove_outliers=False)
    
    if len(df_salary) == 0:
        return None, "没有有效的薪资数据"
    
    # 薪资分布图
    fig1 = px.histogram(
        df_salary, 
        x='平均年收入', 
        nbins=30,
        title='薪资分布直方图',
        labels={'平均年收入': '平均年收入（元）', 'count': '频次'}
    )
    fig1.add_vline(x=df_salary['平均年收入'].mean(), line_dash="dash", line_color="red",
                   annotation_text=f"平均值: {df_salary['平均年收入'].mean():.1f}")
    
    # 各行业平均薪资
    industry_salary = df_salary.groupby('行业')['平均年收入'].agg(['mean', 'count']).reset_index()
    industry_salary = industry_salary[industry_salary['count'] >= 3].sort_values('mean', ascending=False)
    
    fig2 = px.bar(
        industry_salary, 
        x='行业', 
        y='mean',
        title='各行业平均薪资',
        labels={'mean': '平均年收入（元）'},
        color='mean',
        color_continuous_scale='viridis'
    )
    fig2.update_xaxes(tickangle=45)
    
    # 薪资箱线图
    fig3 = px.box(
        df_salary, 
        y='平均年收入',
        title='薪资箱线图',
        labels={'平均年收入': '平均年收入（元）'}
    )
    
    return {
        'fig1': fig1,
        'fig2': fig2,
        'fig3': fig3,
        'stats': {
            'count': len(df_salary),
            'mean': df_salary['平均年收入'].mean(),
            'median': df_salary['平均年收入'].median(),
            'std': df_salary['平均年收入'].std(),
            'min': df_salary['平均年收入'].min(),
            'max': df_salary['平均年收入'].max()
        }
    }, None

def create_job_distribution_analysis(df_filtered, remove_outliers=True):
    """岗位分布分析"""
    if remove_outliers:
        df_jobs = detect_and_remove_outliers(df_filtered, '在职人数', remove_outliers=True)
    else:
        df_jobs = detect_and_remove_outliers(df_filtered, '在职人数', remove_outliers=False)
    
    if len(df_jobs) == 0:
        return None, "没有有效的岗位数据"
    
    # 岗位人数分布
    fig1 = px.histogram(
        df_jobs, 
        x='在职人数', 
        nbins=30,
        title='岗位人数分布',
        labels={'在职人数': '在职人数', 'count': '频次'}
    )
    fig1.add_vline(x=df_jobs['在职人数'].mean(), line_dash="dash", line_color="red",
                   annotation_text=f"平均值: {df_jobs['在职人数'].mean():.1f}")
    
    # 各行业岗位人数
    industry_jobs = df_jobs.groupby('行业')['在职人数'].agg(['sum', 'count']).reset_index()
    industry_jobs = industry_jobs[industry_jobs['count'] >= 3].sort_values('sum', ascending=False)
    
    fig2 = px.bar(
        industry_jobs, 
        x='行业', 
        y='sum',
        title='各行业总岗位人数',
        labels={'sum': '总岗位人数'},
        color='sum',
        color_continuous_scale='plasma'
    )
    fig2.update_xaxes(tickangle=45)
    
    # 平均岗位人数
    avg_jobs = df_jobs.groupby('行业')['在职人数'].mean().reset_index()
    avg_jobs = avg_jobs[avg_jobs['行业'].isin(industry_jobs['行业'])].sort_values('在职人数', ascending=False)
    
    fig3 = px.bar(
        avg_jobs, 
        x='行业', 
        y='在职人数',
        title='各行业平均岗位人数',
        labels={'在职人数': '平均岗位人数'},
        color='在职人数',
        color_continuous_scale='inferno'
    )
    fig3.update_xaxes(tickangle=45)
    
    return {
        'fig1': fig1,
        'fig2': fig2,
        'fig3': fig3,
        'stats': {
            'count': len(df_jobs),
            'total_jobs': df_jobs['在职人数'].sum(),
            'mean': df_jobs['在职人数'].mean(),
            'median': df_jobs['在职人数'].median(),
            'std': df_jobs['在职人数'].std()
        }
    }, None

def create_employee_ratio_analysis(df_filtered, remove_outliers=True):
    """员工占比分析"""
    # 计算占比
    df_ratio = df_filtered.copy()
    df_ratio['在职人数'] = pd.to_numeric(df_ratio['在职人数'], errors='coerce')
    df_ratio['员工人数'] = pd.to_numeric(df_ratio['员工人数'], errors='coerce')
    
    valid_ratio = df_ratio[(df_ratio['在职人数'] > 0) & (df_ratio['员工人数'] > 0)].copy()
    valid_ratio['DS占比'] = valid_ratio['在职人数'] / valid_ratio['员工人数'] * 100
    
    if remove_outliers:
        valid_ratio = detect_and_remove_outliers(valid_ratio, 'DS占比', remove_outliers=True)
    else:
        valid_ratio = detect_and_remove_outliers(valid_ratio, 'DS占比', remove_outliers=False)
    
    if len(valid_ratio) == 0:
        return None, "没有有效的占比数据"
    
    # 占比分布
    fig1 = px.histogram(
        valid_ratio, 
        x='DS占比', 
        nbins=30,
        title='数据分析师占比分布',
        labels={'DS占比': '占比（%）', 'count': '频次'}
    )
    fig1.add_vline(x=valid_ratio['DS占比'].mean(), line_dash="dash", line_color="red",
                   annotation_text=f"平均值: {valid_ratio['DS占比'].mean():.3f}%")
    
    # 各行业平均占比
    industry_ratio = valid_ratio.groupby('行业')['DS占比'].agg(['mean', 'count']).reset_index()
    industry_ratio = industry_ratio[industry_ratio['count'] >= 3].sort_values('mean', ascending=False)
    
    fig2 = px.bar(
        industry_ratio, 
        x='行业', 
        y='mean',
        title='各行业平均占比',
        labels={'mean': '平均占比（%）'},
        color='mean',
        color_continuous_scale='viridis'
    )
    fig2.update_xaxes(tickangle=45)
    
    # 占比与公司规模关系
    fig3 = px.scatter(
        valid_ratio, 
        x='员工人数', 
        y='DS占比',
        title='占比与公司规模关系',
        labels={'员工人数': '员工人数', 'DS占比': '占比（%）'},
        hover_data=['公司名称', '岗位']
    )
    fig3.update_xaxes(type="log")
    
    return {
        'fig1': fig1,
        'fig2': fig2,
        'fig3': fig3,
        'stats': {
            'count': len(valid_ratio),
            'mean_ratio': valid_ratio['DS占比'].mean(),
            'median_ratio': valid_ratio['DS占比'].median(),
            'max_ratio': valid_ratio['DS占比'].max(),
            'min_ratio': valid_ratio['DS占比'].min()
        }
    }, None

def calculate_company_scores(df_filtered):
    """计算企业综合评分"""
    if len(df_filtered) == 0:
        return None, "没有有效数据"
    
    # 数据预处理
    df = df_filtered.copy()
    df['平均年收入'] = pd.to_numeric(df['平均年收入'], errors='coerce')
    df['在职人数'] = pd.to_numeric(df['在职人数'], errors='coerce')
    df['员工人数'] = pd.to_numeric(df['员工人数'], errors='coerce')
    df['平均在职天数'] = pd.to_numeric(df['平均在职天数'], errors='coerce')
    
    # 计算DS占比
    df['DS占比'] = df['在职人数'] / df['员工人数'] * 100
    
    # 筛选有效数据
    valid_df = df[
        (df['平均年收入'] > 0) & 
        (df['在职人数'] > 0) & 
        (df['员工人数'] > 0) & 
        (df['平均在职天数'] > 0) &
        (df['DS占比'] <= 50)  # 排除异常值
    ].copy()
    
    if len(valid_df) == 0:
        return None, "没有有效的评分数据"
    
    # 1. 薪资评分 (0-25分)
    salary_75 = valid_df['平均年收入'].quantile(0.75)
    salary_25 = valid_df['平均年收入'].quantile(0.25)
    valid_df['薪资评分'] = np.where(
        valid_df['平均年收入'] >= salary_75,
        25,
        np.where(
            valid_df['平均年收入'] >= salary_25,
            15 + (valid_df['平均年收入'] - salary_25) / (salary_75 - salary_25) * 10,
            5 + (valid_df['平均年收入'] - valid_df['平均年收入'].min()) / (salary_25 - valid_df['平均年收入'].min()) * 10
        )
    )
    
    # 2. 公司规模评分 (0-20分)
    valid_df['规模评分'] = np.where(
        (valid_df['员工人数'] >= 1000) & (valid_df['员工人数'] <= 10000),
        20,
        np.where(
            valid_df['员工人数'] > 10000,
            15 + 5 * (1 - (valid_df['员工人数'] - 10000) / (valid_df['员工人数'].max() - 10000)),
            10 + 10 * (valid_df['员工人数'] / 1000)
        )
    )
    valid_df['规模评分'] = valid_df['规模评分'].clip(0, 20)
    
    # 3. 头腰尾评分 (0-15分)
    head_tail_scores = {'头部': 15, '腰部': 10, '尾部': 5}
    valid_df['头腰尾评分'] = valid_df['头腰尾'].map(head_tail_scores).fillna(7.5)
    
    # 4. DS团队规模评分 (0-15分)
    ds_team_75 = valid_df['在职人数'].quantile(0.75)
    ds_team_25 = valid_df['在职人数'].quantile(0.25)
    valid_df['DS团队评分'] = np.where(
        valid_df['在职人数'] >= ds_team_75,
        15,
        np.where(
            valid_df['在职人数'] >= ds_team_25,
            8 + (valid_df['在职人数'] - ds_team_25) / (ds_team_75 - ds_team_25) * 7,
            3 + (valid_df['在职人数'] - valid_df['在职人数'].min()) / (ds_team_25 - valid_df['在职人数'].min()) * 5
        )
    )
    
    # 5. DS占比评分 (0-10分)
    valid_df['占比评分'] = np.where(
        (valid_df['DS占比'] >= 2) & (valid_df['DS占比'] <= 8),
        10,
        np.where(
            valid_df['DS占比'] > 8,
            8 + 2 * (1 - (valid_df['DS占比'] - 8) / (valid_df['DS占比'].max() - 8)),
            5 + 5 * (valid_df['DS占比'] / 2)
        )
    )
    valid_df['占比评分'] = valid_df['占比评分'].clip(0, 10)
    
    # 6. 工作稳定性评分 (0-15分)
    days_75 = valid_df['平均在职天数'].quantile(0.75)
    days_25 = valid_df['平均在职天数'].quantile(0.25)
    valid_df['稳定性评分'] = np.where(
        valid_df['平均在职天数'] >= days_75,
        15,
        np.where(
            valid_df['平均在职天数'] >= days_25,
            8 + (valid_df['平均在职天数'] - days_25) / (days_75 - days_25) * 7,
            3 + (valid_df['平均在职天数'] - valid_df['平均在职天数'].min()) / (days_25 - valid_df['平均在职天数'].min()) * 5
        )
    )
    
    # 计算总分
    valid_df['综合评分'] = (valid_df['薪资评分'] + valid_df['规模评分'] + valid_df['头腰尾评分'] + 
                           valid_df['DS团队评分'] + valid_df['占比评分'] + valid_df['稳定性评分'])
    
    # 生成排名
    valid_df = valid_df.sort_values('综合评分', ascending=False).copy()
    valid_df['总排名'] = range(1, len(valid_df) + 1)
    valid_df['行业排名'] = valid_df.groupby('行业')['综合评分'].rank(ascending=False, method='dense').astype(int)
    
    return valid_df, None

def create_score_analysis(df_scored):
    """创建评分分析图表"""
    if len(df_scored) == 0:
        return None, "没有评分数据"
    
    # 前100名企业
    top_100 = df_scored.head(100)
    
    # 1. 综合评分分布
    fig1 = px.histogram(
        top_100, 
        x='综合评分', 
        nbins=20,
        title='前100名企业综合评分分布',
        labels={'综合评分': '综合评分', 'count': '企业数量'}
    )
    
    # 2. 各维度评分分布
    score_columns = ['薪资评分', '规模评分', '头腰尾评分', 'DS团队评分', '占比评分', '稳定性评分']
    avg_scores = top_100[score_columns].mean()
    
    fig2 = px.bar(
        x=score_columns,
        y=avg_scores.values,
        title='前100名企业各维度平均评分',
        labels={'x': '评分维度', 'y': '平均评分'},
        color=avg_scores.values,
        color_continuous_scale='viridis'
    )
    fig2.update_xaxes(tickangle=45)
    
    # 3. 行业分布
    industry_dist = top_100['行业'].value_counts().head(15)
    fig3 = px.bar(
        x=industry_dist.index,
        y=industry_dist.values,
        title='前100名企业行业分布',
        labels={'x': '行业', 'y': '企业数量'},
        color=industry_dist.values,
        color_continuous_scale='plasma'
    )
    fig3.update_xaxes(tickangle=45)
    
    # 4. 头腰尾分布
    head_tail_dist = top_100['头腰尾'].value_counts()
    fig4 = px.pie(
        values=head_tail_dist.values,
        names=head_tail_dist.index,
        title='前100名企业头腰尾分布'
    )
    
    # 5. 薪资vs综合评分散点图
    fig5 = px.scatter(
        top_100,
        x='平均年收入',
        y='综合评分',
        title='薪资与综合评分关系',
        labels={'平均年收入': '平均年收入（元）', '综合评分': '综合评分'},
        hover_data=['公司名称', '行业'],
        color='综合评分',
        color_continuous_scale='viridis'
    )
    
    # 6. 各行业平均综合评分
    industry_avg_score = df_scored.groupby('行业')['综合评分'].mean().sort_values(ascending=False).head(15)
    fig6 = px.bar(
        x=industry_avg_score.index,
        y=industry_avg_score.values,
        title='各行业平均综合评分',
        labels={'x': '行业', 'y': '平均综合评分'},
        color=industry_avg_score.values,
        color_continuous_scale='inferno'
    )
    fig6.update_xaxes(tickangle=45)
    
    return {
        'fig1': fig1,
        'fig2': fig2,
        'fig3': fig3,
        'fig4': fig4,
        'fig5': fig5,
        'fig6': fig6,
        'stats': {
            'total_companies': len(df_scored),
            'top_100_avg_score': top_100['综合评分'].mean(),
            'top_100_avg_salary': top_100['平均年收入'].mean(),
            'top_100_avg_size': top_100['员工人数'].mean(),
            'top_100_avg_team': top_100['在职人数'].mean(),
            'top_100_avg_ratio': top_100['DS占比'].mean(),
            'top_100_avg_days': top_100['平均在职天数'].mean()
        }
    }, None

def main():
    """主函数"""
    st.markdown('<h1 class="main-header">📊 数据分析师岗位综合分析看板</h1>', unsafe_allow_html=True)
    
    # 侧边栏配置
    st.sidebar.header("🔧 数据筛选设置")
    
    # 数据加载
    with st.spinner("正在加载数据..."):
        df = load_data()
    
    if df is None:
        st.error("数据加载失败，请检查数据文件")
        return
    
    # 基本信息
    st.sidebar.markdown("### 📋 数据概览")
    st.sidebar.metric("总记录数", f"{len(df):,}")
    
    # 筛选数据分析师岗位
    ds_df = filter_ds_jobs(df)
    st.sidebar.metric("数据分析师岗位", f"{len(ds_df):,}")
    st.sidebar.metric("占比", f"{len(ds_df)/len(df)*100:.1f}%")
    
    # 异常值处理设置
    st.sidebar.markdown("### 🧹 异常值处理")
    remove_outliers = st.sidebar.checkbox("自动去除异常值", value=True)
    outlier_method = st.sidebar.selectbox(
        "异常值检测方法",
        ["iqr", "zscore"],
        help="IQR: 四分位距方法，Z-score: 标准差方法"
    )
    
    # 数据筛选
    st.sidebar.markdown("### 🎯 数据筛选")
    
    # 行业筛选
    industries = sorted(df['行业'].dropna().unique())
    selected_industries = st.sidebar.multiselect(
        "选择行业",
        industries,
        default=industries[:10] if len(industries) > 10 else industries
    )
    
    # 城市筛选
    cities = sorted(df['城市'].dropna().unique())
    selected_cities = st.sidebar.multiselect(
        "选择城市",
        cities,
        default=cities[:10] if len(cities) > 10 else cities
    )
    
    # 头腰尾筛选
    head_tail_options = sorted(df['头腰尾'].dropna().unique())
    selected_head_tail = st.sidebar.multiselect(
        "选择头腰尾",
        head_tail_options,
        default=head_tail_options
    )
    
    # 应用筛选
    filtered_df = df.copy()
    if selected_industries:
        filtered_df = filtered_df[filtered_df['行业'].isin(selected_industries)]
    if selected_cities:
        filtered_df = filtered_df[filtered_df['城市'].isin(selected_cities)]
    if selected_head_tail:
        filtered_df = filtered_df[filtered_df['头腰尾'].isin(selected_head_tail)]
    
    # 筛选后的数据分析师岗位
    filtered_ds_df = filter_ds_jobs(filtered_df)
    
    # 显示筛选结果
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("筛选后总记录", f"{len(filtered_df):,}")
    with col2:
        st.metric("筛选后DS岗位", f"{len(filtered_ds_df):,}")
    with col3:
        st.metric("DS岗位占比", f"{len(filtered_ds_df)/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")
    with col4:
        st.metric("筛选比例", f"{len(filtered_df)/len(df)*100:.1f}%")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💰 薪资分析", "👥 岗位分布", "📊 员工占比", "🏆 企业评分", "📈 其他维度", "📋 数据明细"])
    
    with tab1:
        st.header("💰 薪资分析")
        
        if len(filtered_ds_df) > 0:
            salary_analysis, error = create_salary_analysis(filtered_ds_df, remove_outliers)
            
            if error:
                st.warning(error)
            else:
                # 显示统计信息
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("有效数据", f"{salary_analysis['stats']['count']:,}")
                with col2:
                    st.metric("平均薪资", f"{salary_analysis['stats']['mean']:.1f}")
                with col3:
                    st.metric("中位数", f"{salary_analysis['stats']['median']:.1f}")
                with col4:
                    st.metric("标准差", f"{salary_analysis['stats']['std']:.1f}")
                with col5:
                    st.metric("最低薪资", f"{salary_analysis['stats']['min']:.1f}")
                with col6:
                    st.metric("最高薪资", f"{salary_analysis['stats']['max']:.1f}")
                
                # 显示图表
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(salary_analysis['fig1'], use_container_width=True)
                with col2:
                    st.plotly_chart(salary_analysis['fig3'], use_container_width=True)
                
                st.plotly_chart(salary_analysis['fig2'], use_container_width=True)
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")
    
    with tab2:
        st.header("👥 岗位分布分析")
        
        if len(filtered_ds_df) > 0:
            job_analysis, error = create_job_distribution_analysis(filtered_ds_df, remove_outliers)
            
            if error:
                st.warning(error)
            else:
                # 显示统计信息
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("有效数据", f"{job_analysis['stats']['count']:,}")
                with col2:
                    st.metric("总岗位人数", f"{job_analysis['stats']['total_jobs']:,}")
                with col3:
                    st.metric("平均岗位人数", f"{job_analysis['stats']['mean']:.1f}")
                with col4:
                    st.metric("中位数", f"{job_analysis['stats']['median']:.1f}")
                with col5:
                    st.metric("标准差", f"{job_analysis['stats']['std']:.1f}")
                
                # 显示图表
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(job_analysis['fig1'], use_container_width=True)
                with col2:
                    st.plotly_chart(job_analysis['fig3'], use_container_width=True)
                
                st.plotly_chart(job_analysis['fig2'], use_container_width=True)
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")
    
    with tab3:
        st.header("📊 员工占比分析")
        
        if len(filtered_ds_df) > 0:
            ratio_analysis, error = create_employee_ratio_analysis(filtered_ds_df, remove_outliers)
            
            if error:
                st.warning(error)
            else:
                # 显示统计信息
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("有效数据", f"{ratio_analysis['stats']['count']:,}")
                with col2:
                    st.metric("平均占比", f"{ratio_analysis['stats']['mean_ratio']:.3f}%")
                with col3:
                    st.metric("中位数占比", f"{ratio_analysis['stats']['median_ratio']:.3f}%")
                with col4:
                    st.metric("最高占比", f"{ratio_analysis['stats']['max_ratio']:.3f}%")
                with col5:
                    st.metric("最低占比", f"{ratio_analysis['stats']['min_ratio']:.3f}%")
                
                # 显示图表
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(ratio_analysis['fig1'], use_container_width=True)
                with col2:
                    st.plotly_chart(ratio_analysis['fig2'], use_container_width=True)
                
                st.plotly_chart(ratio_analysis['fig3'], use_container_width=True)
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")
    
    with tab4:
        st.header("🏆 企业评分")
        
        if len(filtered_ds_df) > 0:
            # 计算企业评分
            df_scored, error = calculate_company_scores(filtered_ds_df)
            
            if error:
                st.warning(error)
            else:
                # 显示评分分析
                score_analysis, error = create_score_analysis(df_scored)
                
                if error:
                    st.warning(error)
                else:
                    # 显示统计信息
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    with col1:
                        st.metric("有效数据", f"{score_analysis['stats']['total_companies']:,}")
                    with col2:
                        st.metric("前100名平均综合评分", f"{score_analysis['stats']['top_100_avg_score']:.1f}")
                    with col3:
                        st.metric("前100名平均薪资", f"{score_analysis['stats']['top_100_avg_salary']:.1f}")
                    with col4:
                        st.metric("前100名平均公司规模", f"{score_analysis['stats']['top_100_avg_size']:.0f}人")
                    with col5:
                        st.metric("前100名平均团队规模", f"{score_analysis['stats']['top_100_avg_team']:.0f}人")
                    with col6:
                        st.metric("前100名平均DS占比", f"{score_analysis['stats']['top_100_avg_ratio']:.3f}%")
                    
                    # 显示图表
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(score_analysis['fig1'], use_container_width=True)
                    with col2:
                        st.plotly_chart(score_analysis['fig2'], use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(score_analysis['fig3'], use_container_width=True)
                    with col2:
                        st.plotly_chart(score_analysis['fig4'], use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(score_analysis['fig5'], use_container_width=True)
                    with col2:
                        st.plotly_chart(score_analysis['fig6'], use_container_width=True)
                    
                    # 企业排名榜单
                    st.subheader("📊 企业排名榜单")
                    
                    # 排名筛选选项
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        rank_type = st.selectbox(
                            "排名类型",
                            ["总排名", "行业排名"],
                            help="选择查看总排名或行业排名"
                        )
                    with col2:
                        top_n = st.selectbox(
                            "显示前N名",
                            [10, 20, 50, 100],
                            help="选择显示前多少名企业"
                        )
                    with col3:
                        selected_industry = st.selectbox(
                            "选择行业（仅行业排名时有效）",
                            ["全部"] + sorted(df_scored['行业'].unique().tolist()),
                            help="选择特定行业查看排名"
                        )
                    
                    # 筛选数据
                    if rank_type == "总排名":
                        display_df = df_scored.head(top_n)
                        title = f"综合评分前{top_n}名企业"
                    else:  # 行业排名
                        if selected_industry == "全部":
                            display_df = df_scored[df_scored['行业排名'] <= top_n].head(top_n * 3)
                            title = f"各行业前{top_n}名企业"
                        else:
                            industry_df = df_scored[df_scored['行业'] == selected_industry].copy()
                            display_df = industry_df.head(top_n)
                            title = f"{selected_industry}行业前{top_n}名企业"
                    
                    # 显示排名表格
                    st.write(f"**{title}**")
                    
                    # 选择显示的列
                    display_columns = [
                        '总排名', '行业排名', '公司名称', '行业', '头腰尾', 
                        '平均年收入', '员工人数', '在职人数', 'DS占比', 
                        '薪资评分', '规模评分', '头腰尾评分', 'DS团队评分', '占比评分', '稳定性评分', '综合评分'
                    ]
                    
                    # 格式化数据
                    display_data = display_df[display_columns].copy()
                    display_data['平均年收入'] = display_data['平均年收入'].round(0).astype(int)
                    display_data['员工人数'] = display_data['员工人数'].round(0).astype(int)
                    display_data['在职人数'] = display_data['在职人数'].round(0).astype(int)
                    display_data['DS占比'] = display_data['DS占比'].round(3)
                    display_data['综合评分'] = display_data['综合评分'].round(2)
                    
                    # 重命名列
                    column_mapping = {
                        '总排名': '总排名',
                        '行业排名': '行业排名',
                        '公司名称': '公司名称',
                        '行业': '行业',
                        '头腰尾': '头腰尾',
                        '平均年收入': '平均年收入（元）',
                        '员工人数': '员工人数',
                        '在职人数': '在职人数',
                        'DS占比': 'DS占比（%）',
                        '薪资评分': '薪资评分',
                        '规模评分': '规模评分',
                        '头腰尾评分': '头腰尾评分',
                        'DS团队评分': 'DS团队评分',
                        '占比评分': '占比评分',
                        '稳定性评分': '稳定性评分',
                        '综合评分': '综合评分'
                    }
                    display_data = display_data.rename(columns=column_mapping)
                    
                    # 显示表格
                    st.dataframe(
                        display_data,
                        use_container_width=True,
                        height=400
                    )
                    
                    # 下载按钮
                    csv = display_data.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label=f"📥 下载{title}数据",
                        data=csv,
                        file_name=f'{title}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv'
                    )
                    
                    # 评分维度说明
                    st.subheader("📋 评分维度说明")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **评分维度权重：**
                        - 薪资评分：25分 (25%)
                        - 公司规模评分：20分 (20%)
                        - 头腰尾评分：15分 (15%)
                        - DS团队规模评分：15分 (15%)
                        - DS占比评分：10分 (10%)
                        - 工作稳定性评分：15分 (15%)
                        - **总分：100分**
                        """)
                    with col2:
                        st.markdown("""
                        **评分标准：**
                        - 薪资评分：基于薪资分位数计算
                        - 规模评分：1000-10000人规模得分最高
                        - 头腰尾评分：头(15分)、腰(10分)、尾(5分)
                        - DS团队评分：基于团队规模分位数计算
                        - 占比评分：2-8%占比得分最高
                        - 稳定性评分：基于在职天数分位数计算
                        """)
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")
    
    with tab5:
        st.header("📈 其他分析维度")
        
        if len(filtered_ds_df) > 0:
            # 公司规模分析
            st.subheader("🏢 公司规模分析")
            valid_size = filtered_ds_df[pd.to_numeric(filtered_ds_df['员工人数'], errors='coerce') > 0]
            
            if len(valid_size) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("有效规模数据", f"{len(valid_size):,}")
                with col2:
                    avg_size = valid_size['员工人数'].astype(float).mean()
                    st.metric("平均公司规模", f"{avg_size:.0f}人")
                with col3:
                    median_size = valid_size['员工人数'].astype(float).median()
                    st.metric("中位数规模", f"{median_size:.0f}人")
                
                # 公司规模分布
                size_data = valid_size['员工人数'].astype(float)
                fig_size = px.histogram(
                    x=size_data,
                    nbins=30,
                    title='公司规模分布',
                    labels={'x': '员工人数', 'y': '频次'}
                )
                fig_size.update_xaxes(type="log")
                st.plotly_chart(fig_size, use_container_width=True)
            
            # 头腰尾分布
            st.subheader("🏆 头腰尾分布")
            head_tail_dist = filtered_ds_df['头腰尾'].value_counts()
            fig_head_tail = px.pie(
                values=head_tail_dist.values, 
                names=head_tail_dist.index,
                title='头腰尾分布'
            )
            st.plotly_chart(fig_head_tail, use_container_width=True)
            
            # 城市分布
            st.subheader("🌆 城市分布")
            city_dist = filtered_ds_df['城市'].value_counts()
            fig_city = px.bar(
                x=city_dist.index, 
                y=city_dist.values,
                title='城市分布',
                labels={'x': '城市', 'y': '岗位数量'}
            )
            fig_city.update_xaxes(tickangle=45)
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")
    
    with tab6:
        st.header("📋 数据明细")
        
        if len(filtered_ds_df) > 0:
            # 数据下载
            csv = filtered_ds_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载筛选后的数据",
                data=csv,
                file_name=f'数据分析师岗位数据_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
            
            # 显示数据表格
            st.subheader("数据预览")
            st.dataframe(
                filtered_ds_df,
                use_container_width=True,
                height=400
            )
            
            # 数据统计
            st.subheader("数据统计")
            st.write(filtered_ds_df.describe())
        else:
            st.warning("筛选条件下没有数据分析师岗位数据")

if __name__ == "__main__":
    main() 
