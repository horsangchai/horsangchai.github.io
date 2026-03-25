#!/usr/bin/env python3
"""
Rebuild processed analytical tables and figures for the Siam slavery portfolio project.

Usage:
    python src/run_analysis.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "figure.dpi": 200
})

def load():
    obs = pd.read_csv(RAW / "historical_observations.csv")
    sources = pd.read_csv(RAW / "source_registry.csv")
    return obs, sources

def build_processed_tables(obs: pd.DataFrame, sources: pd.DataFrame) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    monthon_population_1904 = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="monthon_population")]
        [["location","value_numeric"]]
        .rename(columns={"location":"monthon","value_numeric":"population"})
        .sort_values("population", ascending=False)
    )
    monthon_population_1904.to_csv(PROCESSED/"monthon_population_1904.csv", index=False)

    monthon_ethnicity_1904 = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="ethnic_population_by_monthon")]
        [["location","ethnicity_inferred","value_numeric"]]
        .rename(columns={"location":"monthon","ethnicity_inferred":"ethnicity","value_numeric":"population"})
        .sort_values(["ethnicity","population"], ascending=[True,False])
    )
    monthon_ethnicity_1904.to_csv(PROCESSED/"monthon_ethnicity_1904.csv", index=False)

    race_totals_df = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="race_total_in_detailed_monthons")]
        [["ethnicity_inferred","value_numeric"]]
        .rename(columns={"ethnicity_inferred":"ethnicity","value_numeric":"population"})
        .sort_values("population", ascending=False)
    )
    race_totals_df["share_of_detailed_population"] = race_totals_df["population"] / race_totals_df["population"].sum()
    race_totals_df.to_csv(PROCESSED/"race_totals_1904_detailed_monthons.csv", index=False)

    houses_df = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="houses_count")]
        [["location","value_numeric"]]
        .rename(columns={"location":"monthon","value_numeric":"houses"})
    )
    pph_df = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="persons_per_household")]
        [["location","value_numeric"]]
        .rename(columns={"location":"monthon","value_numeric":"persons_per_household"})
    )
    monks_df = (
        obs[(obs["source_id"]=="S07") & (obs["variable"]=="monks_and_novices_count")]
        [["location","value_numeric"]]
        .rename(columns={"location":"monthon","value_numeric":"monks_and_novices"})
    )
    welfare_proxies = monthon_population_1904.merge(houses_df, on="monthon").merge(pph_df, on="monthon").merge(monks_df, on="monthon")
    welfare_proxies["monks_per_1000"] = welfare_proxies["monks_and_novices"] / welfare_proxies["population"] * 1000
    welfare_proxies.to_csv(PROCESSED/"welfare_proxies_monthon_1904.csv", index=False)

    slave_scale_scenarios = pd.DataFrame([
        {"scenario":"Conservative lower bound","population_estimate":4500000,"slave_share_assumed":0.25,
         "estimated_slave_population":4500000*0.25,
         "basis":"Bowring lower population bound x quarter-slave benchmark"},
        {"scenario":"Pallegoix quarter benchmark","population_estimate":6000000,"slave_share_assumed":0.25,
         "estimated_slave_population":6000000*0.25,
         "basis":"Pallegoix population cited by Bowring x quarter-slave benchmark"},
        {"scenario":"Bowring high-slavery central","population_estimate":5000000,"slave_share_assumed":0.35,
         "estimated_slave_population":5000000*0.35,
         "basis":"Bowring upper population bound x 'more than a third' centralization"},
        {"scenario":"Upper plausible bound","population_estimate":6000000,"slave_share_assumed":0.35,
         "estimated_slave_population":6000000*0.35,
         "basis":"Pallegoix population x Bowring 'more than a third' lower-bound logic"}
    ])
    slave_scale_scenarios.to_csv(PROCESSED/"slave_scale_scenarios.csv", index=False)

    war_df = obs[(obs["source_id"]=="S01") & (obs["variable"]=="count_fighting_men")][["ethnicity_inferred","value_numeric"]].rename(columns={"ethnicity_inferred":"ethnicity","value_numeric":"fighting_men"})
    multi_rows = []
    for _, r in war_df.iterrows():
        for mult in [3,4,5]:
            multi_rows.append({
                "ethnicity": r["ethnicity"],
                "fighting_men": int(r["fighting_men"]),
                "dependent_multiplier": mult,
                "estimated_total_population": int(r["fighting_men"] * mult),
                "assumption_basis": "Adult male fighting-men count scaled by household/dependent multipliers"
            })
    royal_captive_population_scenarios = pd.DataFrame(multi_rows)
    royal_captive_population_scenarios.to_csv(PROCESSED/"royal_captive_population_scenarios.csv", index=False)

    national_total = float(obs[(obs["source_id"]=="S07") & (obs["variable"]=="national_total_population")]["value_numeric"].iloc[0])
    detailed_total = float(obs[(obs["source_id"]=="S07") & (obs["variable"]=="detailed_monthons_population")]["value_numeric"].iloc[0])
    components = {
        "Detailed-count monthons": detailed_total,
        "Udon": 576947,
        "Isan": 915750,
        "Phayap": 485563,
        "Krung Thep": 493677,
        "Burapha": 208868,
        "Saiburi": 219000,
        "Kelantan": 300000,
        "Tringganu": 114895,
    }
    coverage_rows = []
    for component, pop in components.items():
        coverage_rows.append({
            "component": component,
            "population": pop,
            "share_of_national_total": pop / national_total,
            "detailed_enumeration": int(component=="Detailed-count monthons"),
            "lao_heartland_or_related": int(component in ["Udon","Isan","Phayap"])
        })
    census_coverage_1904 = pd.DataFrame(coverage_rows)
    census_coverage_1904.to_csv(PROCESSED/"census_coverage_1904.csv", index=False)

    abolition_timeline = pd.DataFrame([
        {"year":1874,"date":"1874-01-01","event":"Born Slave Price Reduction Act / law of Pee Chau","type":"domestic reform","domestic_reform_score":5,"external_pressure_score":1,"source_id":"S09","notes":"Freed those born after 1868 gradually and curtailed future sales."},
        {"year":1893,"date":"1893-07-01","event":"Franco-Siamese crisis","type":"foreign pressure","domestic_reform_score":1,"external_pressure_score":5,"source_id":"S08","notes":"French pressure sharpened attention to Lao captive status and extraterritorial claims."},
        {"year":1897,"date":"1897-01-01","event":"Renewed ban on further sales","type":"domestic reform","domestic_reform_score":4,"external_pressure_score":2,"source_id":"S09","notes":"Chulalongkorn restated that no further sales should occur."},
        {"year":1899,"date":"1899-01-01","event":"Corvée commuted to head tax","type":"labor regime reform","domestic_reform_score":4,"external_pressure_score":2,"source_id":"S09","notes":"Shifted coercive extraction from labor service to monetized taxation."},
        {"year":1899,"date":"1899-01-01","event":"Draft nationality law discussed","type":"citizenship / classification","domestic_reform_score":3,"external_pressure_score":4,"source_id":"S08","notes":"Citizenship reform tied to management of captive and alien statuses."},
        {"year":1904,"date":"1904-04-08","event":"Anglo-French declaration concerning Siam","type":"foreign pressure","domestic_reform_score":1,"external_pressure_score":4,"source_id":"S06","notes":"Placed Siam in a formalized imperial diplomatic settlement."},
        {"year":1904,"date":"1904-02-13","event":"Siam-French convention","type":"foreign pressure","domestic_reform_score":1,"external_pressure_score":4,"source_id":"S05","notes":"Territorial and jurisdictional settlement with France."},
        {"year":1905,"date":"1905-03-31","event":"Law for the Abolition of Slavery","type":"domestic reform","domestic_reform_score":5,"external_pressure_score":3,"source_id":"S04","notes":"No new slaves, children free, and debt credited at four ticals per month."},
        {"year":1913,"date":"1913-01-01","event":"Nationality Act","type":"citizenship consolidation","domestic_reform_score":4,"external_pressure_score":2,"source_id":"S08","notes":"Birth in Siam became a stronger basis for legal belonging."},
    ])
    abolition_timeline.to_csv(PROCESSED/"abolition_timeline.csv", index=False)

    lao_captive_communities = pd.DataFrame([
        {"community":"Bang Yi-khan","origin_polity":"Vientiane","captive_group":"royal captives and retainers","location_type":"Bangkok community","primary_labor":"elite-household incorporation","secondary_labor":"government service","beneficiary_primary":"Thai elite / royal household","gendered_pathway":"Daughters absorbed as wives/consorts; sons into government service","status_transition":"captive to incorporated elite-linked households","source_id":"S08"},
        {"community":"Bang Khun Phrom","origin_polity":"Lao Phuan","captive_group":"war captives","location_type":"Bangkok community","primary_labor":"fresh-water naval craft construction","secondary_labor":"boat basin digging","beneficiary_primary":"Front Palace / royal navy","gendered_pathway":"Not specified","status_transition":"captive labor under palace patronage","source_id":"S08"},
        {"community":"Thewet","origin_polity":"Champasak","captive_group":"ruler's family and artisans","location_type":"Bangkok community","primary_labor":"goldsmithing","secondary_labor":"blacksmithing","beneficiary_primary":"court / noble households","gendered_pathway":"Not specified","status_transition":"captive artisan service","source_id":"S08"},
        {"community":"Ban Kruai / Yannawa","origin_polity":"Bang Sai Kai / Lao resettlement","captive_group":"able-bodied Lao captives","location_type":"river-port / industrial","primary_labor":"sawmills and shipyards","secondary_labor":"stevedoring and warehousing","beneficiary_primary":"Western firms / port economy","gendered_pathway":"Not specified","status_transition":"war captive labor to wage labor","source_id":"S08"},
        {"community":"Ban Lao Phuan","origin_polity":"Lao Phuan","captive_group":"laborers","location_type":"palace service settlement","primary_labor":"palace landscaping and sanitation","secondary_labor":"elephant service","beneficiary_primary":"Grand Palace / Royal Household","gendered_pathway":"Women’s quarters maintenance under palace department","status_transition":"state slave labor to freemen later evicted","source_id":"S08"},
        {"community":"Ban Kraba","origin_polity":"evicted Lao community","captive_group":"former captive descendants","location_type":"peri-urban resettlement","primary_labor":"wickerware","secondary_labor":"petty commerce","beneficiary_primary":"urban consumer economy","gendered_pathway":"Household-based artisanal and petty trade labor","status_transition":"freed but economically precarious","source_id":"S08"},
        {"community":"Ban Ti Thong / Ban Chang Thong","origin_polity":"Lao goldsmith captives","captive_group":"artisans","location_type":"artisan quarter","primary_labor":"gold beating / gold leaf / filigree","secondary_labor":"medallions, insignia, munitions","beneficiary_primary":"noble households / military and police suppliers","gendered_pathway":"Not specified","status_transition":"captive artisan labor to specialized urban craft production","source_id":"S08"},
    ])
    lao_captive_communities.to_csv(PROCESSED/"lao_captive_communities.csv", index=False)

    edges = [
        ("Vientiane","Bang Yi-khan","origin_to_community",1),
        ("Bang Yi-khan","Elite marriage incorporation","community_to_labor",1),
        ("Bang Yi-khan","Government service","community_to_labor",1),
        ("Lao Phuan","Bang Khun Phrom","origin_to_community",1),
        ("Bang Khun Phrom","Naval craft production","community_to_labor",1),
        ("Champasak","Thewet","origin_to_community",1),
        ("Thewet","Goldsmithing / blacksmithing","community_to_labor",1),
        ("Bang Sai Kai / Lao captives","Ban Kruai / Yannawa","origin_to_community",1),
        ("Ban Kruai / Yannawa","Sawmills and shipyards","community_to_labor",1),
        ("Ban Kruai / Yannawa","Stevedoring / warehousing","community_to_labor",1),
        ("Lao Phuan","Ban Lao Phuan","origin_to_community",1),
        ("Ban Lao Phuan","Palace landscaping","community_to_labor",1),
        ("Ban Lao Phuan","Palace sanitation","community_to_labor",1),
        ("Ban Kraba","Wickerware","community_to_labor",1),
        ("Ban Kraba","Petty commerce","community_to_labor",1),
        ("Lao goldsmith captives","Ban Ti Thong / Ban Chang Thong","origin_to_community",1),
        ("Ban Ti Thong / Ban Chang Thong","Gold leaf and filigree","community_to_labor",1),
        ("Ban Ti Thong / Ban Chang Thong","Military / police insignia and munitions","community_to_labor",1),
    ]
    lao_labor_network_edges = pd.DataFrame(edges, columns=["source_node","target_node","edge_type","weight"])
    lao_labor_network_edges.to_csv(PROCESSED/"lao_labor_network_edges.csv", index=False)

    debt_burden = pd.DataFrame([
        {"case":"Female redeemable slave (low price)","debt_ticals":60,"monthly_credit_1905":4},
        {"case":"Female redeemable slave (high price)","debt_ticals":100,"monthly_credit_1905":4},
        {"case":"Male redeemable slave (low price)","debt_ticals":80,"monthly_credit_1905":4},
        {"case":"Male redeemable slave (high price)","debt_ticals":120,"monthly_credit_1905":4},
        {"case":"Birth slave fixed price at manhood","debt_ticals":48,"monthly_credit_1905":4},
        {"case":"Illustrative child sale","debt_ticals":100,"monthly_credit_1905":4},
        {"case":"Inflated debt paper example","debt_ticals":400,"monthly_credit_1905":4},
    ])
    debt_burden["months_to_freedom_under_1905_law"] = debt_burden["debt_ticals"] / debt_burden["monthly_credit_1905"]
    debt_burden.to_csv(PROCESSED/"debt_burden_scenarios.csv", index=False)

    derived_metrics = pd.DataFrame([
        {
            "metric_id":"midcentury_slave_stock_lower",
            "metric":"Estimated enslaved population lower bound",
            "value": slave_scale_scenarios["estimated_slave_population"].min(),
            "unit":"persons",
            "interpretation":"Conservative lower-bound scenario for mid-century slave stock",
            "formula_or_basis":"4.5m population x 25% slave share"
        },
        {
            "metric_id":"midcentury_slave_stock_upper",
            "metric":"Estimated enslaved population upper bound",
            "value": slave_scale_scenarios["estimated_slave_population"].max(),
            "unit":"persons",
            "interpretation":"Upper plausible scenario for mid-century slave stock",
            "formula_or_basis":"6.0m population x 35% slave share"
        },
        {
            "metric_id":"lao_share_royal_war_captives",
            "metric":"Lao share of listed royal war captives",
            "value": war_df.loc[war_df["ethnicity"]=="Lao","fighting_men"].iloc[0] / war_df["fighting_men"].sum(),
            "unit":"share",
            "interpretation":"Lao were the single largest group among Bowring's listed royal captive fighting men",
            "formula_or_basis":"20,000 / 46,000"
        },
        {
            "metric_id":"estimated_royal_lao_captives_central",
            "metric":"Estimated Lao captive population with dependents (central)",
            "value": war_df.loc[war_df["ethnicity"]=="Lao","fighting_men"].iloc[0] * 4,
            "unit":"persons",
            "interpretation":"Central multiplier using adult males as one quarter of total population",
            "formula_or_basis":"20,000 x 4"
        },
        {
            "metric_id":"census_detailed_coverage_share",
            "metric":"Share of 1904 national population in detailed census",
            "value": detailed_total / national_total,
            "unit":"share",
            "interpretation":"Only about half the kingdom was covered by detailed 1904 enumeration",
            "formula_or_basis":"3,308,032 / 6,686,846"
        },
        {
            "metric_id":"udon_isan_share_of_national_total",
            "metric":"Share of national population in Udon and Isan",
            "value": (576947 + 915750) / national_total,
            "unit":"share",
            "interpretation":"Omitted Lao-heartland population share",
            "formula_or_basis":"(576,947 + 915,750) / 6,686,846"
        },
        {
            "metric_id":"udon_isan_phayap_share_of_national_total",
            "metric":"Share of national population in Udon, Isan, and Phayap",
            "value": (576947 + 915750 + 485563) / national_total,
            "unit":"share",
            "interpretation":"If northern Lao-related Phayap is included, omitted share rises further",
            "formula_or_basis":"(576,947 + 915,750 + 485,563) / 6,686,846"
        },
        {
            "metric_id":"local_gov_budget_growth_factor",
            "metric":"Growth factor of Ministry of Local Government budget",
            "value": 10500000 / 206000,
            "unit":"x",
            "interpretation":"Scale-up of central administrative capacity",
            "formula_or_basis":"10.5m / 206k"
        },
        {
            "metric_id":"bangkok_police_sanitation_share_revenue",
            "metric":"Bangkok police + sanitation as share of 1903-04 revenue",
            "value": (1143000 + 1121064) / 45540000,
            "unit":"share",
            "interpretation":"Visible Bangkok-centered spending share",
            "formula_or_basis":"(1,143,000 + 1,121,064) / 45,540,000"
        },
        {
            "metric_id":"export_growth_1897_1902",
            "metric":"Export growth 1897 to 1902",
            "value": (87401889 - 57689792) / 57689792,
            "unit":"share",
            "interpretation":"Trade expansion during late reform era",
            "formula_or_basis":"(87,401,889 - 57,689,792) / 57,689,792"
        },
        {
            "metric_id":"import_growth_1897_1902",
            "metric":"Import growth 1897 to 1902",
            "value": (65420231 - 40973403) / 40973403,
            "unit":"share",
            "interpretation":"Import expansion during late reform era",
            "formula_or_basis":"(65,420,231 - 40,973,403) / 40,973,403"
        },
        {
            "metric_id":"months_to_freedom_100_tical_debt",
            "metric":"Months to freedom for 100-tical debt under 1905 law",
            "value": 100/4,
            "unit":"months",
            "interpretation":"Illustrative redemption horizon",
            "formula_or_basis":"100 / 4"
        },
        {
            "metric_id":"months_to_freedom_400_tical_debt",
            "metric":"Months to freedom for 400-tical debt under 1905 law",
            "value": 400/4,
            "unit":"months",
            "interpretation":"Inflated debt paper could still trap labor for years even under abolition law",
            "formula_or_basis":"400 / 4"
        },
        {
            "metric_id":"corvee_escape_cost_vs_slave_tax_ratio",
            "metric":"Monthly corvée escape cost vs annual slave tax ratio",
            "value": (6*12) / 5,
            "unit":"ratio",
            "interpretation":"Shows structural incentive to choose dependency over direct corvée status",
            "formula_or_basis":"72 / 5"
        }
    ])
    derived_metrics.to_csv(PROCESSED/"derived_metrics.csv", index=False)

def make_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    slave_scale_scenarios = pd.read_csv(PROCESSED/"slave_scale_scenarios.csv")
    royal_captive_population_scenarios = pd.read_csv(PROCESSED/"royal_captive_population_scenarios.csv")
    monthon_population_1904 = pd.read_csv(PROCESSED/"monthon_population_1904.csv")
    race_totals_df = pd.read_csv(PROCESSED/"race_totals_1904_detailed_monthons.csv")
    debt_burden = pd.read_csv(PROCESSED/"debt_burden_scenarios.csv")
    census_coverage_1904 = pd.read_csv(PROCESSED/"census_coverage_1904.csv")
    welfare_proxies = pd.read_csv(PROCESSED/"welfare_proxies_monthon_1904.csv")
    abolition_timeline = pd.read_csv(PROCESSED/"abolition_timeline.csv")
    lao_captive_communities = pd.read_csv(PROCESSED/"lao_captive_communities.csv")
    edges_df = pd.read_csv(PROCESSED/"lao_labor_network_edges.csv")

    # 1
    fig, ax = plt.subplots(figsize=(8,4.8))
    plot_df = slave_scale_scenarios.sort_values("estimated_slave_population")
    ax.barh(plot_df["scenario"], plot_df["estimated_slave_population"]/1e6)
    ax.set_xlabel("Estimated enslaved population (millions)")
    ax.set_title("Estimated scale of slavery in mid-19th-century Siam")
    for i, v in enumerate(plot_df["estimated_slave_population"]/1e6):
        ax.text(v + 0.03, i, f"{v:.2f}m", va="center", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES/"fig1_slave_scale_scenarios.png", bbox_inches="tight")
    plt.close(fig)

    # 2
    fig, ax = plt.subplots(figsize=(8,4.8))
    plot_df = royal_captive_population_scenarios[royal_captive_population_scenarios["dependent_multiplier"]==4].sort_values("fighting_men")
    x = np.arange(len(plot_df)); width = 0.35
    ax.bar(x - width/2, plot_df["fighting_men"], width, label="Fighting men")
    ax.bar(x + width/2, plot_df["estimated_total_population"], width, label="Dependent-inclusive estimate (x4)")
    ax.set_xticks(x); ax.set_xticklabels(plot_df["ethnicity"], rotation=25, ha="right")
    ax.set_ylabel("Persons"); ax.set_title("Royal war-captive populations reported by Bowring")
    ax.legend(frameon=False); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURES/"fig2_royal_war_captives.png", bbox_inches="tight"); plt.close(fig)

    # 3
    fig, ax = plt.subplots(figsize=(8.5,5.0))
    plot_df = debt_burden.sort_values("months_to_freedom_under_1905_law")
    ax.barh(plot_df["case"], plot_df["months_to_freedom_under_1905_law"])
    ax.set_xlabel("Months to freedom under 1905 four-tical monthly credit")
    ax.set_title("Debt burdens persisted even under the 1905 abolition law")
    for i, v in enumerate(plot_df["months_to_freedom_under_1905_law"]):
        ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURES/"fig3_redemption_burden.png", bbox_inches="tight"); plt.close(fig)

    # 4
    fig, ax = plt.subplots(figsize=(8,3.8))
    detailed = census_coverage_1904[census_coverage_1904["component"]=="Detailed-count monthons"]["population"].iloc[0]
    lao_heart = census_coverage_1904[census_coverage_1904["component"].isin(["Udon","Isan"])]["population"].sum()
    other_omitted = census_coverage_1904[~census_coverage_1904["component"].isin(["Detailed-count monthons","Udon","Isan"])]["population"].sum()
    total = detailed + lao_heart + other_omitted
    ax.barh(["1904 census frame"], [detailed], label="Detailed enumeration")
    ax.barh(["1904 census frame"], [lao_heart], left=[detailed], label="Omitted Lao heartland (Udon + Isan)")
    ax.barh(["1904 census frame"], [other_omitted], left=[detailed+lao_heart], label="Other omitted/special regions")
    ax.set_xlabel("Population"); ax.set_title("The 1904 census only detailed about half the kingdom")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5,-0.25), ncol=2)
    fig.tight_layout(); fig.savefig(FIGURES/"fig4_census_coverage.png", bbox_inches="tight"); plt.close(fig)

    # 5
    fig, ax = plt.subplots(figsize=(9,5.2))
    plot_df = monthon_population_1904.sort_values("population", ascending=True)
    ax.barh(plot_df["monthon"], plot_df["population"])
    ax.set_xlabel("Population"); ax.set_title("Population of the 12 detailed monthons in the 1904 census")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURES/"fig5_monthon_populations.png", bbox_inches="tight"); plt.close(fig)

    # 6
    fig, ax = plt.subplots(figsize=(8,4.8))
    plot_df = race_totals_df.copy()
    plot_df["share_pct"] = plot_df["share_of_detailed_population"]*100
    plot_df = plot_df.sort_values("share_pct", ascending=False).head(8)
    ax.bar(plot_df["ethnicity"], plot_df["share_pct"])
    ax.set_ylabel("Share of detailed-census population (%)")
    ax.set_title("Ethnic composition in the 12 detailed monthons, 1904")
    ax.grid(axis="y", alpha=0.3)
    for label in ax.get_xticklabels():
        label.set_rotation(25); label.set_ha("right")
    fig.tight_layout(); fig.savefig(FIGURES/"fig6_ethnic_composition.png", bbox_inches="tight"); plt.close(fig)

    # 7
    fig, ax = plt.subplots(figsize=(8.5,5.0))
    cats = ["Local Gov't\n1894-95","Local Gov't\n1903-04","Exports\n1897","Exports\n1902","Imports\n1897","Imports\n1902"]
    vals = [206000,10500000,57689792,87401889,40973403,65420231]
    ax.bar(cats, np.array(vals)/1e6)
    ax.set_ylabel("Millions of ticals")
    ax.set_title("Central state capacity and external trade expanded sharply")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURES/"fig7_state_capacity_trade.png", bbox_inches="tight"); plt.close(fig)

    # 8
    fig, ax = plt.subplots(figsize=(9,5.2))
    plot_df = welfare_proxies.sort_values("persons_per_household")
    ax.barh(plot_df["monthon"], plot_df["persons_per_household"])
    ax.set_xlabel("Persons per house")
    ax.set_title("Household size proxy across detailed-census monthons, 1904")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURES/"fig8_household_size_proxy.png", bbox_inches="tight"); plt.close(fig)

    # 9
    fig, ax = plt.subplots(figsize=(9,3.5))
    y = np.zeros(len(abolition_timeline))
    ax.scatter(abolition_timeline["year"], y, s=60)
    for _, r in abolition_timeline.iterrows():
        ax.vlines(r["year"], 0, 0.15 + 0.03*(r["external_pressure_score"]), alpha=0.6)
        ax.text(r["year"], 0.18 + 0.03*(r["external_pressure_score"]), str(r["year"]) + "\n" + r["event"], ha="center", va="bottom", fontsize=8)
    ax.set_ylim(-0.05, 0.42); ax.set_yticks([]); ax.set_xlabel("Year")
    ax.set_title("Abolition was gradual and entangled with imperial diplomacy")
    for spine in ["left","right","top"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout(); fig.savefig(FIGURES/"fig9_abolition_timeline.png", bbox_inches="tight"); plt.close(fig)

    # 10
    G = nx.DiGraph()
    for _, r in edges_df.iterrows():
        G.add_edge(r["source_node"], r["target_node"], edge_type=r["edge_type"], weight=r["weight"])
    origin_nodes = [n for n in G.nodes if n in ["Vientiane","Lao Phuan","Champasak","Bang Sai Kai / Lao captives","Lao goldsmith captives"]]
    community_nodes = [n for n in G.nodes if n in lao_captive_communities["community"].tolist()]
    labor_nodes = [n for n in G.nodes if n not in origin_nodes + community_nodes]
    pos = {}
    for i, n in enumerate(origin_nodes):
        pos[n] = (0, len(origin_nodes)-i)
    for i, n in enumerate(sorted(community_nodes)):
        pos[n] = (1.5, len(community_nodes)-i-0.5)
    for i, n in enumerate(sorted(labor_nodes)):
        pos[n] = (3.2, len(labor_nodes)-i)
    fig, ax = plt.subplots(figsize=(11,7))
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, alpha=0.5, width=1.2, arrowstyle='-|>')
    nx.draw_networkx_nodes(G, pos, nodelist=origin_nodes, ax=ax, node_shape='o', node_size=900, label='Origin polity/group')
    nx.draw_networkx_nodes(G, pos, nodelist=community_nodes, ax=ax, node_shape='s', node_size=1400, label='Bangkok Lao community')
    nx.draw_networkx_nodes(G, pos, nodelist=labor_nodes, ax=ax, node_shape='^', node_size=1100, label='Labor specialization')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
    ax.set_title("Bangkok's Lao captive-labor system linked origin, settlement, and specialized work")
    ax.legend(frameon=False, loc="upper left"); ax.axis("off")
    fig.tight_layout(); fig.savefig(FIGURES/"fig10_lao_labor_network.png", bbox_inches="tight"); plt.close(fig)

def main() -> None:
    obs, sources = load()
    build_processed_tables(obs, sources)
    make_figures()
    print("Processed tables and figures rebuilt successfully.")

if __name__ == "__main__":
    main()
