# Tableau Workbook Export Tool

A collection of Python scripts to:

1. Export workbooks from a Tableau server while preserving the project hierarchy structure.
2. Generate client reports

## Prerequisites

- Python 3.6 or higher
- Access to a Tableau server
  - Adminstrator permissions to download workbooks

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Export Workbooks

Run the `export_workbooks.py` script to export workbooks from a Tableau server. The script will create a directory structure that mirrors the project hierarchy on the server.

```bash
python export_workbooks.py --server <server-url> --username <username> --password <password> --output <output-directory>
```

**Arguments**:

- ```username```: Your Tableau server username
- ```password```: Your Tableau server password
- ```server```: Tableau server address (without https:// and domain suffix)

**Optional Args**:

- ```--site``` or ```-s```: Tableau site name
- ```--log-level``` or ```-l```: Set logging level (debug, info, or error)

**Example**:

```bash
cd Backups
python .\export_tableau_tsc.py jdoe password123 tableau-dev --site mysitename --log-level debug
```

**Output**:
The script will:

1. Connect to the specified Tableau server
2. Download all workbooks
3. Save them in a directory structure matching the project hierarchy
4. Create a 'workbooks' directory in the current path
5. Preserve project names as folder names
6. Save workbooks as .twbx files

**Notes**:

- SSL verification is disabled by default
- Special characters in names are replaced with underscores
- Names are truncated at the first forward slash

### Generate Client Reports

Run the `generate_client_reports.py` script to generate client reports in pdf format. The script will:

1. Read a list of client names from a CSV file
2. Generate a report for each client
3. Optionally merge all reports of each clients into a single PDF

```bash
cd ClientReports
python .\generate_client_reports.py <username> <password> <client> <cut_off_date> --page <page_number> --language <language> --output <output_directory> --site <site_name> --log-level <log_level> --merge
```

**Arguments**:

- ```username```: Tableau server username for authentication
- ```password```: Tableau server password for authentication
- ```server```: Tableau server address/URL
- ```client```: Client CMR number to generate reports for, or 'all' for all clients
- ```cut_off_date```: Cut-off date for reports in YYYY-MM-DD format. Maps to fiscal quarters:  
  - June 30th: Q1  
  - September 30th: Q2
  - December 31st: Q3
  - March 31st: Q4

**Optional Args**:

- ```--page```, ```-p```: Page number(s) to generate.
  - Options: '1','2','3','4','5','all'. Default: '1'
- ```--language```, ```-lang```: Language of reports.
  - Options: 'EN','FR','all'. Default: 'EN'  
- ```--output```, ```-o```: Output directory path. Default: Current directory
- ```--site```, ```-s```: Tableau server site name. Default: None
- ```--log-level```, ```-l```: Logging level.
  - Options: 'debug','info','error'. Default: 'info'
