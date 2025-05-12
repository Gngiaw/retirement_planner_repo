import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy_financial import pmt, fv, pv

def calculate_retirement():
    st.set_page_config(page_title="退休规划系统", page_icon="💰", layout="wide")
    
    with st.sidebar:
        st.header("⚙️ 参数设置")
        current_age = st.number_input("当前年龄", min_value=18, max_value=100, value=51)
        retire_age = st.number_input("退休年龄", min_value=18, max_value=100, value=60)
        current_savings = st.number_input("当前储蓄 (RM)", min_value=0.0, value=300000.0)
        monthly_need = st.number_input("退休后每月需求 (RM)", min_value=0.0, value=5000.0)
        retirement_years = st.number_input("退休后生活年数", min_value=1, value=20)
        return_rate = st.slider("预期年回报率 (%)", 0.0, 15.0, 7.0) / 100
        inflation = st.slider("预期年通胀率 (%)", 0.0, 10.0, 3.5) / 100

    # 初始化关键变量
    total_need = 0.0
    monthly_save = 0.0
    final_gap = 0.0

    # 输入验证
    if retire_age <= current_age:
        st.error("错误：退休年龄必须大于当前年龄")
        return
    
    try:
        # 正确计算步骤
        years_to_retire = retire_age - current_age

        # 步骤1：计算退休时点的资金总需求（考虑退休期间的通胀）
        retirement_fund = 0
        for year in range(1, retirement_years + 1):
            annual_need = monthly_need * 12 * (1 + inflation)**year
            retirement_fund += annual_need / (1 + return_rate)**year

         # 步骤2：计算每月储蓄额
        monthly_save = pmt(return_rate/12, years_to_retire*12, 
                -current_savings, retirement_fund)

         # 步骤3：生成预测数据（分两个阶段）
         # 阶段一：储蓄期（退休前）
        for year in range(current_age, retire_age):
            assets = fv(return_rate, year-current_age, -monthly_save*12, -current_savings)
            needs = 0  # 退休前无支出需求
    
         # 阶段二：退休期
        for year in range(retire_age, retire_age + retirement_years):
            annual_withdrawal = monthly_need * 12 * (1 + inflation)**(year - retire_age)
            assets = assets * (1 + return_rate) - annual_withdrawal

         # 创建DataFrame
         df = pd.DataFrame({
             "年龄": years,
             "累计资产": savings_projection,
             "退休需求": needs_projection
         })
       
        # 显示关键指标
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("需要总储蓄", f"RM{total_need:,.0f}")
        with col2:
            st.metric("每月需储蓄", f"RM{monthly_save:,.0f}")
        with col3:
            st.metric("现有储蓄未来值", f"RM{fv(return_rate, years_to_retire, 0, -current_savings):,.0f}")

        # 绘制图表
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(df['年龄'], df['累计资产'], label='累计资产')
        ax.plot(df['年龄'], df['退休需求'], label='退休需求')
        ax.fill_between(df['年龄'], df['累计资产'], df['退休需求'], 
                       where=(df['累计资产'] >= df['退休需求']), 
                       interpolate=True, color='green', alpha=0.25)
        ax.fill_between(df['年龄'], df['累计资产'], df['退休需求'],
                       where=(df['累计资产'] < df['退休需求']),
                       interpolate=True, color='red', alpha=0.25)
        ax.set_xlabel("年龄")
        ax.set_ylabel("金额 (RM)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # 显示详细数据
        st.subheader("📊 详细预测表")
        df_display = df.copy()
        df_display['累计资产'] = df_display['累计资产'].apply(lambda x: f"RM{x:,.0f}")
        df_display['退休需求'] = df_display['退休需求'].apply(lambda x: f"RM{x:,.0f}")
        st.dataframe(df_display.set_index('年龄'), use_container_width=True)

        # 计算最终缺口
        final_gap = savings_projection[-1] - needs_projection[-1]

    except Exception as e:
        st.error(f"计算错误：{str(e)}")
        return

    # 显示警示信息
    if final_gap < 0:
        st.error(f"⚠️ 退休资金缺口: RM{-final_gap:,.0f}")
        st.write("**建议补救措施：**")
        st.write("1. 每月增加储蓄至少 RM{0:,.0f}".format(abs(monthly_save * 0.1)))
        st.write("2. 考虑延迟退休年龄至 {0} 岁".format(retire_age + 2))
        st.write("3. 调整投资组合至更高收益配置")

if __name__ == "__main__":
    calculate_retirement()
