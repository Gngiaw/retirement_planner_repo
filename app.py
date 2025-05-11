# retirement_planner_app.py (Phase 2 restored Lump Sum + Monthly investment)
import streamlit as st
from datetime import date, datetime
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Retirement Planner", layout="wide")
st.title("💰 Retirement Planner & Investment Projection")

phase1_tab, phase2_tab = st.tabs(["🧓 Phase 1 - Retirement Calculator", "📈 Phase 2 - Investment Projection"])

# --- Shared session state ---
def init_session():
    defaults = {
        "name": "Your Name",
        "dob": date(1970, 1, 1),
        "retire_age": 60,
        "monthly_income": 5000.0,
        "return_rate": 7.0,
        "inflation_rate": 3.5,
        "retirement_years": 20,
        "monthly_saving": 0.0,
        "future_required": 0.0,
        "monthly_invest": 0.0,
        "monthly_start_date": date.today(),
        "initial_lump": 0.0,
        "extra_lumps": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# --- PHASE 1 ---
with phase1_tab:
    st.header("1. Retirement Requirement Calculator")
    st.session_state['name'] = st.text_input("Name", value=st.session_state['name'])
    st.session_state['dob'] = st.date_input("Date of Birth", value=st.session_state['dob'])
    st.session_state['retire_age'] = st.number_input("Planned Retirement Age", value=st.session_state['retire_age'], min_value=40, max_value=80)
    st.session_state['monthly_income'] = st.number_input("Desired Monthly Income After Retirement (RM)", value=st.session_state['monthly_income'])
    st.session_state['return_rate'] = st.number_input("Expected Annual Return Rate (%)", value=st.session_state['return_rate'])
    st.session_state['inflation_rate'] = st.number_input("Expected Annual Inflation Rate (%)", value=st.session_state['inflation_rate'])
    st.session_state['retirement_years'] = st.number_input("Years You Expect to Live After Retirement", value=st.session_state['retirement_years'])

    current_date = date.today()
    dob = st.session_state['dob']
    current_age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
    years_to_retire = st.session_state['retire_age'] - current_age
    months_retired = st.session_state['retirement_years'] * 12
    return_rate = st.session_state['return_rate'] / 100
    inflation_rate = st.session_state['inflation_rate'] / 100
    real_annual_rate = (1 + return_rate) / (1 + inflation_rate) - 1
    real_monthly_rate = (1 + real_annual_rate) ** (1/12) - 1

    future_required = st.session_state['monthly_income'] * (1 - (1 + real_monthly_rate) ** -months_retired) / real_monthly_rate
    present_value = future_required / ((1 + real_annual_rate) ** years_to_retire)
    months_to_save = years_to_retire * 12
    growth_rate = return_rate / 12
    factor = (1 + growth_rate) ** months_to_save
    monthly_saving = (future_required * growth_rate) / (factor - 1)

    st.session_state['monthly_saving'] = monthly_saving
    st.session_state['future_required'] = future_required

    st.subheader("👤 Profile")
    st.markdown(f"**Name:** {st.session_state['name']}  \n**Age:** {current_age} yrs  \n**Years to Retirement:** {years_to_retire} yrs")

    st.subheader("📊 Retirement Requirements")
    st.metric("Future Required at Retirement (RM)", f"{future_required:,.2f}")
    st.metric("Present Value Today (RM)", f"{present_value:,.2f}")
    st.metric("Required Monthly Savings (RM)", f"{monthly_saving:,.2f}")

# --- PHASE 2 ---
with phase2_tab:
    st.header("2. Projected Investment Balance by Return Rates")
    rates = list(range(4, 13))
    base_year = date.today().year

    st.markdown("### 🪙 Lump Sum Investments")
    st.session_state['initial_lump'] = st.number_input("Initial Lump Sum (RM)", value=st.session_state['initial_lump'])
    num_extra_lumps = st.number_input("Number of Additional Lump Sums", value=len(st.session_state['extra_lumps']), min_value=0, step=1)

    extra_lumps = []
    for i in range(num_extra_lumps):
        col1, col2 = st.columns(2)
        with col1:
            amt = st.number_input(f"Lump Sum {i+1} Amount", key=f"lump_amt_{i}", value=0.0)
        with col2:
            yr = st.number_input(f"Lump Sum {i+1} Year", key=f"lump_yr_{i}", value=base_year, step=1)
        extra_lumps.append((yr, amt))
    st.session_state['extra_lumps'] = extra_lumps

    st.markdown("### 💸 Monthly Investments")
    st.session_state['monthly_invest'] = st.number_input("Monthly Investment Amount (RM)", value=st.session_state['monthly_invest'])
    st.session_state['monthly_start_date'] = st.date_input("Start Date for Monthly Investment", value=st.session_state['monthly_start_date'])
    monthly_start_year = st.session_state['monthly_start_date'].year
    monthly_start_month = st.session_state['monthly_start_date'].month

    calendar_years = np.arange(base_year, base_year + years_to_retire + 1)
    projections = pd.DataFrame({
        "Year": np.arange(1, years_to_retire + 1),
        "Age": current_age + np.arange(1, years_to_retire + 1),
        "Calendar Year": calendar_years[1:]
    })

    result_summary = []
    for r in rates:
        rate = r / 100
        balances = []
        balance = 0
        for y in calendar_years:
            yearly_contrib = 0
            if y == base_year:
                yearly_contrib += st.session_state['initial_lump']
            yearly_contrib += sum(amt for yr, amt in st.session_state['extra_lumps'] if yr == y)
            if y == monthly_start_year:
                months = 12 - monthly_start_month + 1
                yearly_contrib += st.session_state['monthly_invest'] * months
            elif y > monthly_start_year:
                yearly_contrib += st.session_state['monthly_invest'] * 12
            balance = (balance + yearly_contrib) * (1 + rate)
            balances.append(balance)
        projections[f"{r}%"] = balances[1:]
        result_summary.append((r, balances[-1]))

    st.subheader("📊 Projected Balance by Net Return Rates")
    st.dataframe(projections.style.format("{:.2f}"))

    chart_data = projections.melt(id_vars=["Calendar Year"], value_vars=[f"{r}%" for r in rates], var_name="Return Rate", value_name="Balance")
    chart = alt.Chart(chart_data).mark_line().encode(
        x="Calendar Year:O",
        y="Balance:Q",
        color="Return Rate:N"
    ).properties(title="Projected Balance by Net Return Rates")
    st.altair_chart(chart, use_container_width=True)

    st.subheader("🎯 Retirement Goal Comparison")
    for rate, final_value in result_summary:
        surplus = final_value - st.session_state['future_required']
        status = "✅ Exceeds goal" if surplus >= 0 else "⚠️ Below goal"
        st.write(f"**{rate}% Return:** Final = RM {final_value:,.2f} | Target = RM {st.session_state['future_required']:,.2f} → {status} (Diff: RM {surplus:,.2f})")
