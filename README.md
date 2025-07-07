### Install Dependencies

install the required Python packages:

```bash
pip install requests
```

### Run the Script

```bash
python ad_api.py
```

## 🔍 Customizing Search Queries

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

# Skills-based
'terms': ['python analyst', 'sql developer', 'tableau specialist']

# Industry-specific
'terms': ['finance analyst', 'marketing analyst', 'healthcare data']

# Experience levels
'terms': ['entry level analyst', 'senior data scientist', 'principal analyst']
```

**Countries:**
```python
# Major markets
'countries': ['US', 'CA', 'GB', 'AU', 'DE', 'FR']

# Specific regions
'countries': ['US']  # US only
'countries': ['CA', 'GB']  # Canada and UK
```

**Search Limits:**
```python
'limit': 50  # Maximum ads per search term per country
```

### Advanced Search Strategies

**For Remote Jobs:**
```python
'terms': ['remote data analyst', 'work from home analyst', 'distributed team data']
```

**For Specific Companies:**
```python
'terms': ['google data analyst', 'meta data scientist', 'amazon analyst']
```

**For Salary-Focused Searches:**
```python
'terms': ['high salary analyst', '$100k data scientist', 'competitive pay data']
```

## 🔒 Meta's Privacy System: Upper & Lower Bounds

### Why Meta Uses Ranges Instead of Exact Numbers

Meta's Ad Library API protects advertiser privacy by showing **ranges** instead of exact spending and impression numbers.

### Understanding the Data Format

Instead of exact numbers, you'll see:
```json
{
  "impressions": {
    "lower_bound": "7000",
    "upper_bound": "7999"
  },
  "spend": {
    "lower_bound": "0", 
    "upper_bound": "99"
  }
}
```

### What This Means:

**Impressions Range:**
- `7000-7999`: The ad was shown between 7,000 and 7,999 times
- `0-999`: Low impression volume (new or limited ad)
- `10000-49999`: Medium impression volume
- `50000+`: High impression volume

**Spending Range:**
- `$0-$99`: Low budget campaign (testing or small target)
- `$100-$999`: Medium budget campaign
- `$1000-$4999`: High budget campaign
- `$5000+`: Major recruitment campaign

### Privacy Protection Benefits:

1. **Competitor Protection**: Prevents exact spending reverse-engineering
2. **Advertiser Confidentiality**: Protects sensitive business data
3. **Regulatory Compliance**: Meets transparency requirements safely
4. **Data Aggregation**: Allows market analysis without exposing details

### How Our Script Handles This:

```python
# We calculate averages from ranges
lower = int(impressions.get('lower_bound', 0))
upper = int(impressions.get('upper_bound', lower))
avg_impressions = (lower + upper) / 2
```

**Example:**
- Range: `7000-7999`
- Our calculation: `(7000 + 7999) / 2 = 7,499.5`
- Analysis: "~7,500 impressions"

## 🎯 Data Quality & Filtering

### Why Some Ads Show N/A

The script now filters for ads with **actual metrics** only, but you should understand why some ads lack data:

1. **Privacy Thresholds**: Only ads reaching minimum engagement show metrics
2. **New Campaigns**: Recently launched ads may not have data yet
3. **Paused Campaigns**: Stopped ads often show N/A
4. **Advertiser Settings**: Some companies opt out of showing metrics

### Our Content Filter

```python
# Include ads with job-related keywords OR from major companies
if (has_job_keywords or is_major_company):
```

This ensures we capture relevant job ads and major company recruiters, regardless of whether they have metrics data.

## 📊 Sample Output Interpretation

### Console Output Example:
```
🔥 JOB AD #1 🔥 ⭐
Company: Google
💰 Spend: $1000-$4999
👀 Impressions: 25000-49999
🎯 Audience Size: 100001-500000
```

**Translation:**
- 🔥 = Has actual metrics data
- ⭐ = Major company
- Google spent $1,000-$4,999 on this ad
- Reached 25,000-49,999 people
- Targeted audience of 100,001-500,000 people

### Market Insights:
- **High spend + High impressions** = Active, urgent hiring
- **Low spend + High impressions** = Efficient targeting
- **High spend + Low impressions** = Premium/niche targeting
- **Consistent spending** = Ongoing recruitment needs

## 🛠️ Troubleshooting

### Common Issues:

**"No ads found":**
- Check your access token is valid
- Try broader search terms
- Verify countries are correct (use 2-letter codes)

**"Request failed":**
- Token might be expired
- Check internet connection
- Verify API access permissions

**"Low quality results":**
- Increase search limits
- Add more search terms
- Try different countries

### Access Token Problems:

1. **Generate new token** at [Meta for Developers](https://developers.facebook.com/)
2. **Check permissions**: Ensure `ads_read` is included
3. **Token expiry**: Tokens expire, generate fresh ones regularly

## 🔮 Advanced Use Cases

### Market Research:
- Compare spending across companies
- Identify hiring trends by industry
- Track seasonal recruitment patterns

### Job Seeking:
- Find actively hiring companies (high spend = urgent need)
- Identify salary ranges from ad content
- Discover in-demand skills from job descriptions

### Competitive Analysis:
- Monitor competitor hiring strategies
- Track industry recruitment budgets
- Analyze targeting strategies

## 📝 Output Files

### CSV File (`data_analyst_jobs_[timestamp].csv`)
Contains raw data ready for Excel/spreadsheet analysis:
- Complete ad details with separate columns for upper/lower bounds
- Metrics data (spend_lower, spend_upper, impressions_lower, impressions_upper)
- Company information, job titles, and ad content
- Platform distribution and targeting data
- Quality indicators (has_metrics, is_major_company)

### Summary Report (`market_summary_[timestamp].txt`)
Human-readable insights:
- Total market spending
- Top hiring companies
- Platform distribution
- Key trends

## 🤝 Contributing

Feel free to modify the script for your needs:
- Add new search terms
- Include additional countries
- Modify filtering criteria
- Enhance analysis functions

## ⚖️ Legal & Ethical Use

- This tool uses Meta's **public** Ad Library API
- All data is publicly available for transparency
- Use responsibly and respect privacy
- Follow Meta's terms of service
- Consider rate limiting for large searches

## 📞 Support

For issues or questions:
1. Check your access token and permissions
2. Verify search parameters are correct
3. Ensure all dependencies are installed
4. Try with simpler search terms first

---

**Happy job market hunting! 🎯📊** 