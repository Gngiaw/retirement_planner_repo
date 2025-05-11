# retirement_planner_app.py (Phase 1 with real rate, Phase 2 with real return columns)
import streamlit as st
from datetime import date
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retirement Planner", layout="wide")
st.title("💰 Retirement Planner")

phase1_tab, phase2_tab = st.tabs(["🧓 Phase 1 - Retirement Calculator", "📈 Phase 2 - Investment Projection"])

# --- PHASE 1 ---
with phase1_tab:
    st.subheader("User Inputs")
    name = st.text_input("Name", value="Your Name")
    dob = st.date_input("Date of Birth", value=date(1974, 1, 1))
    retire_age = st.number_input("Planned Retirement Age", value=60, min_value=40, max_value=80)
    monthly_spending = st.number_input("Desired Monthly Income After Retirement (RM)", value=5000.0)
    inflation_rate = st.number_input("Expected Annual Inflation Rate (%)", value=3.5) / 100
    return_rate = st.number_input("Expected Annual Return Rate (%)", value=7.0) / 100
    years_post_retire = st.number_input("Years You Expect to Live After Retirement", value=20)

    current_year = date.today().year
    current_age = current_year - dob.year
    years_until_retire = retire_age - current_age
    months_to_save = years_until_retire * 12

    fv = monthly_spending * 12 * years_post_retire
    pv_at_retirement = fv / ((1 + inflation_rate) ** years_until_retire)
    real_rate = (1 + return_rate) / (1 + inflation_rate) - 1
    real_monthly = real_rate / 12
    if real_rate > 0:
        monthly_saving = (pv_at_retirement * real_monthly) / (((1 + real_monthly) ** months_to_save) - 1)
    else:
        monthly_saving = pv_at_retirement / months_to_save

    st.subheader("👤 Profile")
    st.markdown(f"**Name:** {name}  \n**Current Age:** {current_age} yrs  \n**Retirement Age:** {retire_age} yrs  \n**Years to Retirement:** {years_until_retire} yrs")

    st.subheader("📊 Retirement Plan Summary")
    st.write(f"**Total Needed in Future (Future Value):** RM {fv:,.2f}")
    st.write(f"**Value Needed at Retirement (Present Value adjusted for inflation):** RM {pv_at_retirement:,.2f}")
    st.write(f"**Effective Real Annual Rate:** {real_rate * 100:.2f}%")
    st.write(f"**Required Monthly Savings (Real Rate Adjusted):** RM {monthly_saving:,.2f}")

# --- PHASE 2 ---
with phase2_tab:
    st.header("📈 Projected Investment Balance by Real Return Rates")
    base_year = current_year
    inflation_rate = st.number_input("Inflation Rate for Projection (%)", value=3.5) / 100
    return_rates = list(range(4, 13))

    st.markdown("### 🪙 Lump Sum Investments")
    initial_lump = st.number_input("Initial Lump Sum (RM)", value=0.0)
    num_extra_lumps = st.number_input("Number of Additional Lump Sums", min_value=0, step=1)
    extra_lumps = []
    for i in range(num_extra_lumps):
        col1, col2 = st.columns(2)
        amt = col1.number_input(f"Lump Sum {i+1} Amount", value=0.0, key=f"lump_amt_{i}")
        yr = col2.number_input(f"Year {i+1}", value=base_year, step=1, key=f"lump_yr_{i}")
        extra_lumps.append((yr, amt))

    st.markdown("### 💸 Monthly Investments")
    monthly_invest = st.number_input("Monthly Investment Amount (RM)", value=0.0)
    monthly_start_date = st.date_input("Start Date for Monthly Investment", value=date.today())
    monthly_start_year = monthly_start_date.year
    monthly_start_month = monthly_start_date.month

    calendar_years = np.arange(base_year, base_year + years_until_retire + 1)
    projections = pd.DataFrame({
        "Year": np.arange(1, years_until_retire + 2),
        "Age": current_age + np.arange(1, years_until_retire + 2),
        "Calendar Year": calendar_years
    })

    for r in return_rates:
        nominal = r / 100
        real = (1 + nominal) / (1 + inflation_rate) - 1
        balances = []
        balance = 0
        for y in calendar_years:
            yearly_contrib = 0
            if y == base_year:
                yearly_contrib += initial_lump
            yearly_contrib += sum(amt for yr, amt in extra_lumps if yr == y)
            if y == monthly_start_year:
                months = 12 - monthly_start_month + 1
                yearly_contrib += monthly_invest * months
            elif y > monthly_start_year:
                yearly_contrib += monthly_invest * 12
            balance = (balance + yearly_contrib) * (1 + real)
            balances.append(balance)
        projections[f"{r}%"] = balances

    st.subheader("📊 Projected Balance by Real Return Rates")
    st.dataframe(projections.style.format("{:.2f}"))

    chart_data = projections.melt(id_vars=["Calendar Year"], value_vars=[f"{r}%" for r in return_rates], var_name="Return Rate", value_name="Balance")
    chart = alt.Chart(chart_data).mark_line().encode(
        x="Calendar Year:O",
        y="Balance:Q",
        color="Return Rate:N"
    ).properties(title="Projected Real Return Investment Growth")
    st.altair_chart(chart, use_container_width=True)
