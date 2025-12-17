# 🟢 𝗕𝗶𝗼𝗴𝗲𝗻𝗲𝘀𝘆𝘀 𝗖𝗼𝗿𝗲 𝘃𝟮.𝟬: 𝗗𝗮𝘁𝗮 𝗘𝗧𝗟 𝗘𝗻𝗴𝗶𝗻𝗲𝗲𝗿𝗶𝗻𝗴 𝗮𝗻𝗱 𝗠𝗼𝗱𝘂𝗹𝗮𝗿 𝗔𝗿𝗰𝗵𝗶𝘁𝗲𝗰𝘁𝘂𝗿𝗲

##  Project Overview
**Biogenesys Core v2.0** focuses on transforming a monolithic process into a **professional, modular ETL pipeline**. The goal of this version was to build a robust engine capable of extracting raw data, applying complex business rules, and validating data quality to produce a **final, clean dataset** ready for any storage destination.

## 🚀 Key Engineering Features
* **Modular Architecture:** The pipeline is organized into a `src/` package with a clear separation of concerns (Extract, Transform, Validate, Load).
* **Data Quality Layer (`validate.py`):** Implementation of a dedicated "Quality Test" module to ensure data integrity and schema consistency before the final output.
* **Feature Engineering & Cleaning:** Advanced logic in `transform.py` to handle data type conversions, null values, and business-specific transformations.
* **CLI Orchestrator:** A central `run_pipeline.py` script that manages the execution flow, ensuring a repeatable and reliable process.

## 📂 Project Structure
```text
├── Biogenesys_Saga/
│   ├── data_latinoamerica.csv   # Raw dataset (Input)
│   ├── src/                     # Modular Core Logic
│   │   ├── __init__.py 
│   │   ├── extract.py           # Data Ingestion Module
│   │   ├── transform.py         # Cleaning & Feature Engineering
│   │   ├── validate.py          # Data Quality Layer (Quality Tests)
│   │   └── load.py              # Final Clean CSV Generation (Local)
│   └── run_pipeline.py          # The CLI Orchestrator (Main Entry)
```
## 🛠️ Tech Stack 
Language: Python 3.x

Data Processing: Pandas, NumPy

Development Pattern: Modular Programming / Functional ETL


## ⚙️ How to Run

Install dependencies:
```text Bash
        pip install pandas numpy
```

Execute the pipeline:
```text Bash
        python Biogenesys_Saga/run_pipeline.py
 ```

**The script will process the raw data, run quality tests, and export the clean dataset.**

###  📈 Impact
This version establishes the Engineering Foundation of the project. By separating the logic into modules and adding a validation layer, the pipeline ensures that the output is high-quality and "analysis-ready." This clean output serves as the primary source for future cloud deployments.
