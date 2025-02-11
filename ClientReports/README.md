# Generate Client Reports

Run the `generate_client_reports.py` script to generate client reports in pdf format. The script will:

```bash
# Export reports
python generate_reports.py export <username> <password> <server> <client> <cut_off_date> [options]

# Merge PDFs
python generate_reports.py merge [options]
```

**Export Command Arguments**:

Required:

- `username`: Tableau server username
- `password`: Tableau server password
- `server`: Tableau server address (without https:// and domain suffix)
- `client`: Client CMR number or 'all' for all clients
- `cut_off_date`: Cut-off date for reports (YYYY-MM-DD format)

Optional:

- `--page`, `-p`: Page number(s) to generate (1-5 or 'all', default: '1')
- `--site`, `-s`: Tableau server site name
- `--language`, `-lang`: Report language ('EN', 'FR', 'all', default: 'EN')
- `--output`, `-o`: Output directory path
- `--log-level`, `-l`: Logging level ('debug', 'info', 'error', default: 'info')

**Merge Command Arguments**:

Optional:

- `--language`, `-lang`: Language to merge ('EN', 'FR', 'all', default: 'EN')
- `--output`, `-o`: Output directory path
- `--log-level`, `-l`: Logging level ('debug', 'info', 'error', default: 'info')

**Examples**:

```bash
# Export page 1 reports for all clients in English for the 2024-25 Q3 fiscal year
python generate_reports.py export jdoe password123 tableau all 2024-03-31 --language EN

# Export all pages for a client in both languages for the 2024-25 Q3 fiscal year
python generate_reports.py export jdoe password123 tableau 12345 2024-03-31 --page all --language all

# Merge all English reports in the reports folder
python generate_reports.py merge --language EN --output ./reports

# Merge PDFs for all languages in the current folder
python generate_reports.py merge --language all
```
