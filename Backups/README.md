# Export Workbooks

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
