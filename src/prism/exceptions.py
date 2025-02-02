class PrismNotFoundError(Exception):
    """Raised when a prism root is not found"""
    pass

class PageError(Exception):
    """Raised when an error occurs during page processing"""
    pass

class PrismError(Exception):
    """Base class for Prism-related errors"""
    pass