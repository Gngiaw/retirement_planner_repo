import streamlit as st
import numpy as np
import pandas as pd

from numpy_financial import pmt, fv, pv

def calculate_retirement():
    st.title("退休规划计算器 💰")
    
    with st.sidebar:
        st.header("输入参数")
        current_age = st.number_input("当前年龄", min_value=18, max_value=100, value=51)
        retire_age = st.number_input("退休年龄", min_value=18, max_value=100, value=60)
        current_savings = st.number_input("当前储蓄 (RM)", min_value=0.0, value=300000.0)
        monthly_need = st.number_input("退休后每月需求 (现值RM)", min_value=0.0, value=5000.0)
        retirement_years = st.number_input("退休后生活年数", min_value=1, value=20)
        return_rate = st.slider("预期年回报率 (%)", 0.0, 15.0, 7.0) / 100
        inflation = st.slider("预期年通胀率 (%)", 0.0, 10.0, 3.5) / 100

    # 输入验证
    if retire_age <= current_age:
        st.error("错误：退休年龄必须大于当前年龄")
        return
    
    years_to_retire = retire_age - current_age
    real_return = (1 + return_rate) / (1 + inflation) - 1  # 实际回报率

    # 计算退休时所需资金总额（考虑通胀）
    annual_need_future = monthly_need * 12 * (1 + inflation)**years_to_retire
    total_need = -pv(real_return, retirement_years, annual_need_future)

    # 计算每月储蓄金额
    monthly_save = pmt(return_rate/12, years_to_retire*12, -current_savings, total_need)

    # 生成预测数据
    years = list(range(current_age, retire_age + 1))
    savings_projection = []
    needs_projection = []
    
    for year in range(years_to_retire + 1):
        future_savings = fv(return_rate, year, -monthly_save*12, -current_savings)
        future_need = pv(inflation, years_to_retire - year, -annual_need_future)
        savings_projection.append(future_savings)
        needs_projection.append(future_need)

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
    st.subheader("详细预测")
    df_display = df.copy()
    df_display['累计资产'] = df_display['累计资产'].apply(lambda x: f"RM{x:,.0f}")
    df_display['退休需求'] = df_display['退休需求'].apply(lambda x: f"RM{x:,.0f}")
    st.dataframe(df_display.set_index('年龄'))

    # 显示警示信息
    final_gap = savings_projection[-1] - needs_projection[-1]
    if final_gap < 0:
        st.error(f"⚠️ 退休资金缺口: RM{-final_gap:,.0f}")
        st.write("建议措施：")
        st.write("- 增加每月储蓄至少RM{abs(monthly_save * 0.1):,.0f}")
        st.write("- 考虑延迟退休年龄")
        st.write("- 调整投资组合提高回报率")

if __name__ == "__main__":
    calculate_retirement()
