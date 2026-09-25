"""
Smart Data Cleaner with LLM-powered schema mapping

Supports multiple schemas: CRM, E-commerce, HR, and Custom
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple
import json
import google.generativeai as genai

from schemas import get_schema, get_custom_schema, list_schemas


class SchemaMapper:
    """Map heterogeneous schemas using LLM"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize with Gemini API"""
        genai.configure(api_key=gemini_api_key)
        self.llm = genai.GenerativeModel('gemini-pro')
        
    def map_columns(self, input_columns: List[str], target_schema: Dict[str, str]) -> Dict[str, str]:
        """
        Map input columns to target schema using LLM
        
        Parameters:
        -----------
        input_columns : List[str]
            Column names from uploaded CSV
        target_schema : Dict[str, str]
            Target field names and descriptions
            
        Returns:
        --------
        Dictionary mapping input → target column names
        """
        print("="*80)
        print("LLM-POWERED SCHEMA MAPPING")
        print("="*80)
        
        # Prepare prompt
        schema_desc = "\n".join([f"  - {field}: {desc}" for field, desc in target_schema.items()])
        
        prompt = f"""You are a data mapping expert. Map the input column names to the standard CRM schema.

INPUT COLUMNS:
{', '.join(input_columns)}

TARGET SCHEMA:
{schema_desc}

INSTRUCTIONS:
1. Map each input column to the most appropriate target field
2. Consider semantic meaning, not just exact matches
3. If a column doesn't match any target field, map it to "skip"
4. Return ONLY valid JSON in this exact format:
{{
  "input_column_1": "target_field",
  "input_column_2": "target_field",
  ...
}}

Examples:
- "cust_name" → "name"
- "ph_no" → "phone"  
- "e-mail" → "email"
- "customer_name" → "name"
- "mobile_number" → "phone"
- "email_address" → "email"

Return the JSON mapping now:"""
        
        print(f"\n🤖 Consulting Gemini AI for schema mapping...")
        print(f"   Input columns: {len(input_columns)}")
        
        try:
            response = self.llm.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                mapping = json.loads(json_match.group())
                
                print(f"\n✓ LLM mapping successful!")
                print(f"\nProposed Mappings:")
                for input_col, target_col in mapping.items():
                    if target_col != "skip":
                        print(f"  {input_col:30} → {target_col}")
                    else:
                        print(f"  {input_col:30} → [SKIP]")
                
                return mapping
            else:
                print(f"\n⚠ Could not parse LLM response, using fallback mapping")
                return self.fallback_mapping(input_columns, target_schema)
                
        except Exception as e:
            print(f"\n⚠ LLM error: {e}, using fallback mapping")
            return self.fallback_mapping(input_columns, target_schema)
    
    def fallback_mapping(self, input_columns: List[str], target_schema: Dict[str, str]) -> Dict[str, str]:
        """Rule-based fallback mapping"""
        mapping = {}
        
        # Simple keyword matching
        name_keywords = ['name', 'fullname', 'full_name', 'customer', 'client']
        email_keywords = ['email', 'e-mail', 'mail', 'email_address']
        phone_keywords = ['phone', 'mobile', 'telephone', 'contact', 'ph_no', 'ph']
        company_keywords = ['company', 'organization', 'org', 'business']
        
        for col in input_columns:
            col_lower = col.lower()
            
            if any(kw in col_lower for kw in name_keywords):
                mapping[col] = 'name'
            elif any(kw in col_lower for kw in email_keywords):
                mapping[col] = 'email'
            elif any(kw in col_lower for kw in phone_keywords):
                mapping[col] = 'phone'
            elif any(kw in col_lower for kw in company_keywords):
                mapping[col] = 'company'
            else:
                mapping[col] = 'skip'
        
        return mapping


class DataCleaner:
    """Clean and validate data"""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with dataframe"""
        self.df = df.copy()
        self.issues = []
        self.stats = {}
        
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format"""
        if pd.isna(phone):
            return ""
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', str(phone))
        
        # Format based on length
        if len(digits) == 10:
            return f"+1{digits}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+{digits}"
        elif len(digits) >= 10:
            return f"+{digits}"
        else:
            return phone  # Invalid, return as-is
    
    def normalize_email(self, email: str) -> str:
        """Normalize email address"""
        if pd.isna(email):
            return ""
        
        email = str(email).lower().strip()
        
        # Remove spaces
        email = email.replace(' ', '')
        
        return email
    
    def normalize_name(self, name: str) -> str:
        """Normalize person name"""
        if pd.isna(name):
            return ""
        
        name = str(name).strip()
        
        # Title case
        name = ' '.join([word.capitalize() for word in name.split()])
        
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if pd.isna(email) or email == "":
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number"""
        if pd.isna(phone) or phone == "":
            return False
        
        # After normalization, should start with + and have 11+ digits
        return phone.startswith('+') and len(re.sub(r'\D', '', phone)) >= 10
    
    def _detect_fuzzy_duplicates(self, threshold=85) -> int:
        """
        Detect and remove fuzzy duplicates based on name, email, and phone similarity
        
        Parameters:
        -----------
        threshold : int
            Similarity score threshold (0-100). Higher = more strict matching
            
        Returns:
        --------
        Number of fuzzy duplicates removed
        """
        from fuzzywuzzy import fuzz
        
        initial_count = len(self.df)
        indices_to_remove = set()
        
        # Create comparison keys
        compare_fields = []
        if 'name' in self.df.columns:
            compare_fields.append('name')
        if 'email' in self.df.columns:
            compare_fields.append('email')
        if 'phone' in self.df.columns:
            compare_fields.append('phone')
        
        if not compare_fields:
            print("   No comparable fields found for fuzzy matching")
            return 0
        
        # Compare records
        for i in range(len(self.df)):
            if i in indices_to_remove:
                continue
            
            for j in range(i + 1, len(self.df)):
                if j in indices_to_remove:
                    continue
                
                is_duplicate = False
                
                # Strategy 1: Exact email/phone match
                if 'email' in compare_fields:
                    email1 = str(self.df.iloc[i]['email']).lower().strip()
                    email2 = str(self.df.iloc[j]['email']).lower().strip()
                    if email1 and email2 and email1 == email2:
                        is_duplicate = True
                
                if not is_duplicate and 'phone' in compare_fields:
                    phone1 = str(self.df.iloc[i]['phone'])
                    phone2 = str(self.df.iloc[j]['phone'])
                    if phone1 and phone2 and phone1 == phone2:
                        is_duplicate = True
                
                # Strategy 2: Fuzzy name match (with email/phone similarity boost)
                if not is_duplicate and 'name' in compare_fields:
                    name1 = str(self.df.iloc[i]['name'])
                    name2 = str(self.df.iloc[j]['name'])
                    
                    if name1 and name2:
                        # Calculate name similarity
                        name_similarity = fuzz.ratio(name1.lower(), name2.lower())
                        
                        # If names are very similar
                        if name_similarity >= threshold:
                            # Check if email/phone are also similar
                            boost_similarity = False
                            
                            if 'email' in compare_fields:
                                email1 = str(self.df.iloc[i].get('email', '')).lower()
                                email2 = str(self.df.iloc[j].get('email', '')).lower()
                                if email1 and email2:
                                    # Similar email domain or username
                                    if '@' in email1 and '@' in email2:
                                        domain1 = email1.split('@')[1]
                                        domain2 = email2.split('@')[1]
                                        if domain1 == domain2:
                                            boost_similarity = True
                            
                            if 'phone' in compare_fields:
                                phone1_digits = re.sub(r'\D', '', str(self.df.iloc[i].get('phone', '')))
                                phone2_digits = re.sub(r'\D', '', str(self.df.iloc[j].get('phone', '')))
                                if len(phone1_digits) >= 7 and len(phone2_digits) >= 7:
                                    # Last 7 digits match (local number)
                                    if phone1_digits[-7:] == phone2_digits[-7:]:
                                        boost_similarity = True
                            
                            # If high name similarity + supporting evidence, mark as duplicate
                            if boost_similarity or name_similarity >= 90:
                                is_duplicate = True
                
                if is_duplicate:
                    indices_to_remove.add(j)
                    if len(indices_to_remove) % 100 == 0:
                        print(f"   Found {len(indices_to_remove)} fuzzy duplicates so far...")
        
        # Remove duplicates
        if indices_to_remove:
            self.df = self.df.drop(self.df.index[list(indices_to_remove)])
            self.df = self.df.reset_index(drop=True)
        
        removed_count = initial_count - len(self.df)
        
        if removed_count > 0:
            print(f"   Examples of fuzzy duplicates detected:")
            print(f"   - Same email with different names")
            print(f"   - Same phone with different spellings")
            print(f"   - Similar names (e.g., 'John Smith' vs 'Jon Smith')")
        
        return removed_count
    
    def clean(self, fuzzy_threshold=85) -> pd.DataFrame:
        """Execute cleaning pipeline
        
        Parameters:
        -----------
        fuzzy_threshold : int
            Similarity threshold (0-100) for fuzzy duplicate detection
            Default 85 means 85% similar names are considered duplicates
        """
        print("\n" + "="*80)
        print("DATA CLEANING PIPELINE")
        print("="*80)
        
        initial_rows = len(self.df)
        
        # 1. Remove exact duplicates
        print("\n1. Removing exact duplicates...")
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)
        exact_removed = before - after
        print(f"   Removed {exact_removed} exact duplicates")
        
        # 2. Fuzzy duplicate detection
        print(f"\n2. Detecting fuzzy duplicates (threshold: {fuzzy_threshold}%)...")
        fuzzy_removed = self._detect_fuzzy_duplicates(threshold=fuzzy_threshold)
        print(f"   Removed {fuzzy_removed} fuzzy duplicates")
        
        # 3. Normalize formats
        print("\n3. Normalizing data formats...")
        
        if 'name' in self.df.columns:
            print("   - Normalizing names...")
            self.df['name'] = self.df['name'].apply(self.normalize_name)
        
        if 'email' in self.df.columns:
            print("   - Normalizing emails...")
            self.df['email'] = self.df['email'].apply(self.normalize_email)
        
        if 'phone' in self.df.columns:
            print("   - Normalizing phone numbers...")
            self.df['phone'] = self.df['phone'].apply(self.normalize_phone)
        
        # 4. Validate data
        print("\n4. Validating data...")
        
        self.df['validation_status'] = 'VALID'
        self.df['validation_issues'] = ''
        
        for idx, row in self.df.iterrows():
            issues = []
            
            # Check email
            if 'email' in self.df.columns:
                if not self.validate_email(row.get('email', '')):
                    issues.append('Invalid email')
            
            # Check phone
            if 'phone' in self.df.columns:
                if not self.validate_phone(row.get('phone', '')):
                    issues.append('Invalid phone')
            
            # Check required fields
            if 'name' in self.df.columns:
                if pd.isna(row.get('name', '')) or row.get('name', '') == '':
                    issues.append('Missing name')
            
            if issues:
                self.df.at[idx, 'validation_status'] = 'INVALID'
                self.df.at[idx, 'validation_issues'] = '; '.join(issues)
        
        # 5. Generate statistics
        valid_count = (self.df['validation_status'] == 'VALID').sum()
        invalid_count = (self.df['validation_status'] == 'INVALID').sum()
        
        print(f"\n   Valid records: {valid_count} ({valid_count/len(self.df)*100:.1f}%)")
        print(f"   Invalid records: {invalid_count} ({invalid_count/len(self.df)*100:.1f}%)")
        
        self.stats = {
            'initial_rows': initial_rows,
            'final_rows': len(self.df),
            'exact_duplicates_removed': exact_removed,
            'fuzzy_duplicates_removed': fuzzy_removed,
            'valid_records': valid_count,
            'invalid_records': invalid_count
        }
        
        return self.df
    
    def get_quality_report(self) -> str:
        """Generate data quality report"""
        report = "="*80 + "\n"
        report += "DATA QUALITY REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Total Records: {self.stats['final_rows']}\n"
        report += f"Valid Records: {self.stats['valid_records']} ({self.stats['valid_records']/self.stats['final_rows']*100:.1f}%)\n"
        report += f"Invalid Records: {self.stats['invalid_records']} ({self.stats['invalid_records']/self.stats['final_rows']*100:.1f}%)\n"
        report += f"Exact Duplicates Removed: {self.stats['exact_duplicates_removed']}\n"
        report += f"Fuzzy Duplicates Removed: {self.stats['fuzzy_duplicates_removed']}\n\n"
        
        # Field completeness
        report += "FIELD COMPLETENESS:\n"
        report += "-" * 80 + "\n"
        for col in self.df.columns:
            if col not in ['validation_status', 'validation_issues']:
                non_null = self.df[col].notna().sum()
                completeness = non_null / len(self.df) * 100
                report += f"  {col:20} {non_null:6} / {len(self.df):6} ({completeness:5.1f}%)\n"
        
        # Issue breakdown
        if self.stats['invalid_records'] > 0:
            report += "\nVALIDATION ISSUES:\n"
            report += "-" * 80 + "\n"
            
            all_issues = self.df[self.df['validation_status'] == 'INVALID']['validation_issues']
            issue_types = {}
            
            for issues_str in all_issues:
                for issue in issues_str.split('; '):
                    issue_types[issue] = issue_types.get(issue, 0) + 1
            
            for issue, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                report += f"  {issue:30} {count:6} ({count/len(self.df)*100:.1f}%)\n"
        
        return report


def process_file(input_path: str, output_path: str, api_key: str, schema_type='crm', custom_schema=None):
    """
    Main pipeline to process a CSV file
    
    Parameters:
    -----------
    input_path : str
        Path to input CSV file
    output_path : str
        Path to save cleaned output CSV
    api_key : str
        Gemini API key
    schema_type : str
        Schema type: 'crm', 'ecommerce', 'hr', or 'custom'
    custom_schema : Dict[str, str], optional
        Custom schema definition (required if schema_type='custom')
    """
    print("="*80)
    print("SMART DATA IMPORTER")
    print("="*80)
    
    # Load CSV
    print(f"\n📂 Loading: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # Get target schema
    if schema_type.lower() == 'custom':
        if custom_schema is None:
            raise ValueError("Custom schema required when schema_type='custom'")
        target_schema = get_custom_schema(custom_schema)
        print(f"\n📋 Using CUSTOM schema with {len(target_schema)} fields")
    else:
        target_schema = get_schema(schema_type)
        print(f"\n📋 Using {schema_type.upper()} schema with {len(target_schema)} fields")
    
    # Map schema using LLM
    mapper = SchemaMapper(api_key)
    mapping = mapper.map_columns(list(df.columns), target_schema)
    
    # Apply mapping
    print("\n" + "="*80)
    print("APPLYING SCHEMA MAPPING")
    print("="*80)
    
    df_mapped = pd.DataFrame()
    for input_col, target_col in mapping.items():
        if target_col != "skip":
            df_mapped[target_col] = df[input_col]
            print(f"  ✓ Mapped {input_col} → {target_col}")
    
    print(f"\n  Final schema: {', '.join(df_mapped.columns)}")
    
    # Clean data
    cleaner = DataCleaner(df_mapped)
    df_clean = cleaner.clean()
    
    # Save cleaned data
    print(f"\n💾 Saving cleaned data to: {output_path}")
    df_clean.to_csv(output_path, index=False)
    print(f"   ✓ Saved {len(df_clean)} rows")
    
    # Generate report
    report = cleaner.get_quality_report()
    print("\n" + report)
    
    # Save report
    report_path = output_path.replace('.csv', '_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"📊 Quality report saved to: {report_path}")
    
    print("\n" + "="*80)
    print("PROCESSING COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python data_cleaner.py <input.csv> <output.csv> <api_key> [schema_type]")
        print("\nSchema Types:")
        print("  crm        - Customer Relationship Management (default)")
        print("  ecommerce  - E-commerce orders and customers")
        print("  hr         - Human Resources employee data")
        print("  custom     - Custom schema (requires --custom-fields)")
        print("\nExamples:")
        print("  python data_cleaner.py input.csv output.csv API_KEY crm")
        print("  python data_cleaner.py input.csv output.csv API_KEY ecommerce")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    api_key = sys.argv[3]
    schema_type = sys.argv[4] if len(sys.argv) > 4 else 'crm'
    
    process_file(input_file, output_file, api_key, schema_type=schema_type)
