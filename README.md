# Fiber Construction Sequencing Comparison Tool

A Streamlit application that compares two fiber construction sequencing methods: "Start Date-Driven" vs. "Lowest Cost First" with interactive visualizations and milestone tracking.

## Features

- **Dual Sequencing Methods**: Compare Start Date-Driven vs. Lowest Cost First approaches
- **Interactive Visualizations**: Gantt charts, milestone tracking, and progress analytics
- **What-If Scenarios**: Adjustable parameters for exploration
- **Business-Friendly Interface**: Clean, executive-ready dashboard
- **Data Import**: Support for CSV/XLSX files with custom data

## Setup

1. **Activate Virtual Environment**:

   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:

   ```bash
   streamlit run app.py
   ```

## Data Format

The app expects data with the following columns:

- Segment Name
- Start Date (CSD)
- Duration (BD)
- Estimated Production Rate (EstRate)
- Cost Per Mile
- Segment Cost
- Miles

## Usage

1. Upload your data file or use the sample data
2. Adjust parameters using the sidebar controls
3. Compare the two sequencing methods side-by-side
4. Analyze milestone achievements and cost implications
5. Export results as needed

## Project Structure

```
jamesstreamlit/
├── app.py                 # Main Streamlit application
├── data_generator.py      # Sample data generation
├── sequencing_logic.py    # Core sequencing algorithms
├── visualizations.py      # Chart and plot functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── venv/                 # Virtual environment
```
