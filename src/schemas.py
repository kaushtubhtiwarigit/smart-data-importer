"""
Schema Definitions for Smart Data Importer

Supports multiple target schemas: CRM, E-commerce, HR, and Custom
"""

from typing import Dict

# Available schemas
SCHEMAS = {
    'crm': {
        'name': 'Full name of the person',
        'email': 'Email address',
        'phone': 'Phone number',
        'company': 'Company name',
        'address': 'Full address',
        'job_title': 'Job title or position',
        'industry': 'Company industry'
    },
    
    'ecommerce': {
        'customer_name': 'Customer full name',
        'email': 'Customer email address',
        'phone': 'Customer phone number',
        'shipping_address': 'Shipping address',
        'billing_address': 'Billing address',
        'customer_id': 'Unique customer identifier',
        'order_id': 'Order number',
        'product_name': 'Product name',
        'product_sku': 'Product SKU code',
        'quantity': 'Quantity ordered',
        'price': 'Product price',
        'order_date': 'Date of order',
        'payment_method': 'Payment method used',
        'order_status': 'Order status (pending/shipped/delivered)'
    },
    
    'hr': {
        'employee_name': 'Employee full name',
        'email': 'Work email address',
        'phone': 'Contact phone number',
        'employee_id': 'Unique employee ID',
        'department': 'Department name',
        'position': 'Job position or title',
        'hire_date': 'Date of hire',
        'salary': 'Annual salary',
        'manager': 'Manager name',
        'employment_type': 'Full-time/Part-time/Contract',
        'location': 'Office location',
        'date_of_birth': 'Date of birth',
        'emergency_contact': 'Emergency contact information'
    }
}


def get_schema(schema_type: str) -> Dict[str, str]:
    """
    Get predefined schema by type
    
    Parameters:
    -----------
    schema_type : str
        Schema type: 'crm', 'ecommerce', 'hr'
        
    Returns:
    --------
    Dictionary with field names and descriptions
    """
    schema_type = schema_type.lower()
    
    if schema_type not in SCHEMAS:
        raise ValueError(f"Unknown schema type: {schema_type}. Available: {list(SCHEMAS.keys())}")
    
    return SCHEMAS[schema_type]


def get_custom_schema(fields: Dict[str, str]) -> Dict[str, str]:
    """
    Create custom schema from field definitions
    
    Parameters:
    -----------
    fields : Dict[str, str]
        Dictionary of {field_name: description}
        
    Returns:
    --------
    Validated custom schema
    
    Example:
    --------
    >>> custom_schema = get_custom_schema({
    ...     'student_name': 'Full name of student',
    ...     'student_id': 'Unique student identifier',
    ...     'gpa': 'Grade point average'
    ... })
    """
    if not isinstance(fields, dict):
        raise ValueError("Custom schema must be a dictionary")
    
    if not fields:
        raise ValueError("Custom schema cannot be empty")
    
    # Validate field names (no special chars except underscore)
    import re
    for field_name in fields.keys():
        if not re.match(r'^[a-z][a-z0-9_]*$', field_name):
            raise ValueError(
                f"Invalid field name: '{field_name}'. "
                "Field names must start with lowercase letter and contain only lowercase letters, numbers, and underscores."
            )
    
    return fields


def list_schemas() -> Dict[str, Dict[str, str]]:
    """
    List all available predefined schemas
    
    Returns:
    --------
    Dictionary of all schemas with their fields
    """
    return SCHEMAS.copy()


def get_schema_info(schema_type: str) -> Dict:
    """
    Get detailed information about a schema
    
    Parameters:
    -----------
    schema_type : str
        Schema type: 'crm', 'ecommerce', 'hr'
        
    Returns:
    --------
    Dictionary with schema metadata
    """
    schema = get_schema(schema_type)
    
    info = {
        'name': schema_type.upper(),
        'field_count': len(schema),
        'fields': schema,
        'description': _get_schema_description(schema_type)
    }
    
    return info


def _get_schema_description(schema_type: str) -> str:
    """Get human-readable description of schema"""
    descriptions = {
        'crm': 'Customer Relationship Management schema for contact data',
        'ecommerce': 'E-commerce schema for customer orders and product data',
        'hr': 'Human Resources schema for employee information'
    }
    return descriptions.get(schema_type.lower(), 'Custom schema')


# Schema validation helpers

def validate_mapped_data(df, schema_type: str) -> Dict:
    """
    Validate that dataframe has expected fields from schema
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Mapped dataframe
    schema_type : str
        Schema type used for mapping
        
    Returns:
    --------
    Dictionary with validation results
    """
    schema = get_schema(schema_type)
    
    present_fields = [f for f in schema.keys() if f in df.columns]
    missing_fields = [f for f in schema.keys() if f not in df.columns]
    extra_fields = [f for f in df.columns if f not in schema.keys() and f not in ['validation_status', 'validation_issues']]
    
    coverage = len(present_fields) / len(schema) * 100 if schema else 0
    
    result = {
        'is_valid': len(missing_fields) == 0,
        'coverage_pct': coverage,
        'present_fields': present_fields,
        'missing_fields': missing_fields,
        'extra_fields': extra_fields,
        'total_expected': len(schema),
        'total_mapped': len(present_fields)
    }
    
    return result


if __name__ == "__main__":
    # Demo usage
    print("="*80)
    print("AVAILABLE SCHEMAS")
    print("="*80)
    
    for schema_name in SCHEMAS.keys():
        info = get_schema_info(schema_name)
        print(f"\n{info['name']}")
        print(f"Description: {info['description']}")
        print(f"Fields: {info['field_count']}")
        print("Fields:")
        for field, desc in info['fields'].items():
            print(f"  - {field:25} {desc}")
