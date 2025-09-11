# Utility functions
from typing import Optional


def get_pagination_params(skip: int = 0, limit: int = 10) -> dict:
    """
    Get pagination parameters.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
    Returns:
        Dictionary with skip and limit values
    """
    return {"skip": skip, "limit": limit}


def get_filter_params(
    search: Optional[str] = None, sort_by: Optional[str] = None
) -> dict:
    """
    Get filtering parameters.

    Args:
        search: Search term for filtering
        sort_by: Field to sort the results by
    Returns:
        Dictionary with search and sort_by values
    """
    return {"search": search, "sort_by": sort_by}
