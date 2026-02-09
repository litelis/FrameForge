"""
JSON Schema Validation Utilities

Ensures all outputs conform to strict Pydantic schemas
"""

from typing import Type, Dict, Any, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def validate_json_schema(data: Dict[str, Any], schema_class: Type[T]) -> Dict[str, Any]:
    """
    Validate dictionary against Pydantic schema
    
    Args:
        data: Dictionary to validate
        schema_class: Pydantic model class to validate against
        
    Returns:
        Validated dictionary
        
    Raises:
        ValueError: If validation fails with details
    """
    try:
        # Validate and parse
        validated = schema_class(**data)
        
        # Return as dict
        return validated.dict()
        
    except ValidationError as e:
        # Log detailed error
        logger.error(f"Schema validation failed for {schema_class.__name__}")
        
        # Build detailed error message
        errors = []
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            msg = error['msg']
            errors.append(f"{field}: {msg}")
        
        error_msg = f"Validation failed for {schema_class.__name__}: " + "; ".join(errors)
        logger.error(error_msg)
        
        raise ValueError(error_msg)
    
    except Exception as e:
        logger.error(f"Unexpected validation error: {str(e)}")
        raise ValueError(f"Validation error: {str(e)}")


def validate_partial(data: Dict[str, Any], schema_class: Type[T]) -> Dict[str, Any]:
    """
    Validate partial data (for updates where not all fields required)
    
    Args:
        data: Dictionary to validate
        schema_class: Pydantic model class
        
    Returns:
        Validated dictionary with only provided fields
    """
    try:
        # Use model_validate for partial validation (Pydantic v2)
        # or construct for Pydantic v1
        try:
            # Pydantic v2 style
            validated = schema_class.model_validate(data, partial=True)
        except AttributeError:
            # Pydantic v1 fallback - construct without validation
            validated = schema_class.construct(**data)
        
        return validated.dict(exclude_unset=True)
        
    except Exception as e:
        logger.error(f"Partial validation error: {str(e)}")
        raise ValueError(f"Partial validation failed: {str(e)}")


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize object for JSON serialization
    
    Handles:
    - datetime objects -> ISO strings
    - bytes -> base64 strings
    - sets -> lists
    - non-serializable -> str()
    """
    import datetime
    import base64
    
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    
    elif isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]
    
    elif isinstance(obj, tuple):
        return [sanitize_for_json(item) for item in obj]
    
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    
    elif isinstance(obj, float):
        # Handle NaN, Inf
        if obj != obj:  # NaN check
            return None
        if obj == float('inf') or obj == float('-inf'):
            return None
        return obj
    
    elif isinstance(obj, BaseModel):
        return sanitize_for_json(obj.dict())
    
    else:
        # Try to return as-is, fallback to str
        try:
            # Test JSON serialization
            import json
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)


def clean_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove empty values from dictionary recursively
    
    Removes:
    - None values
    - Empty strings
    - Empty lists
    - Empty dicts
    """
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for key, value in data.items():
        if value is None:
            continue
        elif isinstance(value, str) and not value.strip():
            continue
        elif isinstance(value, list) and len(value) == 0:
            continue
        elif isinstance(value, dict):
            cleaned_value = clean_empty_values(value)
            if cleaned_value:  # Only add if not empty
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value
    
    return cleaned


def merge_schemas(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two schema dictionaries
    
    Override values take precedence, but nested dicts are merged
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_schemas(result[key], value)
        else:
            result[key] = value
    
    return result


# Example usage
if __name__ == "__main__":
    from models.schemas import PromptRefinementOutput
    
    # Test validation
    test_data = {
        "original_prompt": "Make a nice video",
        "improved_prompt": "Goal: Make a nice video\n- Technical: [Format: 16:9/9:16/1:1]",
        "issues_detected": ["Vague language"],
        "improvements_made": ["Added structure"],
        "user_action_required": "accept"
    }
    
    try:
        validated = validate_json_schema(test_data, PromptRefinementOutput)
        print("Validation successful!")
        print(validated)
    except ValueError as e:
        print(f"Validation failed: {e}")
    
    # Test invalid data
    invalid_data = {
        "original_prompt": "Test",
        "improved_prompt": "",  # Empty - should fail
        "issues_detected": [],
        "improvements_made": [],
        "user_action_required": "invalid"  # Invalid enum
    }
    
    try:
        validate_json_schema(invalid_data, PromptRefinementOutput)
    except ValueError as e:
        print(f"\nExpected validation error: {e}")
