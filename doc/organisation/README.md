# Update Organisation Information. 

This API can be used to update organisation information in LedgerGW.

```
from ledger_api_client import

utils.update_organisation_obj(
    {
        'organisation_id': 2, 
        'organisation_name': "testing 8200", 
        "organisation_abn": "1212112344", 
        "organisation_email": "test@test.com", 
        "organisation_trading_name": "Test PTY LTD", 
        "postal_address": 
            {
                "postal_line1": "4 12 street", 
                "postal_locality": "perth", 
                "postal_state": "WA", 
                "postal_postcode":"6000", 
                "postal_country": "AU" 
            }, 
        "billing_address": 
            {
                "billing_line1": "70 street", 
                "billing_locality": "perth", 
                "billing_state": "WA", 
                "billing_postcode":"6001", 
                "billing_country": "AU" 
            }
    }
)
```
