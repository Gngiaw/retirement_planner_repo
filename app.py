# retirement_planner_app.py
import streamlit as st
from datetime import date, datetime
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retirement Planner", layout="wide")
st.title("💰 Retirement Planner & Investment Projection")

# Create tabs
phase1_tab, phase2_tab = st.tabs(["🧓 Phase 1 - Retirement Calculator", "📈 Phase 2 - Investment Projection"])

# --- PHASE 1 ---
with phase1_tab:
    st.header("1. Retirement Requirement Calculator")
    name = st.text_input("Name", value="Your Name")
    dob = st.date_input("Date of Birth", min_value=date(1940, 1, 1), max_value=date.today())
    retire_age = st.number_input("Planned Retirement Age", value=60, min_value=40, max_value=80)
    monthly_income = st.number_input("Desired Monthly Income After Retirement (RM)", value=5000.0)
    return_rate = st.number_input("Expected Annual Return Rate (%)", value=7.0) / 100
    inflation_rate = st.number_input("Expected Annual Inflation Rate (%)", value=3.5) / 100
    retirement_years = st.number_input("Years You Expect to Live After Retirement", value=20)

    current_age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
    years_to_retire = retire_age - current_age
    months_retired = retirement_years * 12
    real_annual_rate = (1 + return_rate) / (1 + inflation_rate) - 1
    real_monthly_rate = (1 + real_annual_rate) ** (1/12) - 1
    future_required = monthly_income * (1 - (1 + real_monthly_rate) ** -months_retired) / real_monthly_rate
    present_value = future_required / ((1 + real_annual_rate) ** years_to_retire)
    months_to_save = years_to_retire * 12
    growth_rate = return_rate / 12
    factor = (1 + growth_rate) ** months_to_save
    monthly_saving = (future_required * growth_rate) / (factor - 1)

    st.subheader("👤 Profile")
    st.markdown(f"**Name:** {name}  \n**Age:** {current_age} yrs  \n**Years to Retirement:** {years_to_retire} yrs")

    st.subheader("📊 Retirement Requirements")
    st.metric("Future Required at Retirement (RM)", f"{future_required:,.2f}")
    st.metric("Present Value Today (RM)", f"{present_value:,.2f}")
    st.metric("Required Monthly Savings (RM)", f"{monthly_saving:,.2f}")

# --- PHASE 2 ---
with phase2_tab:
    st.header("2. Projected Investment Balance by Return Rates")

    rates = list(range(4, 13))  # 4% to 12%
    base_year = date.today().year

    st.markdown("### 🪙 Lump Sum Investments")
    initial_lump = st.number_input("Initial Lump Sum (RM)", value=0.0)
    initial_year = base_year
    num_extra_lumps = st.number_input("Number of Additional Lump Sums", min_value=0, step=1)
    extra_lumps = []
    for i in range(int(num_extra_lumps)):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(f"Lump Sum {i+1} Amount", value=0.0, key=f"lump_amount_{i}")
        with col2:
            year = st.number_input(f"Year of Lump Sum {i+1}", value=base_year, step=1, key=f"lump_year_{i}")
        extra_lumps.append((year, amount))

    st.markdown("### 💸 Monthly Investments")
    monthly_invest = st.number_input("Monthly Investment Amount (RM)", value=0.0)
    monthly_start_year = st.number_input("Start Year for Monthly Investment", value=base_year, step=1)
    num_extra_monthlies = st.number_input("Number of Additional Monthly Investment Plans", min_value=0, step=1)
    extra_monthlies = []
    for i in range(int(num_extra_monthlies)):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(f"Monthly {i+1} Amount", value=0.0, key=f"month_amount_{i}")
        with col2:
            year = st.number_input(f"Monthly Start Year {i+1}", value=base_year, step=1, key=f"month_year_{i}")
        extra_monthlies.append((year, amount))

    # Generate investment projection table
    years = np.arange(0, years_to_retire + 1)
    ages = current_age + years
    calendar_years = base_year + years
    projections = pd.DataFrame({"Year": years, "Age": ages, "Calendar Year": calendar_years})

    for r in rates:
        rate = r / 100
        balances = []
        balance = 0
        for y in calendar_years:
            yearly_contrib = 0
            if y == initial_year:
                yearly_contrib += initial_lump
            yearly_contrib += sum(amt for yr, amt in extra_lumps if yr == y)
            yearly_contrib += (12 * monthly_invest if y >= monthly_start_year else 0)
            yearly_contrib += sum(12 * amt for yr, amt in extra_monthlies if y >= yr)
            balance = (balance + yearly_contrib) * (1 + rate)
            balances.append(balance)
        projections[f"{r}%"] = balances

    st.subheader("📈 Projected Balance by Net Return Rates")
    st.dataframe(projections.style.format("{:.2f}"))

    chart_data = projections.melt(id_vars=["Calendar Year"], value_vars=[f"{r}%" for r in rates], var_name="Return Rate", value_name="Balance")
    chart = alt.Chart(chart_data).mark_line().encode(
        x="Calendar Year:O",
        y="Balance:Q",
        color="Return Rate:N"
    ).properties(title="Projected Balance by Net Return Rates")

    st.altair_chart(chart, use_container_width=True)
