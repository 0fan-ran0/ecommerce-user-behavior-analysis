import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="电商用户行为分析看板", layout="wide")
st.title("📊 电商用户行为 & RFM用户分层看板")

# ========= 1. 读取数据 =========
@st.cache_data
def load_data():
    # 原始行为数据（和notebook保持一致）
    columns = ['user_id', 'item_id', 'category_id', 'behavior_type', 'timestamp']
    df = pd.read_csv("../data/raw/UserBehavior.csv", names=columns)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['date'] = df['datetime'].dt.date
    start_date = pd.to_datetime('2017-11-25')
    end_date = pd.to_datetime('2017-12-04')
    df = df[(df['datetime'] >= start_date) & (df['datetime'] < end_date)]
    # RFM分层结果
    rfm_df = pd.read_csv("../data/processed/rfm_segment_result.csv")
    return df, rfm_df

df, rfm_df = load_data()

# ========= 2. 行为漏斗 =========
st.subheader("🔍 用户行为转化漏斗")
behavior_cnt = df['behavior_type'].value_counts()
pv = behavior_cnt.get("pv",0)
cart = behavior_cnt.get("cart",0)
fav = behavior_cnt.get("fav",0)
buy = behavior_cnt.get("buy",0)
funnel_df = pd.DataFrame({
    "阶段":["浏览","加购","收藏","购买"],
    "数量":[pv,cart,fav,buy]
})
st.dataframe(funnel_df, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("浏览→购买转化率", f"{buy/pv:.2%}")
col2.metric("加购收藏→购买转化率", f"{buy/(cart+fav):.2%}")
col3.metric("独立用户数", f"{df['user_id'].nunique():,}")

# ========= 3. 活跃时段分布 =========
st.subheader("⏰ 用户活跃时段分布")
hour_data = df.groupby("hour")["user_id"].nunique()
fig1, ax1 = plt.subplots(figsize=(10,4))
sns.barplot(x=hour_data.index, y=hour_data.values, ax=ax1)
ax1.set_xlabel("小时")
ax1.set_ylabel("独立用户数")
st.pyplot(fig1)

# ========= 4. RFM用户分层 =========
st.subheader("👥 RFM用户分层结果")
seg_data = rfm_df["user_segment"].value_counts()
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.barplot(x=seg_data.index, y=seg_data.values, ax=ax2)
ax2.tick_params(axis='x', rotation=30)
st.pyplot(fig2)

# ========= 5. 用户筛选器 =========
st.subheader("🎯 用户明细查询")
seg_select = st.selectbox("选择用户分层", rfm_df["user_segment"].unique())
filter_user = rfm_df[rfm_df["user_segment"] == seg_select]
st.dataframe(filter_user, use_container_width=True)
