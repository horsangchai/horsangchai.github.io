# Slavery in Late-19th-Century Siam: A Data-Science Reconstruction (1850–1905)

## Project summary

This portfolio project reconstructs slavery in Siam as a **data-driven system of labor extraction, inequality, and state formation**, with special attention to the exploitation of **Lao / Isan populations**. Rather than treating slavery as a purely legal category or as a moral aside, the project analyzes it as an integrated political economy linking:

- population registration and ethnic classification
- debt, pricing, and labor obligations
- royal captive labor and Bangkok-centered state projects
- the gendered and intergenerational reproduction of bondage
- late-nineteenth-century abolition, diplomacy, and centralization

## Core research question

**What did slavery in Siam look like at scale—economically, demographically, and structurally—and how did it function to benefit Bangkok-centered elites?**

## Main findings

1. **Slavery was large in scale.** Combining Bowring's 1850s population bounds with contemporary slave-share claims produces a plausible mid-century enslaved population range of roughly **1.1–2.1 million people**.
2. **Lao war captives were central to the royal labor system.** Bowring's own list implies that **Lao accounted for 43.5% of listed royal war-captive fighting men**. Using Grabowsky's quarter-population benchmark for able-bodied men yields a central estimate of roughly **80,000 Lao captives plus dependents** tied to the crown.
3. **Ethnic classification was political.** The 1904 census detailed only **49.5%** of the kingdom, while the omitted Lao heartland of **Udon + Isan alone represented 22.3%** of the kingdom's estimated population.
4. **Debt bondage remained materially heavy even during abolition.** Under the 1905 law's four-tical monthly credit, a 100-tical debt implied about **25 months** to freedom, while a 400-tical inflated note implied **100 months**.
5. **Abolition coincided with state-building and imperial pressure.** The Ministry of Local Government's budget grew by about **51.0x** between 1894–95 and 1903–04, while exports also surged.

## Repository structure

- `data/raw/`
  - `source_registry.csv`: source inventory with URLs and primary/secondary flags
  - `historical_observations.csv`: manually coded observation-level dataset from historical sources
- `data/processed/`
  - cleaned and derived analytical tables used in the report
- `figures/`
  - generated charts and the Lao captive-labor network graphic
- `notebooks/`
  - reproducible Jupyter notebook
- `src/`
  - Python scripts for transformation and analysis
- `docs/`
  - project methodology and coding protocol notes
- `report/`
  - polished report in DOCX and PDF

## Dataset design

The core dataset is **long-form**. Each row in `historical_observations.csv` is one structured historical observation with fields for:

- source linkage
- year / period
- location and region
- population group and ethnicity
- legal status and economic sector
- thematic category
- variable name, numeric value, and units
- bounds, inference flags, page references, and coding notes

This design preserves ambiguity better than forcing all evidence into a single rectangular panel.

## Reproducibility

Install the project dependencies and rebuild the analytical outputs from the manually coded raw CSV files:

```bash
pip install -r requirements.txt
python src/run_analysis.py
```

The notebook version of the workflow is available in `notebooks/siam_slavery_analysis.ipynb`, with a browser-friendly export at `notebooks/siam_slavery_analysis.html`. The main written report is available in both `report/siam_slavery_report.docx` and `report/siam_slavery_report.pdf`.

## Important caveat

This is a **historical reconstruction**, not an administrative microdata extract. The underlying sources are fragmentary, elite-authored, and politically structured. The numbers here are therefore best read as **transparent estimates with uncertainty**, not as final archival totals.
