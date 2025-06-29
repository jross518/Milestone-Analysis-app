import streamlit as st
# … your existing imports and load_data/simulation code …

# --- UI ---
st.set_page_config(layout="wide", page_title="Fiber Sequencing Comparison")
st.title("Fiber Construction Sequencing Methods")

# — EXECUTIVE SUMMARY —
# after you’ve loaded data & run your milestones() logic:
# assume you have variables days50, cost50, days75, cost75, days100, cost100

# Calculate once:
days50, cost50 = milestone_metrics(sched_sd,          0.5)[:2]
days75, cost75 = milestone_metrics(sched_sd,          0.75)[:2]
days100, cost100 = milestone_metrics(sched_sd,         1.0)[:2]

st.markdown("## Executive Summary")
st.markdown(f"""
- **50% Milestone:** Reached in **{days50}** days at **${cost50:,.0f}**  
- **75% Milestone:** Reached in **{days75}** days at **${cost75:,.0f}**  
- **100% Completion:** Finalized in **{days100}** days at total cost **${cost100:,.0f}**  
""")

st.markdown("### Pros & Cons (NTP-Based Sequencing)")
pro_con_df = pd.DataFrame([
    ["Predictability",        "Clear start dates from NTP ensure timely ramp-up",  "Delays in late NTPs push completion out"],
    ["Cost Control",          "Early visibility on segment costs",                 "High-cost segments early can spike CAPEX"],
    ["Risk Management",       "…",                                                "…"],
    ["Stakeholder Confidence","…",                                                "…"],
], columns=["Metric","Advantage","Trade-off"])
st.table(pro_con_df)

# — then continue with your sliders, KPIs, charts, etc. —