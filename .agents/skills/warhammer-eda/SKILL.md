---
name: warhammer-eda
description: Skill for performing an Exploratory Data Analysis (EDA) on the Warhammer 40k dataset to predict unit factions, strictly following the university project guidelines.
---

# Warhammer 40k Faction Prediction: EDA Guidelines

This skill provides the mandatory instructions, structural guidelines, and domain-specific knowledge required to perform a comprehensive Exploratory Data Analysis (EDA) on the Warhammer 40k dataset. The primary goal of the project is to predict the faction to which a unit belongs (`faction_id`).

## 1. General Notebook Requirements
Follow these strict rules based on the assignment guidelines:
- **Language**: The entire notebook (titles, comments, interpretations, and conclusions) MUST be written in **English**.
- **Header**: Start with a formal header containing the Faculty logo (if available), the project title, and a brief description of the problem.
- **Structure**: Combine Markdown cells for explanations with Code cells. Do not produce long sequences of code without markdown interpretations.
- **Reproducibility**: Include a configuration section at the beginning with:
  - Grouped imports.
  - Reproducible file paths (relative paths).
  - Random seed setting (`random_state`) for any stochastic operations.
  - Visualization settings (e.g., `sns.set_theme()`).
- **Execution State**: The final notebook must run end-to-end without errors when using "Run All". Keep all outputs visible.

## 2. Table Definitions & Domain Knowledge
The analysis focuses on the 5 tables stored in the `importantes` folder. When describing these tables in the EDA, use the expanded, non-abbreviated column names for clarity.

### Tables to be Used
1. **`Factions`**: Contains the target faction names and IDs.
   - *Columns to keep*: `id`, `name`.
   - *Columns removed*: `link` (irrelevant URL).
2. **`Datasheets`**: The core table mapping units to factions.
   - *Columns to keep*: `id`, `name`, `faction_id` (Target variable), `loadout` (text description of equipped gear).
   - *Columns removed*: `source_id` (sources table removed), `legend` (inefficient text processing), `role` (indifferent for faction prediction), `transport` (many missing values), `virtual`, `leader_head`, `leader_footer` (missing values/irrelevant), `damaged_w`, `damaged_description`, `link`.
3. **`DS_Models`**: Contains the physical characteristics and defensive stats of the unit models.
   - *Columns to keep*: 
     - `datasheet_id`
     - `name`
     - `M_Movement`: Movement speed.
     - `T_Toughness`: Resistance to being wounded.
     - `Sv_Save`: Armor save value.
     - `inv_sv_InvulnerableSave`: Special save bypassing armor penetration.
     - `W_Wounds`: Health points of the model.
     - `Ld_Leadership`: Morale and psychological resilience.
     - `OC_ObjectiveControl`: Ability to hold tactical objectives.
   - *Columns removed*: `line`, `inv_sv_descr` (mostly empty), `base_size`, `base_size_descr` (physical plastic base size, irrelevant).
4. **`DS_Wargear`**: Contains the offensive weapon profiles.
   - *Columns to keep*: 
     - `datasheet_id`
     - `name`: Weapon name.
     - `description`
     - `range`: Attack range.
     - `type`: Ranged or Melee.
     - `A_Attacks`: Number of attacks made.
     - `BS_WS_Skill`: Ballistic Skill / Weapon Skill (accuracy).
     - `S_Strength`: Weapon's physical power.
     - `AP_ArmorPenetration`: Ability to pierce armor.
     - `D_Damage`: Damage dealt per successful wound.
   - *Columns removed*: `line`, `line_in_wargear`, `dice`.
5. **`DS_Model_Costs`**: Contains the point costs for units.
   - *Columns to keep*: `datasheet_id`, `line`, `description`, `cost`.

### Tables Explicitly Excluded
Document in the EDA why these tables are excluded:
- **Folder `menos_importantes`** (`abilities`, `ds_abilities`, `detachment_abilities`, `enhancements`, `stratagems`): Excluded because they consist almost entirely of long text descriptions or lack numerical characteristics that reliably identify a unit's faction, though they might hold value for future NLP tasks.
- **Folder `removidos`** (`sources`, `last_update`, `ds_options`, `ds_leader`, `ds_unit_comp`): Excluded because they contain purely metadata, irrelevant chart info, URLs, or redundant references.

## 3. Data Integration (`data` table)
After loading the 5 important tables and dropping the specified unused columns, you MUST merge them into a single, unified analytical table (e.g., a dataframe named `data`). 
- **Join Logic**: Document the keys used for merging (e.g., `Datasheets.id` = `DS_Models.datasheet_id`).
- **Validation**: Verify that the joins do not create unintended duplicates or drop unexpected records.

## 4. EDA Phases

### A. Structural Inspection & Roles
- Identify the analytical role of each column: Identifier, Numerical (Continuous/Discrete), Categorical (Nominal/Ordinal), or Text.

### B. Data Quality
- Check for missing values, duplicates, impossible ranges (e.g., negative toughness), and extreme outliers. 
- Summarize findings and implications. Do not silently impute or drop without justification.

### C. Univariate Analysis
- Describe numerical variables (center, dispersion, shape) and categorical variables (frequencies). 

### D. Target Variable Analysis
- Explicitly analyze `faction_id`.
- Show counts, proportions, and assess the class balance/imbalance.
- Establish a naive baseline (e.g., always predicting the majority faction).

### E. Bivariate & Multivariate Analysis
- Explore relationships between numerical/categorical features and the target faction.
- Identify correlations and multicollinearity between stats (e.g., `T_Toughness` vs `W_Wounds`).
- Compare groups (e.g., "Do Orks have lower average `BS_WS_Skill` but higher `A_Attacks`?").

### F. Exploratory Feature Engineering (CRITICAL)
- **Numerical Features**: Analyze derived features if useful (e.g., total offensive power = `A_Attacks` * `S_Strength` * `D_Damage`).
- **Text Features**: Extract faction-specific vocabulary from text columns like `loadout` and `name` (in `DS_Wargear`). 
  - *Example*: Orks have distinct terminology ("kustom", "choppa", "dakka"), while Space Marines use standard terms ("plasma", "bolter", "chainsword"). 
  - Build simple frequency analyses or TF-IDF explorations to show that these words strongly associate with specific `faction_id`s.

### G. Conclusions & Roadmap
End the notebook with:
- Summary of main findings.
- Pending data quality issues to resolve during modeling.
- Important variables and interactions discovered.
- Hypotheses for data cleaning, imputation, and encoding to be validated during the modeling phase.
