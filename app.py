import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy_financial import pmt, fv, pv
from datetime import date

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
        
        # 新增投资模块
        st.markdown("### 🪙 一次性投资")
        initial_lump = st.number_input("初始一次性投资 (RM)", value=current_savings)
        num_extra_lumps = st.number_input("额外一次性投资次数", min_value=0, step=1, value=0)
        
        extra_lumps = []
        base_year = date.today().year
        for i in range(num_extra_lumps):
            col1, col2 = st.columns(2)
            amt = col1.number_input(f"金额 {i+1}", value=0.0, key=f"lump_amt_{i}")
            yr = col2.number_input(f"投资年份 {i+1}", 
                                 min_value=base_year, 
                                 max_value=base_year+100, 
                                 value=base_year, 
                                 key=f"lump_yr_{i}")
            extra_lumps.append((yr, amt))
        
        st.markdown("### 💸 每月定期投资")
        monthly_invest = st.number_input("每月投资金额 (RM)", value=0.0)
        monthly_start_date = st.date_input("开始日期", value=date.today())
        monthly_start_year = monthly_start_date.year
        monthly_start_month = monthly_start_date.month

    # 初始化关键变量
    total_need = 0.0
    monthly_save = 0.0
    final_gap = 0.0

    # 输入验证
    if retire_age <= current_age:
        st.error("错误：退休年龄必须大于当前年龄")
        return
    
    try:
        years_to_retire = retire_age - current_age
        real_return = (1 + return_rate) / (1 + inflation) - 1

        # 计算通胀调整后的需求
        annual_need_future = monthly_need * 12 * (1 + inflation)**years_to_retire
        total_need = -pv(real_return, retirement_years, annual_need_future)
        
        # 生成时间轴
        base_year = date.today().year
        calendar_years = np.arange(base_year, base_year + years_to_retire + 1)
        years = list(range(current_age, current_age + len(savings_projection)))
        
        # 初始化资产数组
        assets = initial_lump  # 包含初始一次性投资
        savings_projection = [assets]
        
        # 处理额外一次性投资
        lump_sum_dict = {yr: amt for yr, amt in extra_lumps}
        
        # 处理每月投资
        monthly_investments = {}
        current_year = base_year
        for yr in calendar_years:
            if yr >= monthly_start_year:
                months = 12 if yr > monthly_start_year else 12 - monthly_start_month + 1
                monthly_investments[yr] = monthly_invest * months
            else:
                monthly_investments[yr] = 0.0

        # 逐年计算资产增长
        for idx, calendar_year in enumerate(calendar_years):
            # 添加当年的一次性投资
            if calendar_year in lump_sum_dict:
                assets += lump_sum_dict[calendar_year]
                
            # 添加每月投资的年终值
            monthly_contribution = monthly_investments.get(calendar_year, 0.0)
            if monthly_contribution > 0:
                assets = fv(return_rate/12, 12, -monthly_invest, -assets)
            else:
                assets *= (1 + return_rate)
                
            savings_projection.append(assets)
        
        # 退休期计算
        current_assets = savings_projection[-1]
        for year in range(1, retirement_years + 1):
            annual_withdrawal = monthly_need * 12 * (1 + inflation)**year
            current_assets = current_assets * (1 + return_rate) - annual_withdrawal
            savings_projection.append(current_assets)
        
        # 创建DataFrame
        df = pd.DataFrame({
            "年龄": years,
            "累计资产": savings_projection[:len(years)],
            "退休需求": [0]*years_to_retire + [monthly_need*12*(1+inflation)**y for y in range(1, retirement_years+1)]
        })

        # 显示关键指标
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("退休时需准备资金", f"RM{total_need:,.0f}")
        with col2:
            st.metric("预测退休时资产", f"RM{savings_projection[years_to_retire]:,.0f}")
        with col3:
            adequacy_ratio = savings_projection[years_to_retire] / total_need
            status = "✅ 足够" if adequacy_ratio >= 1 else "⚠️ 不足"
            st.metric("资金充足率", f"{adequacy_ratio:.0%}", status)

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
        df_display['退休需求'] = df_display['退休需求'].apply(lambda x: f"RM{x:,.0f}" if x > 0 else "-")
        st.dataframe(df_display.set_index('年龄'), use_container_width=True)

        # 计算最终缺口
        final_gap = savings_projection[-1] - df['退休需求'].iloc[-1]
        
        # 显示警示信息
        if final_gap < 0:
            st.error(f"⚠️ 退休资金缺口: RM{-final_gap:,.0f}")
            st.write("**建议补救措施：**")
            st.write(f"1. 每月增加投资至少 RM{abs(final_gap/(years_to_retire*12)):,.0f}")
            st.write(f"2. 延迟退休年龄至 {retire_age + 2} 岁")
            st.write("3. 优化投资组合配置")

    except Exception as e:
        st.error(f"计算错误：{str(e)}")
        return

if __name__ == "__main__":
    calculate_retirement()
