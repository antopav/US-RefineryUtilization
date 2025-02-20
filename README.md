# US-RefineryUtilization


**Analyze U.S. and Regional Refinery Utilization for Commodity Trading**

This project leverages the EIA API to fetch and visualize weekly refinery utilization rates for the U.S. and Petroleum Administration for Defense Districts (PADDs), providing actionable insights for commodity traders. It demonstrates my ability to integrate quantitative analysis, Python programming, and domain expertise in commodity markets.

---

##  Key Features
- Fetches real-time refinery utilization data for the U.S. and PADDs (1–5) via EIA API v2.
- Visualizes utilization trends (2022–2025) to highlight regional patterns, with emphasis on Gulf Coast (PADD 3) due to its oil market significance.
- Employs data processing and visualization to support trading decisions, showcasing coding proficiency.

---

##  Usage
1. Obtain an EIA API key from [EIA Open Data](https://www.eia.gov/opendata/register.cfm).
2. Set your API key as an environment variable:
   - **Windows**: `set EIA_API_KEY=your_key_here` (in CMD)
   - **Mac/Linux**: `export EIA_API_KEY=your_key_here`
   - Alternatively, use a `.env` file with `EIA_API_KEY=your_key_here` and install `python-dotenv`.
3. Install dependencies:
   ```bash
   pip install requests pandas matplotlib python-dotenv