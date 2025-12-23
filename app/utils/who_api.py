"""
WHO API Integration Module
Provides functions to fetch health indicator data from the World Health Organization API
"""

import requests
from typing import Optional, Dict, Any


def get_who_indicator_data(indicator_code: str, filters: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch WHO health indicator data for a specific indicator code.
    
    Args:
        indicator_code (str): The WHO indicator code (e.g., 'NCD_BMI_30', 'MORT_DIAB')
        filters (str, optional): OData filter string (e.g., "$filter=Dim1 eq 'FMLE'")
    
    Returns:
        Dict[str, Any]: Processed WHO data or error message
    """
    base_url = "https://ghoapi.azureedge.net/api"
    
    try:
        # Construct the API URL
        url = f"{base_url}/{indicator_code}"
        if filters:
            url = f"{url}?{filters}"
        
        # Make the API request
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Process and return relevant data
        if 'value' in data and len(data['value']) > 0:
            # Extract key information from the first few records
            records = data['value'][:5]  # Limit to first 5 records
            
            processed_data = {
                "indicator": indicator_code,
                "records_found": len(data['value']),
                "sample_data": []
            }
            
            for record in records:
                processed_record = {
                    "country": record.get('SpatialDim', 'N/A'),
                    "year": record.get('TimeDim', 'N/A'),
                    "value": record.get('NumericValue', 'N/A'),
                    "gender": record.get('Dim1', 'N/A')
                }
                processed_data["sample_data"].append(processed_record)
            
            return processed_data
        else:
            return {
                "indicator": indicator_code,
                "message": "No data available for this indicator",
                "records_found": 0
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "indicator": indicator_code,
            "error": f"API request failed: {str(e)}",
            "records_found": 0
        }
    except Exception as e:
        return {
            "indicator": indicator_code,
            "error": f"Unexpected error: {str(e)}",
            "records_found": 0
        }


def get_country_health_data(country_code: str, indicator_code: str) -> Dict[str, Any]:
    """
    Fetch WHO health data for a specific country and indicator.
    
    Args:
        country_code (str): ISO3 country code (e.g., 'USA', 'GBR')
        indicator_code (str): The WHO indicator code
    
    Returns:
        Dict[str, Any]: Country-specific health data
    """
    filters = f"$filter=SpatialDim eq '{country_code}'"
    return get_who_indicator_data(indicator_code, filters)
