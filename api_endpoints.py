# Base URL for MIS Data APIs
BASE_MIS_DATA_API_URL = "http://127.0.0.1:8000/api/loan"

# Customer-related MIS Data API Endpoints
CUSTOMER_GET_ALL_URL = f"{BASE_MIS_DATA_API_URL}/customers/get-all/"
CUSTOMER_COUNT_URL = f"{BASE_MIS_DATA_API_URL}/customers/count/"
CUSTOMER_SEARCH_URL = f"{BASE_MIS_DATA_API_URL}/customers/search/"
CUSTOMER_GET_BY_ACCOUNT_URL = f"{BASE_MIS_DATA_API_URL}/customers/getBy-account-number/"
CUSTOMER_SEARCH_BY_ADDRESS_URL = f"{BASE_MIS_DATA_API_URL}/customers/search-by-address/"

# Location-related API Endpoints
EXTERNAL_LOCATION_API_BASE_URL = "https://countriesnow.space/api/v0.1"
