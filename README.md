### Install Dependencies

install the required Python packages:

```bash
pip install requests
```

### Run the Script

```bash
python ad_api.py
```

### Modifying Search Terms

In `ad_api.py`, find the `search_configurations` section:

```python
search_configurations = [
    {
        'terms': ['data analyst', 'data scientist', 'business analyst', 'data engineer'],
        'countries': ['US'],
        'limit': 50
    },
    {
        'terms': ['remote data analyst', 'hiring data scientist', 'data jobs'],
        'countries': ['US', 'CA', 'GB'],
        'limit': 40
    }
]
```

### Customization Options:

**Search Terms:**
```python
# Job titles
'terms': ['data analyst', 'data scientist', 'business analyst']
```

**Countries:**
```python
# Country examples
'countries': ['US', 'CA', 'GB', 'AU', 'DE', 'FR']

# Specific regions
'countries': ['US']  # US only
'countries': ['CA', 'GB']  # Canada and UK
```

**Search Limits:**
```python
'limit': 50  # Maximum ads per search term per country
```

Meta's Ad Library API protects advertiser privacy by showing **ranges** instead of exact spending and impression numbers.