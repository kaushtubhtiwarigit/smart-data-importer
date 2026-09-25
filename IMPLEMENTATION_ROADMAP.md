# Smart Data Importer - Implementation Roadmap

**Current Status**: 70% Complete  
**Priority Fixes**: Listed below

## Missing Features Analysis

### ✅ What Already Works
- CSV upload and parsing
- Gemini API integration for schema mapping
- CRM schema support
- Basic data cleaning (name, email, phone normalization)
- Exact duplicate detection
- Data validation
- Quality reporting
- CSV export

### ❌ What's Missing

#### Priority 1: Critical Gaps (Must Fix)

**1. Fuzzy Duplicate Detection**
- **Current**: Only exact duplicates removed
- **Need**: Fuzzy name matching, email/phone similarity
- **Implementation**: Use `fuzzywuzzy` or `rapidfuzz`
- **Effort**: 2-3 hours

**2. Multiple Schema Support**
- **Current**: Only CRM schema hardcoded
- **Need**: E-commerce, HR, Custom schemas
- **Implementation**: Schema configuration system
- **Effort**: 3-4 hours

**3. API Endpoints Don't Match Documentation**
- **Current**: Simple `/process` and `/download`
- **Documented**: `/api/upload`, `/api/map`, `/api/clean`, `/api/download/:id`
- **Implementation**: Restructure Flask routes
- **Effort**: 2 hours

#### Priority 2: Important Features

**4. Interactive Mapping Review UI**
- **Current**: Auto-mapping with no review
- **Need**: UI to review/edit mappings before applying
- **Implementation**: Frontend component + API endpoint
- **Effort**: 4-5 hours

**5. LLM Response Robustness**
- **Current**: Basic regex extraction with fallback
- **Need**: Structured JSON, validation, retries
- **Implementation**: Better prompts + error handling
- **Effort**: 2 hours

**6. Upload History/Database**
- **Current**: No tracking
- **Need**: SQLite database tracking uploads
- **Implementation**: Database schema + CRUD operations
- **Effort**: 2-3 hours

#### Priority 3: Nice to Have

**7. Batch Processing**
- **Current**: One CSV at a time
- **Need**: Multiple CSV merge capability
- **Effort**: 3 hours

**8. Phone Normalization Improvements**
- **Current**: US-only assumption
- **Need**: Configurable country code
- **Effort**: 1 hour

**9. File Cleanup/Security**
- **Current**: Files persist indefinitely
- **Need**: Automatic cleanup, size limits
- **Effort**: 1 hour

**10. Integration Tests**
- **Current**: Basic unit tests only
- **Need**: End-to-end workflow tests
- **Effort**: 2 hours

---

## Implementation Plan

### Phase 1: Quick Wins (6-7 hours)

**Goal**: Fix most visible gaps

1. ✅ Add fuzzy duplicate detection
2. ✅ Add E-commerce schema
3. ✅ Add HR schema
4. ✅ Improve LLM response handling
5. ✅ Fix phone normalization (country configurable)

### Phase 2: Core Features (8-10 hours)

**Goal**: Make it production-worthy

6. ✅ Implement proper API endpoints
7. ✅ Add upload history database
8. ✅ Create interactive mapping review
9. ✅ Add batch processing
10. ✅ File cleanup and security

### Phase 3: Polish (3-4 hours)

**Goal**: Interview-ready

11. ✅ Integration tests
12. ✅ Updated documentation
13. ✅ Demo script
14. ✅ Known limitations doc

---

## Realistic Approach for Now

Given time constraints, let's focus on **Phase 1** fixes that give maximum impact:

### Must-Do (Today)

1. **Fuzzy Duplicates** - Most visible gap
2. **Multiple Schemas** - Core feature claim
3. **Better LLM Handling** - Improves reliability

### Should-Do (If Time)

4. **Upload History** - Shows system thinking
5. **API Restructure** - Matches documentation

### Document (Instead of Build)

6. **Interactive Mapping** - Document in "Future Features"
7. **Batch Processing** - Document in "Future Features"

---

## Next Steps

Starting with **Fuzzy Duplicate Detection**...

