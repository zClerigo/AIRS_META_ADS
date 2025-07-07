import requests
import json
import csv
from datetime import datetime

ACCESS_TOKEN = "EAAKFAZBK4LOQBPFW4L04ohmLrhNlcUiy1H038o5HWYWmqYF19Ihq3Ws2mUWpybZA7ca4QOzmUiiSLOXfxiKLyHjgZA1AggptgorHHuyOQLl28gA3bTv9uumKodO9XzZBIvSnmhEan8u0GT4DOO4ZBGAvgYttOpGgFnN6LOFOPfWTFvdAarEcJ42y634IzZApfmYNmMfQQy1YJW"

ADS_LIBRARY_BASE = "https://graph.facebook.com/v18.0/ads_archive"

def make_request(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def extract_job_ads():
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
        },
        {
            'terms': ['analyst position', 'data team', 'analytics role'],
            'countries': ['US'],
            'limit': 30
        },
        {
            'terms': ['data analyst jobs', 'analyst hiring', 'data science position'],
            'countries': ['US', 'CA'],
            'limit': 30
        }
    ]
    
    all_job_ads = []
    
    for config in search_configurations:
        for search_term in config['terms']:
            for country in config['countries']:
                print(f"🔍 Searching for: '{search_term}' in {country}")
                
                params = {
                    'access_token': ACCESS_TOKEN,
                    'ad_type': 'ALL',
                    'ad_reached_countries': country,
                    'search_terms': search_term,
                    'limit': config['limit'],
                    'fields': 'id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,page_name,ad_creative_link_titles,ad_creative_link_descriptions,ad_creative_link_captions,spend,impressions,publisher_platforms,estimated_audience_size,languages,ad_snapshot_url,ad_creative_bodies'
                }
        
                result = make_request(ADS_LIBRARY_BASE, params)
                
                if result and 'data' in result:
                    ads = result['data']
                    print(f"Found {len(ads)} ads for '{search_term}' in {country}")
                    
                    job_keywords = ['job', 'career', 'position', 'hire', 'hiring', 'apply', 'work', 'employment', 'opportunity', 'team', 'role', 'analyst', 'engineer', 'scientist']
                    
                    for ad in ads:
                        page_name = ad.get('page_name', '').lower()
                        link_titles = ad.get('ad_creative_link_titles', [])
                        link_descriptions = ad.get('ad_creative_link_descriptions', [])
                        ad_bodies = ad.get('ad_creative_bodies', [])
                        
                        all_text = f"{page_name} {' '.join(link_titles)} {' '.join(link_descriptions)} {' '.join(ad_bodies)}".lower()
                        
                        has_job_keywords = any(keyword in all_text for keyword in job_keywords)
                        
                        impressions = ad.get('impressions')
                        spend = ad.get('spend')
                        
                        has_impressions = (impressions and impressions != 'N/A' and 
                                         (isinstance(impressions, dict) or 
                                          (isinstance(impressions, str) and impressions.strip() != '')))
                        has_spend = (spend and spend != 'N/A' and 
                                   (isinstance(spend, dict) or 
                                    (isinstance(spend, str) and spend.strip() != '')))
                        
                        has_metrics = has_impressions or has_spend
                        
                        if has_job_keywords:
                            job_ad = {
                                'search_term': search_term,
                                'country': country,
                                'id': ad.get('id'),
                                'company': ad.get('page_name'),
                                'creation_date': ad.get('ad_creation_time'),
                                'delivery_start': ad.get('ad_delivery_start_time'),
                                'delivery_stop': ad.get('ad_delivery_stop_time'),
                                'job_titles': ad.get('ad_creative_link_titles', []),
                                'descriptions': ad.get('ad_creative_link_descriptions', []),
                                'captions': ad.get('ad_creative_link_captions', []),
                                'ad_creative_bodies': ad.get('ad_creative_bodies', []),
                                'spend': ad.get('spend', 'N/A'),
                                'impressions': ad.get('impressions', 'N/A'),
                                'publisher_platforms': ad.get('publisher_platforms', []),
                                'estimated_audience_size': ad.get('estimated_audience_size', 'N/A'),
                                'languages': ad.get('languages', []),
                                'ad_snapshot_url': ad.get('ad_snapshot_url', ''),
                                'has_metrics': has_metrics
                            }
                            all_job_ads.append(job_ad)
    
    seen_ids = set()
    unique_ads = []
    for ad in all_job_ads:
        if ad['id'] not in seen_ids:
            seen_ids.add(ad['id'])
            unique_ads.append(ad)
    
    all_job_ads = unique_ads
    all_job_ads.sort(key=lambda x: (
        x.get('has_metrics', False) if x.get('has_metrics') is not None else False
    ), reverse=True)
    
    return all_job_ads

def display_job_ads(job_ads):
    if not job_ads:
        return
    
    for i, job_ad in enumerate(job_ads, 1):
        metrics_indicator = "🔥" if job_ad.get('has_metrics', False) else ""
        
        spend_display = job_ad['spend']
        if isinstance(spend_display, dict):
            lower = spend_display.get('lower_bound', '0')
            upper = spend_display.get('upper_bound', lower)
            spend_display = f"${lower}-${upper}"
        
        impressions_display = job_ad['impressions']
        if isinstance(impressions_display, dict):
            lower = impressions_display.get('lower_bound', '0')
            upper = impressions_display.get('upper_bound', lower)
            impressions_display = f"{lower}-{upper}"
        
        audience_display = job_ad['estimated_audience_size']
        if isinstance(audience_display, dict):
            lower = audience_display.get('lower_bound', '0')
            upper = audience_display.get('upper_bound', lower)
            audience_display = f"{lower}-{upper}"



def save_job_ads(job_ads):
    if not job_ads:
        return None
    
    csv_filename = f"data_analyst_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'ad_id', 'company', 'search_term', 'country', 'creation_date', 
                'delivery_start', 'delivery_stop', 'spend_lower', 'spend_upper', 
                'impressions_lower', 'impressions_upper', 'audience_size_lower', 
                'audience_size_upper', 'job_titles', 'descriptions', 'ad_content',
                'platforms', 'languages', 'has_metrics', 'ad_url'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for ad in job_ads:
                spend = ad.get('spend', 'N/A')
                spend_lower = spend_upper = 'N/A'
                if isinstance(spend, dict):
                    spend_lower = spend.get('lower_bound', 'N/A')
                    spend_upper = spend.get('upper_bound', 'N/A')
                
                impressions = ad.get('impressions', 'N/A')
                impressions_lower = impressions_upper = 'N/A'
                if isinstance(impressions, dict):
                    impressions_lower = impressions.get('lower_bound', 'N/A')
                    impressions_upper = impressions.get('upper_bound', 'N/A')
                
                audience_size = ad.get('estimated_audience_size', 'N/A')
                audience_lower = audience_upper = 'N/A'
                if isinstance(audience_size, dict):
                    audience_lower = audience_size.get('lower_bound', 'N/A')
                    audience_upper = audience_size.get('upper_bound', 'N/A')
                
                row = {
                    'ad_id': ad.get('id', ''),
                    'company': ad.get('company', ''),
                    'search_term': ad.get('search_term', ''),
                    'country': ad.get('country', ''),
                    'creation_date': ad.get('creation_date', ''),
                    'delivery_start': ad.get('delivery_start', ''),
                    'delivery_stop': ad.get('delivery_stop', ''),
                    'spend_lower': spend_lower,
                    'spend_upper': spend_upper,
                    'impressions_lower': impressions_lower,
                    'impressions_upper': impressions_upper,
                    'audience_size_lower': audience_lower,
                    'audience_size_upper': audience_upper,
                    'job_titles': '; '.join(ad.get('job_titles', [])),
                    'descriptions': '; '.join(ad.get('descriptions', [])),
                    'ad_content': '; '.join(ad.get('ad_creative_bodies', []))[:500],
                    'platforms': ', '.join(ad.get('publisher_platforms', [])),
                    'languages': ', '.join(ad.get('languages', [])),
                    'has_metrics': ad.get('has_metrics', False),
                    'ad_url': ad.get('ad_snapshot_url', '')
                }
                
                writer.writerow(row)
        
        return csv_filename
        
    except Exception as e:
        return None

def main():
    job_ads = extract_job_ads()
    
    if job_ads:
        display_job_ads(job_ads)
        filename = save_job_ads(job_ads)

if __name__ == "__main__":
    main()