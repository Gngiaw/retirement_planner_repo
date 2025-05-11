import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import altair as alt

st.set_page_config(page_title="Retirement Planner", layout="wide")

st.title("📊 Retirement & Investment Planner")

# User inputs
st.sidebar.header("Investor Info")
name = st.sidebar.text_input("Name", value="")
dob = st.sidebar.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())
contact = st.sidebar.text_input("Contact")

# Age Calculation
current_age = date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day))
ret_age = st.sidebar.number_input("Retirement Age", value=current_age+20, min_value=current_age+1)
years_to_retire = ret_age - current_age

# Financial Inputs
st.sidebar.header("Retirement Goals")
monthly_expenses = st.sidebar.number_input("Desired Monthly Income after Retirement (RM)", value=5000.0)
years_post = st.sidebar.number_input("Years to Live After Retirement", value=30)
annual_return_before = st.sidebar.number_input("Annual Return Before Retirement (%)", value=7.0) / 100
annual_return_after = st.sidebar.number_input("Annual Return After Retirement (%)", value=5.0) / 100
inflation = st.sidebar.number_input("Inflation Rate (%)", value=3.0) / 100
current_savings = st.sidebar.number_input("Current Savings (RM)", value=0.0)

# Monthly Savings Calculation
st.subheader("1. Required Monthly Savings")
months_to_save = years_to_retire * 12
months_retired = years_post * 12

# Adjust income to future value at retirement
desired_income_fv = monthly_expenses * ((1 + inflation) ** years_to_retire)

# PV of retirement withdrawals using annuity formula
r_post = annual_return_after / 12
retirement_needed = desired_income_fv * (1 - (1 + r_post) ** -months_retired) / r_post

# Calculate monthly contribution needed using future value formula
r_pre = annual_return_before / 12
factor = (1 + r_pre) ** months_to_save
monthly_saving = (retirement_needed - current_savings * factor) * r_pre / (factor - 1)

st.metric("Required Monthly Savings (RM)", f"{monthly_saving:,.2f}")


# Sensitivity Table
st.subheader("2. Sensitivity Table (Real Annual Returns)")
rates = np.arange(0.04, 0.13, 0.01)
df_sens = pd.DataFrame({'Year': np.arange(1, years_to_retire + 1)})
df_sens['Age'] = current_age + df_sens['Year']
df_sens['Calendar Year'] = date.today().year + df_sens['Year']

for rate in rates:
    real_rate = (1 + rate) / (1 + inflation) - 1
    bal = current_savings
    growth = []
    for year in range(1, years_to_retire + 1):
        bal = (bal + monthly_saving * 12) * (1 + real_rate)
        growth.append(bal)
    df_sens[f"{int(rate*100)}%"] = growth

st.dataframe(df_sens.style.format("{:.2f}"))

# Disposal of Invested Capital
st.subheader("3. Post-Retirement Capital Disposal")
start_balance = retirement_needed
withdrawals = []
balances = []
returns = []
bal = start_balance
annual_income = desired_income_fv

for year in range(1, years_post + 1):
    returns.append(bal * annual_return_after)
    withdrawals.append(annual_income)
    bal = bal * (1 + annual_return_after) - annual_income
    balances.append(bal)
    annual_income *= (1 + inflation)

df_dispose = pd.DataFrame({
    "Year": np.arange(1, years_post + 1),
    "Calendar Year": date.today().year + years_to_retire + np.arange(1, years_post + 1),
    "Age": current_age + years_to_retire + np.arange(1, years_post + 1),
    "Start Balance": [start_balance if i == 0 else balances[i-1] for i in range(len(balances))],
    "Returns": returns,
    "Withdrawal": withdrawals,
    "End Balance": balances
})

st.dataframe(df_dispose.style.format("{:.2f}"))

# Chart: Capital Depletion
st.subheader("4. Chart: Capital Depletion Over Time")
chart = alt.Chart(df_dispose).mark_line().encode(
    x=alt.X("Calendar Year:O", title="Year"),
    y=alt.Y("End Balance:Q", title="Balance (RM)")
).properties(
    width=700,
    height=400,
    title="Retirement Capital Depletion Over Time"
)
st.altair_chart(chart, use_container_width=True)
