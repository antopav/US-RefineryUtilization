import requests
import pandas as pd
import matplotlib.pyplot as plt
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'refinery_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Your API key

api_key = os.getenv('EIA_API_KEY')


# Series IDs (U.S. total + PADDs)
series_ids = {
    'U.S. Total': 'WPULEUS3',  # U.S. Percent Utilization
    'PADD 1': 'W_NA_YUP_R10_PER',  # East Coast
    'PADD 2': 'W_NA_YUP_R20_PER',  # Midwest
    'PADD 3': 'W_NA_YUP_R30_PER',  # Gulf Coast
    'PADD 4': 'W_NA_YUP_R40_PER',  # Rocky Mountain
    'PADD 5': 'W_NA_YUP_R50_PER'   # West Coast
}

# Store dataframes
dfs = {}

# Base URL
base_url = "https://api.eia.gov/v2/petroleum/pnp/wiup/data/"

# Fetch data
logger.info("Starting data fetch")
for name, series_id in series_ids.items():
    logger.info(f"Fetching data for {name} with series {series_id}")
    url = f"{base_url}?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    try:
        response = requests.get(url).json()
        if 'response' not in response or 'data' not in response['response']:
            logger.error(f"API call failed for {name}: {response}")
            raise ValueError(f"API call failed for {name}")
        
        data = response['response']['data']
        if not data:
            logger.warning(f"No data returned for {name}")
            continue
        
        df = pd.DataFrame(data)[['period', 'value']]
        df.columns = ['Date', 'Utilization_Rate']
        df['Date'] = pd.to_datetime(df['Date'])
        df['Utilization_Rate'] = pd.to_numeric(df['Utilization_Rate'], errors='coerce')
        df = df.sort_values('Date').dropna(subset=['Utilization_Rate'])
        
        if df.empty:
            logger.warning(f"Processed data for {name} is empty after cleaning")
            continue
        
        # Analysis
        df['4W_MA'] = df['Utilization_Rate'].rolling(window=4).mean()
        df['Volatility'] = df['Utilization_Rate'].rolling(window=4).std()
        dfs[name] = df
        logger.info(f"Successfully processed data for {name}: {len(df)} rows")
    except Exception as e:
        logger.error(f"Error processing {name}: {str(e)}")
        continue

if not dfs:
    logger.error("No data processed successfully. Exiting.")
    raise SystemExit("No data to plot.")

# Create dashboard
logger.info("Generating dashboard")
fig = plt.figure(figsize=(18, 12), constrained_layout=True)
gs = fig.add_gridspec(3, 3)  # 3 rows, 3 columns

# Plot 1-6: Individual Trends (U.S. + PADDs)
axes = []
for i, (name, df) in enumerate(dfs.items()):
    row = i // 3
    col = i % 3
    if i < 6:  # Limit to 6 slots (U.S. + 5 PADDs)
        ax = fig.add_subplot(gs[row, col])
        ax.plot(df['Date'], df['Utilization_Rate'], label='Utilization (%)', color='blue')
        ax.plot(df['Date'], df['4W_MA'], label='4W MA', linestyle='--', color='orange')
        ax.fill_between(df['Date'], df['Utilization_Rate'] - df['Volatility'], 
                        df['Utilization_Rate'] + df['Volatility'], color='blue', alpha=0.1, label='Volatility')
        ax.set_title(f'{name}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Utilization (%)')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        axes.append(ax)
        logger.info(f"Added trend plot for {name}")

# Plot 7: Stacked Comparison (bottom left, enhanced)
ax_stack = fig.add_subplot(gs[2, 0:2])
colors = ['#4682b4', '#87ceeb', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']  # Muted blues/greens, bold for PADD 3
for i, (name, df) in enumerate(dfs.items()):
    # Filter to last 3 years for clarity
    recent_df = df[df['Date'] >= '2022-01-01']
    if name == 'PADD 3':  # Highlight Gulf Coast (PADD 3)
        ax_stack.plot(recent_df['Date'], recent_df['Utilization_Rate'], label=name, 
                      color=colors[i], linewidth=2.5, linestyle='solid')
    else:
        ax_stack.plot(recent_df['Date'], recent_df['Utilization_Rate'], label=name, 
                      color=colors[i], linewidth=1.5, linestyle='solid')
ax_stack.set_title('U.S. & PADD Refinery Utilization (2022–2025)')
ax_stack.set_xlabel('Date')
ax_stack.set_ylabel('Utilization (%)')
ax_stack.legend(title='Regions', fontsize=8, loc='upper left', bbox_to_anchor=(1, 1))
ax_stack.grid(True, alpha=0.3)
logger.info("Added enhanced stacked comparison plot")

# Plot 8: Volatility Bar Chart (bottom right)
ax_bar = fig.add_subplot(gs[2, 2])
volatility = {name: df['Volatility'].mean() for name, df in dfs.items()}
volatility_std = {name: df['Volatility'].std() for name, df in dfs.items()}
ax_bar.bar(volatility.keys(), volatility.values(), yerr=volatility_std.values(), 
           capsize=5, color='skyblue', edgecolor='black')
ax_bar.set_title('Avg Volatility by Region')
ax_bar.set_xlabel('Region')
ax_bar.set_ylabel('Volatility (%)')
ax_bar.grid(axis='y', alpha=0.3)
ax_bar.tick_params(axis='x', rotation=45)
logger.info("Added volatility bar chart")

# Finalize and save
plt.savefig('refinery_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()
logger.info("Dashboard saved as refinery_dashboard.png and displayed")