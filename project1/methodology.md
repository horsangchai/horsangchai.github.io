# Methodology

## 1. Research design

This project treats slavery in Siam as a measurable political-economic system rather than only a legal status. The empirical strategy combines:

1. **Primary-source extraction** from Bowring, British consular reporting, the 1904 official Siam publication, and the 1905 abolition law.
2. **Structured coding** of qualitative historical statements into quantitative variables.
3. **Secondary-source triangulation** using Grabowsky, Van Roy, and Cruikshank to recover censal context, ethnic classification bias, captive-labor geography, and abolition chronology.
4. **Transparent estimation** where the historical record is incomplete.

## 2. Source hierarchy

Priority was given to primary sources. Secondary works were used mainly in three ways:

- to translate or contextualize primary material (especially the 1904 census explanation)
- to recover community-level evidence not preserved in a single machine-readable administrative source
- to identify distortions in official classification, especially the erasure of Lao ethnicity

## 3. Unit of observation

The core file, `historical_observations.csv`, is a long-form observation table. One row may represent:

- a direct numeric statement (for example, 20,000 Lao fighting men)
- a reported range (for example, male slave prices of 80–120 ticals)
- a binary coded feature of the legal regime (for example, women could be forced into marriage with only partial remission of redemption value)
- a bounded or approximate statement (for example, “more than a third”)

This structure was chosen because the sources are heterogeneous: law, narrative, budgets, census explanation, diplomatic correspondence, and community studies do not map neatly into one rectangular panel.

## 4. Coding principles

### 4.1 Direct numeric coding
When a source gave a numeric value directly, that value was entered in `value_numeric` with units and page references.

Examples:
- number of listed royal war captives by ethnicity
- wage rates in ticals
- budget totals in ticals
- census populations by monthon and race

### 4.2 Range coding
When the source gave a range, both the row-level value and the `lower_bound` / `upper_bound` fields were used.

Examples:
- male redeemable slave prices: 80–120 ticals
- female redeemable slave prices: 60–100 ticals
- Talesap exports: 100,000–200,000 piculs

### 4.3 Bounded statements
Some sources give lower or upper bounds but not exact values.
These are coded as such rather than converted into false precision.

Examples:
- Bowring: “much more than a third” of Siamese were slaves
- Grabowsky: slaves may have made up “up to one fourth” of the total population

### 4.4 Constructivist coding of ethnicity
The project explicitly distinguishes administrative labels from historically interpreted labels.

Examples:
- if the census framework classified Lao as Thai, `ethnicity_admin` may be “Thai” while `ethnicity_inferred` records “Lao”
- renaming of monthons such as Lao Phuan → Udon was coded as an administrative act of ethnic suppression

This is important because the census did not merely describe ethnicity; it helped produce a Bangkok-centered national category.

## 5. Derived estimates

### 5.1 Mid-century slave-stock scenarios
A scenario approach was used because no single census provides a complete mid-century slave count.

Inputs:
- Bowring’s population lower and upper bounds: 4.5–5.0 million
- Pallegoix benchmark cited by Bowring: 6.0 million
- slave-share claims around one fourth to “more than a third”

Outputs:
- lower-bound and upper-plausible enslaved population scenarios

### 5.2 Dependent-inclusive Lao captive estimate
Bowring’s 20,000 Lao royal war captives refer only to “fighting men”.
To estimate total captive populations including women, children, and dependents, the project uses Grabowsky’s note that tax-paying able-bodied men were roughly one fourth of the population.

Central estimate:
- 20,000 × 4 = 80,000

Sensitivity range:
- multipliers of 3, 4, and 5

This is a transparent inference, not a direct count.

### 5.3 Redemption-burden simulation
The 1905 law credited 4 ticals per month against debt.
The project applies that rate to Bowring’s price and debt examples to estimate months to freedom.

This produces a simple simulation of how gradual abolition interacted with existing debt burdens.

## 6. Analytical themes

The processed datasets and figures are organized around six themes:

1. scale and demography
2. labor systems and economic contribution
3. women and children
4. political economy of abolition
5. inequality and extraction
6. welfare and regional disparity

## 7. Limitations

1. **Elite-source bias.** Most primary sources were produced by officials, diplomats, or foreign observers, not by enslaved people.
2. **Coverage bias.** The 1904 census omitted major Lao regions from detailed enumeration.
3. **Category bias.** “Thai” is partly an administrative product rather than a neutral ethnic descriptor.
4. **Temporal mismatch.** The project combines evidence from the 1850s, 1880, 1904, and 1905. This is necessary for reconstruction but should not be mistaken for a single-year panel.
5. **No individual microdata.** Household or person-level original returns are not available here, so the project is meso- and macro-analytical.

## 8. Why the long-form dataset matters

The strongest feature of the project is not any one estimate; it is the way heterogeneous historical evidence is converted into a linked analytical dataset that supports reproducible quantitative reasoning while preserving uncertainty.
