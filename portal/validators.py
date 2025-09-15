# Add this to your validators.py or at the top of views.py
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class FlexibleIntegerValidator(BaseValidator):
    """Validator that handles both string and integer comparisons"""
    
    def __init__(self, limit_value, message=None):
        super().__init__(limit_value, message)
    
    def compare(self, a, b):
        # Convert both values to integers for comparison
        try:
            a_int = int(a)
            b_int = int(b)
            return a_int < b_int
        except (ValueError, TypeError):
            # If conversion fails, let the field validation handle it
            return False
    
    def clean(self, x):
        try:
            return int(x)
        except (ValueError, TypeError):
            return x