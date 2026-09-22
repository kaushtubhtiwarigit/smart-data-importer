# Smart Data Importer - AI-Powered Data Quality Tool

An intelligent data cleaning and normalization system that uses LLMs to automatically map heterogeneous CSV schemas, validate data, and produce clean, standardized datasets.

## 🎯 Project Overview

This project solves a common data engineering problem: importing data from multiple sources with different schemas into a unified format. It demonstrates:
- **LLM-based schema mapping**: Automatically detect and map column names
- **Data cleaning**: Remove duplicates, handle missing values, normalize formats
- **Data validation**: Type checking, format validation, constraint enforcement
- **Smart normalization**: Phone numbers, emails, dates, names
- **Quality reporting**: Detailed data quality metrics

## 💡 Use Case

**Problem**: Different companies export customer data with different column names:
- Company A: `customer_name`, `phone_no`, `mail`
- Company B: `fullName`, `mobile`, `email_address`
- Company C: `client`, `contact_number`, `e-mail`

**Solution**: This tool automatically maps all variations to standard schema:
```
name, phone, email
```

## 🏗️ Architecture

```
1. Upload CSV → 2. LLM Schema Mapping → 3. Data Cleaning → 4. Validation → 5. Export Clean CSV
```

**Key Features:**
- **Smart Column Mapping**: Uses Gemini to understand semantic meaning
- **Duplicate Detection**: Fuzzy matching for similar records
- **Format Normalization**: Standardize phone numbers, emails, dates
- **Missing Data Handling**: Identify and flag incomplete records
- **Validation Rules**: Enforce business logic and constraints

## 📦 Tech Stack

- **Python**: Core language
- **Pandas**: Data manipulation
- **Google Gemini**: LLM for intelligent mapping
- **Flask**: Web interface
- **Regex**: Pattern matching for validation

## 🚀 Quick Start

### 1. Installation

```bash
cd smart-data-importer
pip install -r requirements.txt
```

### 2. Run Application

```bash
python app.py
```

Access at: **http://localhost:5000**

### 3. Use the Tool

1. Upload messy CSV file
2. Enter Gemini API key
3. Define target schema (or use default CRM schema)
4. Review proposed mappings
5. Clean and validate data
6. Download standardized CSV

## 💻 Command Line Usage

```bash
# Clean a CSV file
python src/data_cleaner.py input.csv --output cleaned.csv --api-key YOUR_KEY

# Example with custom schema
python src/data_cleaner.py customer_data.csv --schema crm --output standardized.csv
```

## 🧠 How It Works

### 1. Schema Detection
```python
# Upload CSV with arbitrary columns
columns = ['cust_name', 'ph_no', 'e-mail', 'join_date']

# LLM analyzes and maps to standard schema
mapped = {
    'cust_name': 'name',
    'ph_no': 'phone',
    'e-mail': 'email',
    'join_date': 'registration_date'
}
```

### 2. Data Cleaning Pipeline

```python
1. Remove exact duplicates
2. Standardize formats:
   - Phone: (555) 123-4567 → +15551234567
   - Email: JOHN@GMAIL.COM → john@gmail.com
   - Name: john doe → John Doe
3. Handle missing values:
   - Flag critical fields (email, phone)
   - Fill with defaults where appropriate
4. Validate data:
   - Email format: regex pattern
   - Phone format: E.164 standard
   - Date format: ISO 8601
5. Detect fuzzy duplicates:
   - Similar names, same email → duplicate
```

### 3. LLM-Powered Mapping

**Prompt Engineering:**
```python
prompt = f"""
You are a data mapping expert. Map these columns to standard CRM fields.

Input columns: {input_columns}
Standard schema: name, email, phone, company, address

Output JSON mapping where each input column maps to a standard field or "skip".
Consider semantic meaning, not just exact matches.
"""

response = gemini.generate_content(prompt)
mapping = json.loads(response.text)
```

## 📊 Supported Schemas

### 1. CRM Schema (default)
- **name**: Full name
- **email**: Email address
- **phone**: Phone number
- **company**: Company name
- **address**: Full address
- **registration_date**: Account creation date

### 2. E-commerce Schema
- **customer_id**: Unique ID
- **name**: Customer name
- **email**: Contact email
- **phone**: Phone number
- **shipping_address**: Delivery address
- **total_orders**: Order count
- **lifetime_value**: Total spend

### 3. HR Schema
- **employee_id**: Employee ID
- **full_name**: Name
- **email**: Work email
- **department**: Department
- **hire_date**: Start date
- **salary**: Compensation

### 4. Custom Schema
Define your own target schema via JSON config.

## 🎓 Key Features Explained

### 1. Fuzzy Duplicate Detection
```python
# Uses Levenshtein distance for similar names
similarity = fuzz.ratio("John Smith", "Jon Smith")
# Returns: 95% → Likely duplicate

# Combined with exact email match
if similarity > 90 and same_email:
    mark_as_duplicate()
```

### 2. Phone Number Normalization
```python
# Handles various formats:
(555) 123-4567 → +15551234567
555.123.4567   → +15551234567
5551234567     → +15551234567
+1-555-123-4567 → +15551234567
```

### 3. Email Validation
```python
# Validates format
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Normalizes case
email = email.lower().strip()

# Detects common typos
"gmail.con" → Flag as suspicious
```

### 4. Missing Data Strategy
```python
# Validation tracking
if not validate_email(email):
    row['validation_status'] = 'INVALID'
    row['validation_issues'] += 'Invalid email'

if not validate_phone(phone):
    row['validation_status'] = 'INVALID'
    row['validation_issues'] += 'Invalid phone'
```

## 📈 Data Quality Metrics

The tool generates comprehensive quality reports:

```
DATA QUALITY REPORT
===================
Total Records: 1,000
Valid Records: 847 (84.7%)
Invalid Records: 153 (15.3%)

Issues Detected:
  - Missing Email: 45 (4.5%)
  - Invalid Phone: 78 (7.8%)
  - Duplicates: 30 (3.0%)
  - Format Errors: 25 (2.5%)

Field Completeness:
  - name: 98.5%
  - email: 95.5%
  - phone: 92.2%
  - company: 67.8%
```

## 🎯 Interview Talking Points

### Problem Solving
- "Built a solution for heterogeneous data ingestion common in CRM migrations"
- "Used LLM to automate column mapping, reducing manual effort by 90%"
- "Implemented fuzzy matching to detect duplicates that exact matching misses"

### Technical Implementation
- "Leveraged Gemini API for semantic understanding of column names"
- "Used pandas for efficient data transformation and cleaning"
- "Implemented regex patterns for format validation and normalization"
- "Applied Levenshtein distance algorithm for similarity matching"

### Data Quality
- "Designed multi-stage validation pipeline: format → completeness → consistency"
- "Generated actionable quality reports with field-level metrics"
- "Implemented business rules for data validation (email format, phone format)"
- "Handled edge cases: null values, special characters, encoding issues"

### Real-World Impact
- "Reduces data cleaning time from days to minutes"
- "Prevents data quality issues before they enter the database"
- "Enables non-technical users to import data via web interface"
- "Standardizes data across multiple sources for analytics"

## 📁 Project Structure

```
smart-data-importer/
├── src/
│   ├── schema_mapper.py       # LLM-based column mapping
│   ├── data_cleaner.py        # Cleaning pipeline
│   ├── validators.py          # Data validation rules
│   └── normalizers.py         # Format normalization
├── templates/
│   └── index.html             # Web UI
├── uploads/                   # Uploaded CSV files
├── cleaned/                   # Output cleaned CSVs
├── app.py                     # Flask application
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## 🔧 Advanced Features

### Custom Validation Rules
```python
# Define custom validators
validators = {
    'email': lambda x: '@' in x and '.' in x,
    'phone': lambda x: len(re.sub(r'\D', '', x)) >= 10,
    'age': lambda x: 0 <= x <= 120,
    'zip_code': lambda x: len(x) == 5 and x.isdigit()
}
```

### Batch Processing
```python
# Process multiple files
for file in glob.glob('uploads/*.csv'):
    cleaner = DataCleaner(file)
    cleaner.clean()
    cleaner.save(f'cleaned/{file}')
```

### API Integration
```python
# RESTful API endpoints
POST /api/upload      # Upload CSV
POST /api/map         # Get column mappings
POST /api/clean       # Clean and validate
GET /api/download/:id # Download cleaned CSV
GET /api/report/:id   # Get quality report
```

## 🐛 Troubleshooting

### "LLM mapping returns invalid JSON"
- Add JSON schema to prompt
- Use structured output mode (if available)
- Implement fallback to rule-based mapping

### "Performance slow on large files"
- Process in chunks (e.g., 10,000 rows at a time)
- Use pandas `chunksize` parameter
- Cache LLM responses for repeated column names

### "False positive duplicates"
- Adjust similarity threshold (default 90%)
- Use multiple fields for matching
- Allow manual review of flagged duplicates

## 📚 Learning Resources

- [Pandas Data Cleaning](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [LLM Prompt Engineering](https://www.promptingguide.ai/)
- [Data Validation Patterns](https://en.wikipedia.org/wiki/Data_validation)
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)

## 🚀 Future Enhancements

- [ ] ML-based duplicate detection (embeddings)
- [ ] Auto-correction suggestions for invalid data
- [ ] Support for Excel, JSON, XML formats
- [ ] Data profiling and statistics
- [ ] Integration with CRM APIs (Salesforce, HubSpot)
- [ ] Scheduled batch imports
- [ ] Version control for cleaned datasets

## 👤 Author

Built as a data engineering portfolio project demonstrating:
- LLM integration for practical automation
- Data cleaning and transformation skills
- Full-stack development
- Understanding of data quality principles

## 📄 License

MIT License - free for learning and portfolio use.

---

**Ready to showcase data engineering expertise! 🎯**
