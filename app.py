# retirement_planner_app.py (multi-page structure)
import streamlit as st
from datetime import date, datetime
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retirement Planner", layout="wide")
st.sidebar.title("📂 App Navigation")
page = st.sidebar.radio("Go to", ["Retirement Calculator", "Investment Projection"])

# Shared variables
base_year = date.today().year
current_date = date.today()

if page == "Retirement Calculator":
    st.title("🧓 Retirement Calculator")

    name = st.text_input("Name", value="Your Name")
    dob = st.date_input("Date of Birth", min_value=date(1940, 1, 1), max_value=current_date)
    retire_age = st.number_input("Planned Retirement Age", value=60, min_value=40, max_value=80)
    monthly_income = st.number_input("Desired Monthly Income After Retirement (RM)", value=5000.0)
    return_rate = st.number_input("Expected Annual Return Rate (%)", value=7.0) / 100
    inflation_rate = st.number_input("Expected Annual Inflation Rate (%)", value=3.5) / 100
    retirement_years = st.number_input("Years You Expect to Live After Retirement", value=20)

    current_age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
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

elif page == "Investment Projection":
    st.title("📈 Investment Projection")

    rates = list(range(4, 13))
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
    monthly_start_date = st.date_input("Start Date for Monthly Investment", value=current_date)
    monthly_start_year = monthly_start_date.year
    monthly_start_month = monthly_start_date.month

    num_extra_monthlies = st.number_input("Number of Additional Monthly Investment Plans", min_value=0, step=1)
    extra_monthlies = []
    for i in range(int(num_extra_monthlies)):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(f"Monthly {i+1} Amount", value=0.0, key=f"month_amount_{i}")
        with col2:
            start_date = st.date_input(f"Start Date {i+1}", value=current_date, key=f"month_date_{i}")
        extra_monthlies.append((start_date.year, start_date.month, amount))

    # Project to retirement age
    years_to_retire = st.number_input("Years to Retirement (for Projection)", value=10, step=1)
    current_age = st.number_input("Current Age", value=50, step=1)
    calendar_years = np.arange(base_year, base_year + years_to_retire + 1)
    projections = pd.DataFrame({"Year": np.arange(0, years_to_retire + 1), "Age": current_age + np.arange(0, years_to_retire + 1), "Calendar Year": calendar_years})

    for r in rates:
        rate = r / 100
        balances = []
        balance = 0
        for y in calendar_years:
            yearly_contrib = 0
            if y == initial_year:
                yearly_contrib += initial_lump
            yearly_contrib += sum(amt for yr, amt in extra_lumps if yr == y)
            if y == monthly_start_year:
                months = 12 - monthly_start_month + 1
                yearly_contrib += monthly_invest * months
            elif y > monthly_start_year:
                yearly_contrib += monthly_invest * 12
            for (yr, mo, amt) in extra_monthlies:
                if y == yr:
                    months = 12 - mo + 1
                    yearly_contrib += amt * months
                elif y > yr:
                    yearly_contrib += amt * 12
            balance = (balance + yearly_contrib) * (1 + rate)
            balances.append(balance)
        projections[f"{r}%"] = balances

    st.subheader("📊 Projected Balance by Net Return Rates")
    st.dataframe(projections.style.format("{:.2f}"))

    chart_data = projections.melt(id_vars=["Calendar Year"], value_vars=[f"{r}%" for r in rates], var_name="Return Rate", value_name="Balance")
    chart = alt.Chart(chart_data).mark_line().encode(
        x="Calendar Year:O",
        y="Balance:Q",
        color="Return Rate:N"
    ).properties(title="Projected Balance by Net Return Rates")

    st.altair_chart(chart, use_container_width=True)
