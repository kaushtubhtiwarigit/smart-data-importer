# Known Limitations - Smart Data Importer

## Current Implementation Gaps

### 1. Duplicate Detection
**Status:** Partial Implementation
- ✅ Exact duplicates are removed via `pandas.drop_duplicates()`
- ❌ Fuzzy matching NOT implemented
- ❌ No similarity threshold configuration
- ❌ Cannot detect "John Smith" vs "Jon Smith" as duplicates

**Workaround:** Use exact matching only

**Future:** Implement Levenshtein distance with fuzzywuzzy library

---

### 2. Schema Support
**Status:** Single Schema Only
- ✅ CRM schema works (name, email, phone, company, address)
- ❌ E-commerce schema NOT implemented
- ❌ HR schema NOT implemented  
- ❌ Custom schema NOT user-configurable

**Workaround:** Modify `target_schema` dict in `data_cleaner.py` manually

**Future:** Add schema selector in UI and configurable schema files

---

### 3. Data Persistence
**Status:** No Database
- ✅ Files saved to `cleaned/` folder
- ❌ No database storage
- ❌ No history tracking
- ❌ Cannot query past uploads

**Workaround:** Files are accessible on filesystem

**Future:** Add SQLite database for upload history and audit trail

---

### 4. Batch Processing
**Status:** Single File Only
- ✅ One CSV at a time
- ❌ Cannot process multiple files
- ❌ Cannot merge multiple CSVs
- ❌ No folder upload

**Workaround:** Process files individually

**Future:** Add batch upload and merging capabilities

---

### 5. Mapping Preview
**Status:** No Interactive Review
- ✅ LLM generates mappings
- ❌ Cannot preview before applying
- ❌ Cannot manually adjust mappings
- ❌ No confidence scores shown

**Workaround:** Mappings are logged to console

**Future:** Add UI for reviewing and editing mappings before processing

---

### 6. LLM Robustness
**Status:** Basic Error Handling
- ✅ Falls back to rule-based mapping on error
- ❌ No retry logic
- ❌ No structured output enforcement
- ❌ Parsing can fail on malformed JSON

**Workaround:** Gemini usually returns valid JSON

**Future:** Use Gemini structured output mode, add retries

---

### 7. File Validation
**Status:** Basic Validation
- ✅ File type checked (CSV only)
- ✅ File size limit (16MB)
- ❌ No encoding detection/handling
- ❌ No malformed CSV recovery
- ❌ No empty file prevention

**Workaround:** Ensure CSVs are well-formed UTF-8

**Future:** Add encoding detection, better error messages

---

### 8. Performance
**Status:** Not Optimized
- ✅ Works for files up to ~10K rows
- ❌ Slow on 100K+ rows (loads entire CSV in memory)
- ❌ No streaming processing
- ❌ No progress indicators for large files

**Workaround:** Split large files into smaller chunks

**Future:** Implement chunked processing with progress bars

---

### 9. Security
**Status:** Basic Security
- ✅ API key not logged
- ✅ File type validation
- ❌ No rate limiting
- ❌ No file content scanning
- ❌ Uploaded files not automatically deleted

**Workaround:** Run in trusted environment only

**Future:** Add rate limiting, virus scanning, auto-cleanup

---

### 10. Testing
**Status:** Unit Tests Only
- ✅ Unit tests for cleaning functions
- ❌ No integration tests
- ❌ No end-to-end tests
- ❌ No test fixtures with various edge cases

**Workaround:** Manual testing with sample CSVs

**Future:** Add pytest integration tests and more fixtures

---

## Not Implemented Features from README

The following features are **mentioned in README but NOT implemented**:

1. ❌ Fuzzy duplicate detection with Levenshtein distance
2. ❌ E-commerce, HR, and custom schemas
3. ❌ Interactive mapping preview/editing
4. ❌ Batch file processing
5. ❌ Database persistence
6. ❌ API endpoints for programmatic access
7. ❌ ML-based duplicate detection
8. ❌ Integration with CRM APIs (Salesforce, HubSpot)

---

## Honest Use Cases

### ✅ Good For:
- Cleaning small-medium CSVs (< 10K rows)
- Standardizing CRM contact data
- One-time data imports
- Proof-of-concept demonstrations

### ❌ Not Suitable For:
- Production data pipelines
- Large-scale ETL (100K+ rows)
- Mission-critical data processing
- Multi-schema data warehousing
- Automated scheduled imports

---

## Recommendations

**For Portfolio/Interviews:**
- Demonstrate what **actually works**
- Explain design decisions
- Discuss **future improvements** as learning opportunities
- Be honest about limitations

**For Production Use:**
- Implement missing features before deploying
- Add comprehensive error handling
- Create backup/rollback mechanisms
- Add monitoring and logging
- Security audit required

---

**Last Updated:** September 22, 2026
