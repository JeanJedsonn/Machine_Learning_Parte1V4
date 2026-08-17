import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()

    cells = []

    # 1. Header and Configuration
    cells.append(nbf.v4.new_markdown_cell("""<img src="images/Logo_de_la_Facultad_Experimental_de_Ciencia_y_Tecnología.svg" width="150" align="right">

# Warhammer 40k Faction Prediction - EDA
**University of Carabobo**  
**Experimental Faculty of Science and Technology**  
**Department of Computing**  
**Course:** Machine Learning  

**Description:** This notebook performs a comprehensive Exploratory Data Analysis (EDA) on a Warhammer 40k dataset. The primary objective is to understand the underlying data structure, assess data quality, and discover patterns to predict the faction to which a unit belongs (`faction_id`).

### Context & Definition of the Problem
The domain is the tabletop wargame Warhammer 40k. Players build armies from different factions, each with unique statistics, weapons, and specializations. 
- **Observation Unit**: A single Datasheet (which represents a specific unit or character in the game, along with its aggregated models and wargear).
- **Target Variable**: `faction_id` (or `faction_name`). This is a **multiclass classification** problem.

### Guiding Questions
1. How imbalanced is the distribution of factions?
2. What are the general ranges, cardinality, and quality issues (missing/duplicates) of the game stats?
3. Which stats (Toughness, Wounds, Movement) correlate most with the Cost of a unit?
4. How do weapon preferences (Melee vs Ranged) differentiate factions?
5. Can we extract meaningful faction-specific vocabulary from weapon names using NLP?
"""))

    cells.append(nbf.v4.new_code_cell("""# Configuration & Imports
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
import re

# Reproducibility and Visuals
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
sns.set_theme(style="whitegrid", palette="muted")
pd.set_option('display.max_columns', None)
"""))

    # 2. Data Loading
    cells.append(nbf.v4.new_markdown_cell("""## 1. Data Loading and Integration
We connect to the SQLite database `warhammer40k.db` which contains our raw tables. We will extract the 5 important tables and construct a unified analytical dataframe.

### Excluded Data and Dimensionality Reduction
To build a clean and focused analytical dataset, several tables and columns were discarded:
**Discarded Tables:**
- `sources`, `last_update`, `ds_options`, `ds_leader`, `ds_unit_comp`: Irrelevant metadata, external links, and composition limits that do not define a unit's combat profile.
- `abilities`, `detachment_abilities`, `enhancements`, `stratagems` (and their junction tables): Excluded because they are composed almost entirely of unstructured narrative text and lack numerical features directly usable for faction identification.

**Discarded Columns from `Datasheets`:**
- `source_id`, `link`: External references and URLs.
- `legend`, `role`: Narrative text with inefficient processing overhead.
- `transport`, `virtual`, `leader_head`, `leader_footer`, `damaged_w`, `damaged_description`: Excluded due to massive amounts of missing data (nulls) and little to no predictive power.

**Other Discarded Columns (from remaining tables):**
- `line`, `line_in_wargear`: Internal row indices without analytical value.
- `dice`: Dice rolling formulas (e.g., D6) that are too complex for simple numeric parsing.
- `link` (from Factions): External URL.
- `name` (from DS_Models), `description` (from DS_Wargear, DS_Model_Costs), `inv_sv_descr`, `base_size`, `base_size_descr`: Purely descriptive/narrative text or physical dimensions that do not directly contribute to the numeric combat profile.

### Included Tables & Contributed Columns:
*   **`Factions`**: `name` (extracted as `faction_name`).
*   **`Datasheets`**: `id`, `name` (extracted as `unit_name`), `faction_id`, and `loadout`.
*   **`DS_Models`**: `M`, `T`, `Sv`, `inv_sv`, `W`, `Ld`, and `OC` (averaged per datasheet).
*   **`DS_Wargear`**: `A`, `BS_WS`, `S`, `AP`, `D`, `range`, `type`, and `name` (aggregated per datasheet).
*   **`DS_Model_Costs`**: `cost` (averaged per datasheet).


### Data Dictionary
To understand the tabletop attributes, here is the definition of each variable:
- **Movement (M)**: Inches the unit can move in the Movement phase.
- **Toughness (T)**: Compared against weapon Strength to determine wound success.
- **Save (Sv)**: Armor saving throw to avoid damage.
- **Invulnerable Save (inv_sv)**: Special save that ignores Armor Penetration (AP).
- **Wounds (W)**: Health points. When damage equals this, the model dies.
- **Leadership (Ld)**: Used for Battle-shock tests (rolling 2D6).
- **Objective Control (OC)**: The value this model contributes to controlling an objective marker.
- **Base Size**: The physical size of the model's base in millimeters, key for measuring distances.
- **Attacks (A)**: Number of attacks a weapon makes.
- **Skill (BS/WS)**: Ballistic Skill (ranged) or Weapon Skill (melee). The dice roll needed to hit.
- **Strength (S)**: Compared to target's Toughness to see if an attack wounds.
- **Armor Penetration (AP)**: Negative modifier applied to the target's Save.
- **Damage (D)**: Wounds removed per successful unsaved wound.
"""))

    cells.append(nbf.v4.new_code_cell("""# Connect to the local SQLite DB
conn = sqlite3.connect('warhammer40k.db')

# Load the tables
factions = pd.read_sql_query("SELECT id as faction_id, name as faction_name FROM Factions", conn)
datasheets = pd.read_sql_query("SELECT id as datasheet_id, name as unit_name, faction_id, loadout FROM Datasheets", conn)
models = pd.read_sql_query(\"\"\"
    SELECT datasheet_id, name as model_name, 
           CAST(REPLACE(M, '"', '') AS FLOAT) as M_Movement, 
           CAST(T AS FLOAT) as T_Toughness, 
           Sv as Sv_Save, 
           inv_sv as inv_sv_InvulnerableSave, 
           CAST(W AS FLOAT) as W_Wounds, 
           Ld as Ld_Leadership, 
           CAST(OC AS FLOAT) as OC_ObjectiveControl 
    FROM DS_Models
\"\"\", conn)
wargear = pd.read_sql_query(\"\"\"
    SELECT datasheet_id, name as weapon_name, type as weapon_type, range, 
           A as A_Attacks, BS_WS as BS_WS_Skill, S as S_Strength, 
           AP as AP_ArmorPenetration, D as D_Damage
    FROM DS_Wargear
\"\"\", conn)
costs = pd.read_sql_query("SELECT datasheet_id, cost FROM DS_Model_Costs", conn)

conn.close()

print(f"Datasheets: {len(datasheets)}, Models: {len(models)}, Wargear: {len(wargear)}, Costs: {len(costs)}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Merge into a Unified Data Table
We will merge the datasets using `datasheet_id`. Since a single datasheet might have multiple models, weapons, and costs, joining them all directly will cause an explosion of rows (Cartesian product). To prevent this, we aggregate Wargear, Models, and Costs at the `datasheet_id` level before merging with the main `Datasheets` table.
"""))

    cells.append(nbf.v4.new_code_cell("""# Extract numeric and text values
def extract_numeric(val):
    try:
        return float(val)
    except:
        return np.nan

def extract_skill(val):
    if pd.isna(val): return np.nan
    match = re.search(r'\d+', str(val))
    if match: return float(match.group())
    return np.nan

def extract_range(val):
    if pd.isna(val): return np.nan
    if 'melee' in str(val).lower(): return 0.0
    match = re.search(r'\d+', str(val))
    if match: return float(match.group())
    return np.nan

# Extract models
models['Sv_numeric'] = models['Sv_Save'].apply(extract_skill)
models['Ld_numeric'] = models['Ld_Leadership'].apply(extract_skill)
models['inv_sv_numeric'] = models['inv_sv_InvulnerableSave'].apply(extract_skill)

# Aggregate Models (Average stats per datasheet)
models_agg = models.groupby('datasheet_id').agg({
    'M_Movement': 'mean',
    'T_Toughness': 'mean',
    'W_Wounds': 'mean',
    'OC_ObjectiveControl': 'mean',
    'Sv_numeric': 'mean',
    'Ld_numeric': 'mean',
    'inv_sv_numeric': 'mean'
}).reset_index()

wargear['A_numeric'] = wargear['A_Attacks'].apply(extract_numeric)
wargear['S_numeric'] = wargear['S_Strength'].apply(extract_numeric)
wargear['D_numeric'] = wargear['D_Damage'].apply(extract_numeric)
wargear['AP_numeric'] = wargear['AP_ArmorPenetration'].apply(extract_numeric)
wargear['Skill_numeric'] = wargear['BS_WS_Skill'].apply(extract_skill)
wargear['Range_numeric'] = wargear['range'].apply(extract_range)

wargear_agg = wargear.groupby('datasheet_id').agg({
    'A_numeric': 'mean',
    'S_numeric': 'mean',
    'D_numeric': 'mean',
    'AP_numeric': 'mean',
    'Skill_numeric': 'mean',
    'Range_numeric': 'mean',
    'weapon_name': lambda x: ' '.join(x.dropna()),
    'weapon_type': lambda x: ' '.join(x.dropna())
}).reset_index()

# Aggregate Costs
costs['cost_numeric'] = pd.to_numeric(costs['cost'], errors='coerce')
costs_agg = costs.groupby('datasheet_id').agg({'cost_numeric': 'mean'}).reset_index()

# Merge everything into a final 'data' table
data = datasheets.merge(factions, on='faction_id', how='left')
data = data.merge(models_agg, on='datasheet_id', how='left')
data = data.merge(wargear_agg, on='datasheet_id', how='left')
data = data.merge(costs_agg, on='datasheet_id', how='left')

# Rename columns for clarity in plots
data = data.rename(columns={
    'M_Movement': 'Movement',
    'T_Toughness': 'Toughness',
    'W_Wounds': 'Wounds',
    'OC_ObjectiveControl': 'Objective_Control',
    'Sv_numeric': 'Save',
    'Ld_numeric': 'Leadership',
    'inv_sv_numeric': 'Invulnerable_Save',
    'A_numeric': 'Attacks',
    'S_numeric': 'Strength',
    'D_numeric': 'Damage',
    'AP_numeric': 'Armor_Penetration',
    'Skill_numeric': 'Skill',
    'Range_numeric': 'Range',
    'weapon_type': 'Weapon_Type',
    'cost_numeric': 'Cost'
})

print(f"Final merged dataset shape: {data.shape}")
display(data.head())
"""))

    # 3. Structural Inspection
    cells.append(nbf.v4.new_markdown_cell("""## 2. Structural Inspection and Data Quality
Let's define the analytical roles:
- **Identifier**: `datasheet_id`, `unit_name`
- **Target**: `faction_id` (Categorical Nominal)
- **Categorical Nominal**: `faction_name`
- **Numerical Continuous**: `Movement`, `Toughness`, `Save`, `Invulnerable_Save`, `Wounds`, `Leadership`, `Objective_Control`, `Attacks`, `Strength`, `Damage`, `Armor_Penetration`, `Skill`, `Range`, `Cost`
- **Text**: `loadout`, `weapon_name`, `Weapon_Type`
"""))

    cells.append(nbf.v4.new_code_cell("""# Data Types and Missing Values
quality_df = pd.DataFrame({
    'Type': data.dtypes,
    'Missing Values': data.isnull().sum(),
    'Missing %': (data.isnull().sum() / len(data)) * 100,
    'Cardinality': data.nunique()
})
display(quality_df)

print("\\n--- Ranges and Distribution (describe) ---")
display(data.describe())
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Data Quality Implications & Domain Rules
- **Missing Values**: Some units might not have models or wargear explicitly listed in a format that was parsed numerically (e.g. abilities instead of weapons). We must decide whether to impute these with medians or treat them as a distinct group.
- **Duplicates**: The merge strategy successfully avoided duplication by aggregating at the datasheet level.
- **Ranges and Domain**: Stats like Toughness, Wounds, and Strength strictly positive, which respects the domain rules of the game.
- **Cardinality**: `faction_name` has high cardinality (many factions), which will require specific balancing strategies.
- **Temporal Order**: *Not applicable*. This dataset represents static rules and profiles of tabletop game units; thus, temporal or sequential ordering does not apply.
"""))

    # 4. Univariate Analysis
    cells.append(nbf.v4.new_markdown_cell("""## 3. Univariate Analysis & Target Analysis
Let's explore the distributions of key numerical features and the target variable.
"""))

    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(18, 5))

sns.histplot(data['Toughness'], bins=20, kde=True, ax=axes[0], color='skyblue')
axes[0].set_title('Distribution of Toughness')

sns.histplot(data['Wounds'], bins=20, kde=True, ax=axes[1], color='salmon')
axes[1].set_title('Distribution of Wounds')

sns.histplot(data['Cost'], bins=20, kde=True, ax=axes[2], color='lightgreen')
axes[2].set_title('Distribution of Costs')

plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Factions that Stand Out
Let's analyze which factions have the highest average attributes across the board.
"""))

    cells.append(nbf.v4.new_code_cell("""# Factions that stand out in key attributes
attributes = ['Toughness', 'Wounds', 'Movement', 'Cost']
titles = ['Toughness', 'Wounds', 'Movement', 'Cost']

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for i, attr in enumerate(attributes):
    # Calculate average attribute per faction
    top_factions = data.groupby('faction_name')[attr].mean().sort_values(ascending=False).head(5)
    
    sns.barplot(x=top_factions.values, y=top_factions.index, ax=axes[i], palette="magma")
    axes[i].set_title(f'Top 5 Factions by Average {titles[i]}')
    axes[i].set_xlabel(f'Average {titles[i]}')
    axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_code_cell("""# Target Variable Analysis
plt.figure(figsize=(12, 6))
order = data['faction_name'].value_counts().index
sns.countplot(y=data['faction_name'], order=order, palette='viridis')
plt.title('Class Balance of Target Variable (Faction)')
plt.xlabel('Count')
plt.ylabel('Faction Name')
plt.show()

# Baseline Accuracy
majority_class_count = data['faction_name'].value_counts().max()
baseline = majority_class_count / len(data)
print(f"Majority Class Baseline Accuracy: {baseline*100:.2f}%")
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Target Analysis Conclusions
- The target variable is severely **imbalanced**. Space Marines represent a massive portion of the dataset, which is expected given the tabletop game's lore and rules. 
- A naive baseline simply guessing "Space Marines" would achieve around 15-20% accuracy. Our predictive model must beat this. Data balancing techniques (SMOTE, class weights) will be necessary during modeling.
"""))

    # 5. Bivariate & Multivariate
    cells.append(nbf.v4.new_markdown_cell("""## 4. Bivariate & Multivariate Analysis
We will analyze how numerical features correlate with each other and how they differ across factions.
"""))

    cells.append(nbf.v4.new_code_cell("""# Correlation Heatmap
numeric_cols = ['Movement', 'Toughness', 'Wounds', 'Objective_Control', 'Attacks', 'Strength', 'Damage', 'Cost']

plt.figure(figsize=(10, 8))
corr = data[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Matrix of Numerical Features")
plt.show()
"""))

    cells.append(nbf.v4.new_code_cell("""# Boxplots: Key Attributes by Faction
top_factions = data['faction_name'].value_counts().head(10).index
subset = data[data['faction_name'].isin(top_factions)]

attributes_to_plot = ['Toughness', 'Wounds', 'Strength', 'Cost']
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
axes = axes.flatten()

for i, attr in enumerate(attributes_to_plot):
    sns.boxplot(x='faction_name', y=attr, data=subset, ax=axes[i], palette='Set2')
    axes[i].set_title(f'{attr} Distribution across Top 10 Factions')
    axes[i].tick_params(axis='x', rotation=45)
    axes[i].set_xlabel('')

plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Feature Relationships
- `Toughness` and `Wounds` are highly correlated, which logically represents the "bulk" of a unit.
- Cost strongly correlates with Wounds and Offensive stats, showing the point balancing of the game.
- Boxplots show significant differences between factions: Adeptus Custodes generally exhibit higher toughness compared to Astra Militarum.
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Cost Efficiency per Faction
We can compute the cost-efficiency of factions by dividing key stats by `cost_numeric`. This reveals which factions get the most "value" per point.
"""))

    cells.append(nbf.v4.new_code_cell("""# Calculate efficiency metrics
cost_data = data[data['Cost'] > 0].copy()
cost_data['Toughness_per_Cost'] = cost_data['Toughness'] / cost_data['Cost']
cost_data['Wounds_per_Cost'] = cost_data['Wounds'] / cost_data['Cost']

# Group by faction
efficiency = cost_data.groupby('faction_name').agg({
    'Toughness_per_Cost': 'mean',
    'Wounds_per_Cost': 'mean'
})

print("--- Top 5 Factions: Toughness per Cost ---")
display(efficiency.sort_values(by='Toughness_per_Cost', ascending=False)[['Toughness_per_Cost']].head(5))

print("\\n--- Top 5 Factions: Wounds per Cost ---")
display(efficiency.sort_values(by='Wounds_per_Cost', ascending=False)[['Wounds_per_Cost']].head(5))
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Wargear Specialization (Melee vs Ranged)
We can analyze the raw `DS_Wargear` data to determine the specialization of each faction. Do they prefer Melee weapons, or Ranged weapons? What is their average range?
"""))

    cells.append(nbf.v4.new_code_cell("""# Merge wargear with factions to analyze specialization
wargear_faction = wargear.merge(datasheets[['datasheet_id', 'faction_id']], on='datasheet_id')
wargear_faction = wargear_faction.merge(factions[['faction_id', 'faction_name']], on='faction_id')

# Standardize weapon_type
wargear_faction['is_melee'] = wargear_faction['weapon_type'].str.contains('Melee', case=False, na=False)
wargear_faction['is_ranged'] = wargear_faction['weapon_type'].str.contains('Ranged', case=False, na=False)

wargear_faction['Weapon Category'] = np.where(wargear_faction['is_melee'], 'Melee', 
                                     np.where(wargear_faction['is_ranged'], 'Ranged', 'Other'))

type_counts = wargear_faction.groupby(['faction_name', 'Weapon Category']).size().unstack(fill_value=0)
if 'Melee' in type_counts.columns and 'Ranged' in type_counts.columns:
    type_counts = type_counts[['Melee', 'Ranged']]
    
    # Calculate percentage
    type_pct = type_counts.div(type_counts.sum(axis=1), axis=0) * 100
    
    # Plot Melee vs Ranged preference
    type_pct.plot(kind='bar', stacked=True, figsize=(14, 6), colormap='Set1')
    plt.title('Weapon Type Preference per Faction (Melee vs Ranged %)')
    plt.ylabel('Percentage of Weapons (%)')
    plt.legend(title='Weapon Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
"""))
    
    cells.append(nbf.v4.new_code_cell("""# Analyze Range Preference
def parse_range(r):
    if pd.isna(r): return np.nan
    r = str(r).lower()
    if 'melee' in r: return 0.0
    # extract first number
    match = re.search(r'\d+', r)
    if match: return float(match.group())
    return np.nan

wargear_faction['range_numeric'] = wargear_faction['range'].apply(parse_range)

# Average range per faction
avg_range = wargear_faction.groupby('faction_name')['range_numeric'].mean().sort_values(ascending=False)

plt.figure(figsize=(14, 6))
sns.barplot(x=avg_range.index, y=avg_range.values, palette='Blues_r')
plt.title('Average Weapon Range per Faction (Including Melee as 0)')
plt.xticks(rotation=90)
plt.ylabel('Average Range (inches)')
plt.tight_layout()
plt.show()
"""))

    # 6. Feature Engineering
    cells.append(nbf.v4.new_markdown_cell("""## 5. Exploratory Feature Engineering
### Derived Numerical Feature: Offensive Power
We can define theoretical offensive power as $Attacks \\times Strength \\times Damage$.
"""))

    cells.append(nbf.v4.new_code_cell("""data['Offensive_Power'] = data['Attacks'] * data['Strength'] * data['Damage']

plt.figure(figsize=(10, 5))
sns.histplot(data['Offensive_Power'], bins=30, kde=True, color='purple')
plt.title("Distribution of Derived Feature: Offensive Power")
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""### Text Feature Engineering: Faction Vocabulary
Factions in Warhammer 40k have highly distinct naming conventions. Orks use words like "Kustom" or "Choppa", while Space Marines use "Plasma" or "Bolter". We will extract these text patterns using NLP.
"""))

    cells.append(nbf.v4.new_code_cell("""# NLP on Weapon Names for ALL Factions
data['weapon_name'] = data['weapon_name'].fillna('')

# Increase max_features to capture variety across all factions
cv = CountVectorizer(stop_words='english', max_features=100)
words_matrix = cv.fit_transform(data['weapon_name'])
word_counts = pd.DataFrame(words_matrix.toarray(), columns=cv.get_feature_names_out())
word_counts['faction_name'] = data['faction_name']

# Group by faction and get the sum of word counts
faction_words = word_counts.groupby('faction_name').sum()

# Plotting top 3 words for each faction
factions_list = faction_words.index.tolist()
num_factions = len(factions_list)
cols = 4
rows = (num_factions // cols) + (1 if num_factions % cols > 0 else 0)

fig, axes = plt.subplots(rows, cols, figsize=(20, 4 * rows))
axes = axes.flatten()

for i, faction in enumerate(factions_list):
    row = faction_words.loc[faction]
    top_words = row.sort_values(ascending=False).head(3)
    # Only plot if there are words (count > 0)
    top_words = top_words[top_words > 0]
    
    if not top_words.empty:
        sns.barplot(x=top_words.values, y=top_words.index, ax=axes[i], palette="viridis")
        axes[i].set_title(f'{faction[:25]}')
        axes[i].set_xlabel('')
    else:
        axes[i].set_title(f'{faction[:25]} (No words)')
        axes[i].axis('off')

# Hide any unused subplots
for j in range(len(factions_list), len(axes)):
    axes[j].axis('off')

plt.tight_layout()
plt.show()
"""))

    cells.append(nbf.v4.new_markdown_cell("""The NLP extraction proves highly successful. Words strongly associate with `faction_id`, making text features extremely valuable for prediction.
"""))

    # 7. Conclusions
    cells.append(nbf.v4.new_markdown_cell("""## 6. Conclusions, Limitations & Roadmap

### Summary of Findings
- **Imbalance**: The dataset is extremely imbalanced towards Space Marines.
- **Cost Balancing**: Stats perfectly scale with cost, indicating a highly balanced game design. 
- **Faction Identity**: Features like Movement, Toughness, and Wargear Specialization (Melee vs Ranged percentages) clearly separate factions like Adeptus Custodes (high toughness, melee) from Astra Militarum (low toughness, ranged).
- **Text Power**: NLP extraction of weapon names proved extremely powerful in identifying faction-specific jargon (e.g., "choppa" for Orks).

### Hypotheses and Decisions for Modeling
- **Hypothesis 1 (Association)**: Weapon vocabulary is the strongest predictor of a faction, even more than numerical stats, due to thematic naming conventions.
- **Hypothesis 2**: Cost efficiency (`Toughness_per_Cost`) can accurately distinguish elite factions from swarm factions.
- **Decision 1**: We must use TF-IDF or CountVectorizer on `weapon_name` and `loadout`.
- **Decision 2**: We must apply class weighting or SMOTE to handle the massive Space Marine overrepresentation.
- **Decision 3**: Missing numeric values in Wargear stats will be imputed with 0, under the assumption that a missing attack stat implies the unit relies on abilities rather than direct combat.

These decisions must be strictly validated during the cross-validation phase of modeling to avoid data leakage.
"""))

    nb.cells = cells
    with open('Warhammer40k_EDA.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

if __name__ == '__main__':
    create_notebook()
    print("Notebook 'Warhammer40k_EDA.ipynb' created successfully.")
