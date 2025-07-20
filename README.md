

## Prerequisites

### 1. Meta Developer Account Setup

#### Step 1: Confirm Your Identity and Location
1. Go to [facebook.com/ID](https://www.facebook.com/ID)
2. Follow the confirmation process required to run ads about social issues, elections, or politics
3. ⚠️ **Important**: This process can take a few days to complete

#### Step 2: Create a Meta for Developers Account
1. Visit [Meta for Developers](https://developers.facebook.com/)
2. Click **"Get Started"**
3. Log in with your Facebook account
4. Agree to the Platform Policy during account creation

#### Step 3: Create an App and Get API Access
1. Once logged in, go to [Meta Ad Library API](https://www.facebook.com/ads/library/api/)
2. Click **"Access the API"**
3. Create a new app by selecting **"My Apps > Create App"**
4. Choose **"Business"** as the app type
5. Fill in your app details:
   - **App Name**: Choose a descriptive name
   - **Contact Email**: Your email address
   - **Business Account**: Select or create one

#### Step 4: Get Your Access Token
1. In your app dashboard, go to **"Tools > Graph API Explorer"**
2. Select your app from the dropdown
3. Click **"Generate Access Token"**
4. Copy the access token - you'll need this for the script

### 2. R Environment Setup

Install required R packages:

```r
install.packages(c("httr", "jsonlite", "dplyr", "readr", "purrr"))
```

## Configuration

### Update Access Token

Edit the `ACCESS_TOKEN` variable in `ad_api.R`:

```r
ACCESS_TOKEN <- "YOUR_ACCESS_TOKEN_HERE"
```

Replace `"YOUR_ACCESS_TOKEN_HERE"` with the token you obtained from Meta.

## Usage

### Run the Script

```bash
Rscript ad_api.R
```

Or in R console:

```r
source("ad_api.R")
```

### Output Files

The script generates two CSV files:

- `analyst_ads_[timestamp].csv` - Global results (US, GB, CA)
- `analyst_ads_india_[timestamp].csv` - India-specific results

## Customization

### Modifying Search Configurations

In `ad_api.R`, find the search configuration sections:

#### Global Searches
```r
search_configurations <- list(
  list(terms = "analyst", countries = "US", limit = 1000, ad_type = "ALL"),
  list(terms = "analyst", countries = "GB", limit = 1000, ad_type = "ALL"),
  list(terms = "analyst", countries = "US", limit = 1000, ad_type = "POLITICAL_AND_ISSUE_ADS"),
  list(terms = "analyst", countries = "CA", limit = 500, ad_type = "ALL")
)
```

#### India Searches
```r
india_search_configurations <- list(
  list(terms = "analyst", countries = "IN", limit = 1000, ad_type = "ALL"),
  list(terms = "analyst", countries = "IN", limit = 1000, ad_type = "POLITICAL_AND_ISSUE_ADS")
)
```

### Customization Options

**Search Terms:**
```r
# Change search terms
terms = "data scientist"  # Single term
terms = "business analyst"  # Different role
```

**Countries:**
```r
# Country codes (ISO 3166-1 alpha-2)
countries = "US"     # United States
countries = "CA"     # Canada  
countries = "GB"     # United Kingdom
countries = "DE"     # Germany
countries = "AU"     # Australia
countries = "FR"     # France
countries = "IN"     # India
```

**Search Limits:**
```r
limit = 1000  # Maximum ads per search (up to 1000)
```

**Ad Types:**
```r
ad_type = "ALL"                        # All ad types
ad_type = "POLITICAL_AND_ISSUE_ADS"    # Political/issue ads only (has gender data)
```

## Gender Demographics Data

The script attempts to collect gender-related targeting information:

### Available Fields
- `demographic_distribution` - Available for **political/issue ads only**
- `target_gender` - Available for **UK/EU ads** and **political/issue ads in Brazil**
- `target_ages` - Age targeting ranges
- `age_country_gender_reach_breakdown` - Detailed demographic breakdown

### Data Limitations
⚠️ **Important**: Due to Meta's privacy policies:
- Gender metrics are **limited** to specific ad types and regions
- Most commercial ads will **not** have gender data
- Political/issue ads have the most comprehensive demographic data

## API Rate Limits & Best Practices

- The Meta Ad Library API has rate limits
- The script includes error handling for failed requests
- Large searches may take several minutes to complete
- Consider running searches during off-peak hours

## Data Privacy & Usage

- All data is public information from Meta's Ad Library
- Comply with Meta's Terms of Service when using this data
- Data should be used for research and analysis purposes
- Do not attempt to identify individual users

## Troubleshooting

### Common Issues

1. **"Request failed" errors**:
   - Check your internet connection
   - Verify your access token is valid
   - Ensure you've completed identity verification

2. **"Error: HTTP 400"**:
   - Invalid parameters (check country codes, ad types)
   - Access token may be expired

3. **"Error: HTTP 403"**:
   - Access token lacks required permissions
   - Identity verification may not be complete

4. **No results found**:
   - Try broader search terms
   - Check if ads exist for your target country
   - Political ads may be limited by date ranges

### Getting Help

- [Meta Ad Library API Documentation](https://developers.facebook.com/docs/ad-library-api/)
- [Meta for Developers Community](https://developers.facebook.com/community/)
- [Ad Library API Script Repository](https://github.com/facebookresearch/Ad-Library-API-Script-Repository)

## Notes

- Meta's Ad Library API shows **ranges** instead of exact spending and impression numbers for privacy protection
- The script automatically removes duplicate ads across different searches
- Results are sorted by availability of metrics (ads with spend/impression data first)