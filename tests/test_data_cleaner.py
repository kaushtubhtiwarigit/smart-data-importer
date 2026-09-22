"""
Tests for data cleaning functionality
"""

import unittest
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from data_cleaner import DataCleaner, SchemaMapper


class TestDataCleaner(unittest.TestCase):
    """Test data cleaning and normalization"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = pd.DataFrame({
            'name': ['john doe', 'JANE SMITH', '  bob  johnson  ', None, 'Alice'],
            'email': ['john@gmail.com', 'JANE@EXAMPLE.COM', 'bob @yahoo.com', 'invalid', 'alice@test.com'],
            'phone': ['5551234567', '(555) 987-6543', '555.123.4567', 'invalid', '+1-555-999-8888']
        })
        self.cleaner = DataCleaner(self.test_data)
    
    def test_normalize_name(self):
        """Test name normalization"""
        assert self.cleaner.normalize_name('john doe') == 'John Doe'
        assert self.cleaner.normalize_name('JANE SMITH') == 'Jane Smith'
        assert self.cleaner.normalize_name('  bob  johnson  ') == 'Bob Johnson'
        assert self.cleaner.normalize_name(None) == ''
    
    def test_normalize_email(self):
        """Test email normalization"""
        assert self.cleaner.normalize_email('JOHN@GMAIL.COM') == 'john@gmail.com'
        assert self.cleaner.normalize_email('bob @yahoo.com') == 'bob@yahoo.com'
        assert self.cleaner.normalize_email('  TEST@EXAMPLE.COM  ') == 'test@example.com'
        assert self.cleaner.normalize_email(None) == ''
    
    def test_normalize_phone(self):
        """Test phone normalization"""
        assert self.cleaner.normalize_phone('5551234567') == '+15551234567'
        assert self.cleaner.normalize_phone('(555) 987-6543') == '+15559876543'
        assert self.cleaner.normalize_phone('555.123.4567') == '+15551234567'
        assert self.cleaner.normalize_phone('+1-555-999-8888') == '+15559998888'
        assert self.cleaner.normalize_phone(None) == ''
    
    def test_validate_email(self):
        """Test email validation"""
        assert self.cleaner.validate_email('john@gmail.com') == True
        assert self.cleaner.validate_email('test@example.co.uk') == True
        assert self.cleaner.validate_email('invalid') == False
        assert self.cleaner.validate_email('test@') == False
        assert self.cleaner.validate_email('@example.com') == False
        assert self.cleaner.validate_email('') == False
        assert self.cleaner.validate_email(None) == False
    
    def test_validate_phone(self):
        """Test phone validation"""
        assert self.cleaner.validate_phone('+15551234567') == True
        assert self.cleaner.validate_phone('+15559876543') == True
        assert self.cleaner.validate_phone('invalid') == False
        assert self.cleaner.validate_phone('123') == False
        assert self.cleaner.validate_phone('') == False
        assert self.cleaner.validate_phone(None) == False
    
    def test_clean_pipeline(self):
        """Test full cleaning pipeline"""
        result = self.cleaner.clean()
        
        # Should have added validation columns
        assert 'validation_status' in result.columns
        assert 'validation_issues' in result.columns
        
        # Check statistics were generated
        assert hasattr(self.cleaner, 'stats')
        assert 'initial_rows' in self.cleaner.stats
        assert 'valid_records' in self.cleaner.stats
        assert 'invalid_records' in self.cleaner.stats
    
    def test_duplicate_removal(self):
        """Test duplicate detection"""
        data_with_dups = pd.DataFrame({
            'name': ['John Doe', 'John Doe', 'Jane Smith'],
            'email': ['john@test.com', 'john@test.com', 'jane@test.com'],
            'phone': ['+15551234567', '+15551234567', '+15559876543']
        })
        
        cleaner = DataCleaner(data_with_dups)
        result = cleaner.clean()
        
        # Should have removed 1 duplicate
        assert cleaner.stats['duplicates_removed'] == 1
        assert len(result) == 2
    
    def test_quality_report(self):
        """Test quality report generation"""
        self.cleaner.clean()
        report = self.cleaner.get_quality_report()
        
        assert 'DATA QUALITY REPORT' in report
        assert 'Total Records' in report
        assert 'Valid Records' in report
        assert 'FIELD COMPLETENESS' in report


class TestSchemaMapper(unittest.TestCase):
    """Test schema mapping functionality"""
    
    def test_fallback_mapping(self):
        """Test rule-based fallback mapping"""
        # Skip LLM, test fallback directly
        mapper = SchemaMapper('dummy_key')
        
        input_cols = ['customer_name', 'ph_no', 'e-mail', 'company_name', 'random_field']
        target_schema = {
            'name': 'Full name',
            'email': 'Email address',
            'phone': 'Phone number',
            'company': 'Company name'
        }
        
        mapping = mapper.fallback_mapping(input_cols, target_schema)
        
        assert mapping['customer_name'] == 'name'
        assert mapping['ph_no'] == 'phone'
        assert mapping['e-mail'] == 'email'
        assert mapping['company_name'] == 'company'
        assert mapping['random_field'] == 'skip'


if __name__ == '__main__':
    unittest.main()
