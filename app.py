import streamlit as st
import pandas as pd
import numpy as np
from numpy_financial import pmt, fv, pv
from datetime import date

st.set_page_config(page_title="Retirement Planner", layout="wide")

st.title("📊 Welcome to Your Retirement & Investment Planner")
st.markdown("This personalized tool helps you **project your future** and plan **financial freedom** with confidence.")
st.image(
    "https://providencefinancialinc.com/wp-content/uploads/2012/11/bigstock-Retirement-Ahead-8148597.jpg",
    caption="Plan your retirement with peace of mind",
    use_container_width=True
)



# — SIDEBAR: Investor Details —
st.sidebar.header("Investor Details")
name = st.sidebar.text_input("Name", value="")
dob = st.sidebar.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())
contact = st.sidebar.text_input("Contact")

# compute ages
today = date.today()
current_age = today.year - dob.year
ret_age = st.sidebar.number_input(
    "Retirement Age (years old)",
    value=current_age + 10, min_value=current_age, step=1
)
years_to_retire = ret_age - current_age

# — SIDEBAR: Calculator Settings —
st.sidebar.header("Calculator Settings")
gross_pct = st.sidebar.number_input(
    "Expected Annual Return Rate (%)",
    value=7.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f"
)
gross_return_rate = gross_pct / 100
inflation_pct = st.sidebar.number_input(
    "Expected Annual Inflation Rate (%)",
    value=3.0, min_value=0.0, max_value=100.0, step=0.1, format="%.1f"
)
inflation_rate = inflation_pct / 100

real_return = (1 + gross_return_rate) / (1 + inflation_rate) - 1

# — SIDEBAR: Post-Retirement Planning —
st.sidebar.header("Post-Retirement Planning")
monthly_expenses = st.sidebar.number_input("Desired Monthly Income after Retirement (RM)", min_value=0.0, value=5000.0)

years_post = st.sidebar.number_input(
    "Years to Live After Retirement", value=20, min_value=1, step=1
)


# 计算通胀调整后的需求
annual_need_future = monthly_expenses * 12 * (1 + inflation_rate)**years_to_retire
future_required = -pv(real_return, years_post, annual_need_future)

# — SIDEBAR: Pre-Retirement Investments —
st.sidebar.header("Pre-Retirement Investments")
first_lump = st.sidebar.number_input(
    "First Lump Sum Amount (RM)", value=0.0, step=100.0, format="%.2f"
)
first_lump_date = st.sidebar.date_input(
    "Date of First Lump Sum", value=today, min_value=today
)

num_additional = st.sidebar.number_input(
    "Number of Additional Lump Sums", value=0, min_value=0, step=1
)
additional_amts = []
additional_dts = []
for i in range(int(num_additional)):
    amt = st.sidebar.number_input(
        f"Additional Lump Sum #{i+2} Amount (RM)",
        value=0.0, step=100.0, format="%.2f", key=f"add_amt_{i}"
    )
    dt = st.sidebar.date_input(
        f"Date of Additional Lump Sum #{i+2}",
        value=today, min_value=today, key=f"add_dt_{i}"
    )
    additional_amts.append(amt)
    additional_dts.append(dt)

monthly_invest = st.sidebar.number_input(
    "Monthly Invest Amount (RM)", value=0.0, step=100.0, format="%.2f"
)
monthly_start = st.sidebar.date_input(
    "Monthly Invest Start Date", value=today, min_value=today
)

num_add_month = st.sidebar.number_input(
    "Number of Additional Monthly Investments", value=0, min_value=0, step=1
)
additional_month_amts = []
additional_month_dts = []
for j in range(int(num_add_month)):
    m_amt = st.sidebar.number_input(
        f"Additional Monthly Invest #{j+1} Amount (RM)",
        value=0.0, step=100.0, format="%.2f", key=f"add_mon_amt_{j}"
    )
    m_dt = st.sidebar.date_input(
        f"Date of Additional Monthly Invest #{j+1}",
        value=today, min_value=today, key=f"add_mon_dt_{j}"
    )
    additional_month_amts.append(m_amt)
    additional_month_dts.append(m_dt)

# — SIDEBAR: Longevity Test — 
st.sidebar.header("Money Longevity Test")
manual_start = st.sidebar.number_input(
    "Starting Capital (RM)",
    value=float(future_required),
    step=1000.0,
    format="%.2f"
)
manual_withdraw = st.sidebar.number_input(
    "Annual Withdrawal (RM)",
    value=float(monthly_expenses * 12),
    step=1000.0,
    format="%.2f"
)
manual_pct = st.sidebar.number_input(
    "Annual Gross Return Rate (%)",
    value=7.0, min_value=0.0, max_value=100.0, step=0.5, format="%.1f"
)
gross_growrate = manual_pct / 100

manual_ipct = st.sidebar.number_input(
    "Inflaction Rate (%)",
    value=3.5, min_value=0.0, max_value=100.0, step=0.5, format="%.1f"
)
gross_irate = manual_ipct / 100

max_years = st.sidebar.number_input(
    "Max Years to Simulate",
    value=50,
    min_value=1,
    step=1
)

savings_projection = []
years = list(range(current_age, ret_age + years_post))
for year in range(years_to_retire + 1):
    future_savings = fv(gross_return_rate, year, -monthly_inves*12, -first_lump)   
    savings_projection.append(future_savings)
   
# — MAIN PAGE —
st.title("📊 Retirement & Investment Planner")
st.markdown(f"**Name:** {name}")
st.markdown(f"**DOB:** {dob.strftime('%d %b %Y')}  **Age:** {current_age} yrs")
st.markdown(f"**Contact:** {contact}")
st.markdown(f"**Expected Gross Return Rate:** {gross_return_rate:.1%}")
st.markdown(f"**Expected Inflation Rate:** {inflation_rate:.1%}")
st.markdown(f"**Years to Retirement:** {years_to_retire} yrs")
st.write("---")
# key metrics
col1, col2 = st.columns(2)
col1.metric("预测退休时资产", f"RM{savings_projection[years_to_retire]:,.0f}")
col2.metric("Future Required at Retirement (RM)", f"{future_required:,.0f}")
col3, col4 = st.columns(2)
col3.metric("First Lump Date", first_lump_date.strftime('%d %b %Y'))
col4.metric("Monthly Invest Start", monthly_start.strftime('%d %b %Y'))
st.write("---")

# — CALCULATE REQUIRED MONTHLY SAVINGS —
st.subheader("Required Monthly Savings to Meet Future Goal")
net_monthly = (gross_return_rate - inflation_rate) / 12
months = years_to_retire * 12
if net_monthly != 0:
    req_month = future_required * net_monthly / ((1 + net_monthly)**months - 1)
else:
    req_month = future_required / months
st.metric("Required Monthly Savings (RM)", f"{req_month:,.2f}")
st.write("---")

# — SENSITIVITY TABLE —
st.subheader("Projected Balance by Net Return Rates")
rates = np.arange(0.04, 0.13, 0.01)
start_year = first_lump_date.year

df_sens = pd.DataFrame({'Year': np.arange(1, years_to_retire+1)})
# Add Age and Calendar Year columns
df_sens['Age'] = current_age + df_sens['Year']
df_sens['Calendar Year'] = today.year + df_sens['Year']
for rate in rates:
    net_annual = rate - inflation_rate
    balances = []
    bal = 0.0
    for y in df_sens['Year']:
        current_year = start_year + y - 1
        # lumpsums
        year_lumps = 0.0
        if y == 1 and first_lump_date.year == start_year:
            year_lumps += first_lump
        for dt, amt in zip(additional_dts, additional_amts):
            if dt.year == current_year:
                year_lumps += amt
        # base monthly
        if y == 1:
            months_base = 13 - monthly_start.month
        else:
            months_base = 12
        base_annuity = monthly_invest * months_base
        # additional monthly streams
        add_annuity = 0.0
        for mdt, mamt in zip(additional_month_dts, additional_month_amts):
            if mdt.year < current_year:
                months_add = 12
            elif mdt.year == current_year:
                months_add = 13 - mdt.month
            else:
                months_add = 0
            add_annuity += mamt * months_add
        principal = bal + year_lumps + base_annuity + add_annuity
        bal = principal * (1 + net_annual)
        balances.append(bal)
    df_sens[f"{int(rate*100)}%"] = balances
# format Year, Age, Calendar Year as integers and rates as 2-decimal floats
fmt = {col: "{:.2f}" for col in df_sens.columns if col.endswith('%')}
fmt.update({"Year":"{:.0f}", "Age":"{:.0f}", "Calendar Year":"{:.0f}"})
styled = df_sens.style.format(fmt).set_properties(**{'text-align':'center'})
st.dataframe(styled)   

# — CHART: Projected Balance by Net Return Rates —
# index by Calendar Year so the x-axis shows the actual year numbers
import altair as alt

proj_chart = df_sens[["Calendar Year"] + [f"{r}%" for r in range(4, 13)]]
proj_chart_melted = proj_chart.melt(id_vars="Calendar Year", var_name="Return Rate", value_name="Balance")

chart = alt.Chart(proj_chart_melted).mark_line().encode(
    x=alt.X("Calendar Year:O", title="Year", axis=alt.Axis(format='d')),  # 'O' treats as ordinal to avoid decimals
    y=alt.Y("Balance:Q", title="Balance (RM)"),
    color="Return Rate:N"
).properties(
    title="Projected Balance by Net Return Rates",
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# — DISPOSAL OF INVESTED CAPITAL —
st.subheader("Disposal of Invested Capital")

start_balance   = future_required
annual_withdraw = monthly_expenses * 12
net_annual      = gross_return_rate - inflation_rate
Retirement_age  = ret_age
Retirement_year = today.year + years_to_retire

years, starts, returns, withdraws, ends = [], [], [], [], []
bal = start_balance

for y in range(1, int(years_post) + 1):
    years.append(y)
    starts.append(bal)

    ret = bal * net_annual
    returns.append(ret)

    wd = annual_withdraw * ((1 + inflation_rate) ** (years_to_retire))
    withdraws.append(wd)

    end_bal = bal + ret - wd
    ends.append(end_bal)

    bal = end_bal

# Build DataFrame with Year, Age, Calendar Year, plus your columns
df_disp = pd.DataFrame({
    "Year":           years,
    "Age":            [Retirement_age + y for y in years],
    "Calendar Year":  [Retirement_year + y for y in years],
    "Start Balance":  starts,
    "Returns":        returns,
    "Withdrawal":     withdraws,
    "End Balance":    ends
})

# Formatting & display
disp_fmt = {
    "Year":          "{:.0f}",
    "Age":           "{:.0f}",
    "Calendar Year": "{:.0f}",
    "Start Balance": "{:,.2f}",
    "Returns":       "{:,.2f}",
    "Withdrawal":    "{:,.2f}",
    "End Balance":   "{:,.2f}"
}

st.dataframe(
    df_disp
      .style
      .format(disp_fmt)
      .set_properties(**{"text-align":"center"}),
    width=800
)

# — CHART: Depletion Over Time —
# Add Calendar Year and Age columns first
df_disp["Calendar Year"] = today.year + years_to_retire + df_disp["Year"]
df_disp["Age"] = current_age + years_to_retire + df_disp["Year"]

# Now build the chart
chart = alt.Chart(df_disp).mark_line(color="red").encode(
    x=alt.X("Calendar Year:O", title="Year", axis=alt.Axis(format="d")),
    y=alt.Y("End Balance:Q", title="End Balance (RM)")
).properties(
    title="Post-Retirement Disposal End Balance",
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# — HOW LONG WILL YOUR MONEY LAST? —
st.subheader("How Long Will Your Money Last?")
start_balances, returns_l, withdrawals_l, end_balances, years_l = [], [], [], [], []

bal2 = manual_start
net_ret = gross_growrate - gross_irate
year = 1

while bal2 > 0 and year <= max_years:
    years_l.append(year)
    start_balances.append(bal2)
    
    # 1) earn return
    r = bal2 * net_ret
    returns_l.append(r)
    
    # 2) withdraw
    w = manual_withdraw * ((1 + gross_irate) ** (years_to_retire))
    withdrawals_l.append(w)
    
    # 3) new ending balance
    end_b = bal2 + r - w
    end_balances.append(end_b)
    
    # 4) next
    bal2 = end_b
    year += 1

df_longevity = pd.DataFrame({
    "Year":         years_l,
    "Start Balance": start_balances,
    "Returns":      returns_l,
    "Withdrawal":   withdrawals_l,
    "End Balance":  end_balances
})

longevity_fmt = {
    "Year":          "{:.0f}",
    "Start Balance": "{:,.2f}",
    "Returns":       "{:,.2f}",
    "Withdrawal":    "{:,.2f}",
    "End Balance":   "{:,.2f}"
}

st.dataframe(
    df_longevity
      .style
      .format(longevity_fmt)
      .set_properties(**{"text-align":"center"}),
    width=800
)

# — CHART: Longevity Simulation —
df_longevity["Calendar Year"] = today.year + years_to_retire + df_longevity["Year"]
df_longevity["Age"] = current_age + years_to_retire + df_longevity["Year"]

chart = alt.Chart(df_longevity).mark_line(color="green").encode(
    x=alt.X("Calendar Year:O", title="Year", axis=alt.Axis(format="d")),
    y=alt.Y("End Balance:Q", title="End Balance (RM)")
).properties(
    title="Money Longevity Simulation",
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# — LEGEND —
with st.expander("🗒 Legend (raw sheet)"):
    st.dataframe(df_legend)

# — FULL PDF EXPORT WITH ALL CHARTS & TABLES —
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

st.subheader("📄 Download Full Multi‑Chart & Table PDF Report")

if st.button("Download All Charts & Tables as PDF"):
    # 1) Create charts into buffers
    buf_sens = BytesIO()
    fig1, ax1 = plt.subplots(figsize=(6, 3))
    for r in [f"{i}%" for i in range(4,13)]:
        df_sens.plot(x="Year", y=r, ax=ax1, legend=True)
    ax1.set_title("Projected Balance by Net Return Rates")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Balance (RM)")
    ax1.xaxis.get_major_locator().set_params(integer=True)  # <- this is the fix
    fig1.tight_layout()
    fig1.savefig(buf_sens, format="PNG")
    buf_sens.seek(0)


    # Disposal Chart
    buf_disp = BytesIO()
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    df_disp.plot(x="Year", y="End Balance", ax=ax2, legend=False, color="red")
    ax2.set_title("Post‑Retirement Disposal End Balance")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("End Balance (RM)")
    ax2.xaxis.get_major_locator().set_params(integer=True)
    fig2.tight_layout()
    fig2.savefig(buf_disp, format="PNG")
    buf_disp.seek(0)


    # Longevity Chart
    buf_lon = BytesIO()
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    df_longevity.plot(x="Year", y="End Balance", ax=ax3, legend=False, color="green")
    ax3.set_title("Money Longevity Simulation")
    ax3.set_xlabel("Year")
    ax3.set_ylabel("End Balance (RM)")
    ax3.xaxis.get_major_locator().set_params(integer=True)
    fig3.tight_layout()
    fig3.savefig(buf_lon, format="PNG")
    buf_lon.seek(0)


    # 2) Build PDF story
    pdf_buf = BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Investor Info
    story.append(Paragraph("<b>Retirement & Investment Full Report</b>", styles["Title"]))
    story.append(Spacer(6, 32))
    info = [
        f"<b>Name</b>: {title} {name}",
        f"<b>DOB</b>: {dob.strftime('%d %b %Y')}   <b>Age</b>: {current_age}",
        f"<b>Retirement Age</b>: {ret_age},   <b>Years to Retire</b>: {years_to_retire}",
        f"<b>Expected Return Rate</b>: {gross_pct:.1f}%   <b>Inflation Rate</b>: {inflation_pct:.1f}%",
        f"<b>Experted Monthly Income after Retirement (RM)</b>: {monthly_expenses:,.0f}",
        f"<b>Total Required at Retirement (RM)</b>: {future_required:,.0f}",
        f"<b>Required Monthly Savings to Meet The Goal (RM)</b>: {req_month:,.0f}"       
   ]
    for line in info:
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(4, 10))

    story.append(Spacer(4, 32))

    story.append(Paragraph("<b>Lump Sum Investment $$</b>", styles["Title"]))
    story.append(Spacer(6, 22))
    info = [
       f'<font color="blue"><b>“Lump sum is a powerful way to grow your wealth faster for a long-term goal.”</b></font>'
   ]
    if first_lump > 0:           
           info.append(f"<b>First Lump Sum (RM)</b>: {first_lump:,.0f}, <b>First Lunp Sum (Date)</b>: {first_lump_date.strftime('%d %b %Y')}")
    else:
           info.append("<b>First Lump Sum (RM)</b>: None")

    if num_additional > 0:
            for i in range(num_additional):
                amt = additional_amts[i]
                dt = additional_dts[i]
                info.append(f"<b>Additional Lump Sums (#)</b>: {num_additional:,.0f}")
                info.append(f"<b>Additional Lump Sum #{i+2} (RM)</b>: {amt:,.0f}, <b>Date</b>: {dt.strftime('%d %b %Y')}")
    else:
           info.append("<b>Additional Lump Sums</b>: None")
    for line in info:
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(4, 10))

    story.append(Spacer(4, 32))
    story.append(Paragraph("<b>Monthly Investment (RSP) $$ </b>", styles["Title"]))
    story.append(Spacer(6, 22))

    info = [
        f'<font color="blue"><b>“RSP is a smart, stress-free way to grow your wealth over time — even if you’re just starting out.”</b></font>'
   ]
    if monthly_invest > 0:           
           info.append(f"<b>Monthly Invest:RSP (RM)</b>: {monthly_invest:,.0f}, <b>Monthly Invest:RSP (Date)</b>: {monthly_start.strftime('%d %b %Y')}")
    else:
           info.append("<b>Monthly Invest:RSP (RM)</b>: None")

    if num_add_month > 0:
            for i in range(num_add_month):
                m_amt = additional_month_amts[i]
                m_dt = additional_month_dts[i]
                info.append(f"<b>Additional Monthly Investments (#)</b>: {num_add_month:,.0f}")
                info.append(f"<b>Additional Monthly Invest #{i+2} (RM)</b>: {m_amt:,.0f}, <b>Date</b>: {m_dt.strftime('%d %b %Y')}")
    else:
           info.append("<b>Additional Monthly Invest</b>: None")
    for line in info:
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(4, 10))
    story.append(PageBreak())

    # Sensitivity Chart + Table
    story.append(Paragraph("<b>1. Sensitivity: Projected Balances</b>", styles["Heading2"]))
    story.append(Image(buf_sens, width=450, height=200))
    story.append(Spacer(1, 12))
    sens_cols = df_sens.columns.tolist()
    sens_table = [sens_cols]
    for _, row in df_sens.iterrows():
        rowvals = []
        for col in sens_cols:
            if col in ["Year", "Age", "Calendar Year"]:
                rowvals.append(str(int(row[col])))
            else:
                rowvals.append(f"{row[col]:,.0f}")
        sens_table.append(rowvals)
    tbl1 = Table(sens_table, repeatRows=1, colWidths=[30] + [30] + [60] + [50]*(len(sens_cols)-1))
    tbl1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTSIZE",(0,0),(-1,-1),8),
    ]))
    story.append(tbl1)
    story.append(PageBreak())

    # Disposal Chart + Table
    story.append(Paragraph("<b>2. Post Retirement Disposal</b>", styles["Heading2"]))
    story.append(Image(buf_disp, width=450, height=200))
    story.append(Spacer(1, 12))

    disp_table = [["Year", "Calendar Year", "Age", "Start Balance", "Returns", "Withdrawal", "End Balance"]]
    for _, row in df_disp.iterrows():
        disp_table.append([
            str(int(row["Year"])),
            str(int(row["Calendar Year"])),
            str(int(row["Age"])),
            f"{row['Start Balance']:,.0f}",
            f"{row['Returns']:,.0f}",
            f"{row['Withdrawal']:,.0f}",
            f"{row['End Balance']:,.0f}"
        ])
    tbl2 = Table(disp_table, repeatRows=1, colWidths=[50, 60, 50, 80, 80, 80, 80])
    tbl2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ]))
    story.append(tbl2)
    story.append(PageBreak())

    # Longevity Chart + Table
    story.append(Paragraph("<b>3. Money Longevity Simulation</b>", styles["Heading2"]))
    story.append(Image(buf_lon, width=450, height=200))
    story.append(Spacer(1, 12))

    # Full header with 7 columns (including Calendar Year & Age)
    lon_table = [["Year", "Calendar Year", "Age", "Start Balance", "Returns", "Withdrawal", "End Balance"]]
    for _, row in df_longevity.iterrows():
        lon_table.append([
            str(int(row["Year"])),
            str(int(row["Calendar Year"])),
            str(int(row["Age"])),
            f"{row['Start Balance']:,.0f}",
            f"{row['Returns']:,.0f}",
            f"{row['Withdrawal']:,.0f}",
            f"{row['End Balance']:,.0f}"
        ])

    tbl3 = Table(lon_table, repeatRows=1, colWidths=[50, 60, 50, 80, 80, 80, 80])
    tbl3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl3)


    # Build and serve download
    doc.build(story)
    st.download_button(
        label="📥 Download Full PDF Report",
        data=pdf_buf.getvalue(),
        file_name="full_retirement_report.pdf",
        mime="application/pdf"
    )
