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
    # MODIFY SEARCH TERMS HERE
    # Regular searches (non-India)
    search_configurations = [
        {
            'terms': ['analyst'],
            'countries': ['US'],
            'limit': 1000,
            'ad_type': 'ALL'
        },
        {
            'terms': ['analyst'],
            'countries': ['GB'],
            'limit': 1000,
            'ad_type': 'ALL'
        },
        {
            'terms': ['analyst'],
            'countries': ['US'],
            'limit': 1000,
            'ad_type': 'POLITICAL_AND_ISSUE_ADS'
        },
        {
            'terms': ['analyst'],
            'countries': ['CA'],
            'limit': 500,
            'ad_type': 'ALL'
        }
    ]
    
    # India-specific searches
    india_search_configurations = [
        {
            'terms': ['analyst'],
            'countries': ['IN'],
            'limit': 1000,
            'ad_type': 'ALL'
        },
        {
            'terms': ['analyst'],
            'countries': ['IN'],
            'limit': 1000,
            'ad_type': 'POLITICAL_AND_ISSUE_ADS'
        }
    ]
    
    all_job_ads = []
    india_job_ads = []
    
    # Process regular searches
    for config in search_configurations:
        for search_term in config['terms']:
            for country in config['countries']:
                print(f"Searching for: '{search_term}' in {country} (type: {config['ad_type']})")
                
                params = {
                    'access_token': ACCESS_TOKEN,
                    'ad_type': config['ad_type'],
                    'ad_reached_countries': country,
                    'search_terms': search_term,
                    'limit': config['limit'],
                    'fields': 'id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,page_name,ad_creative_link_titles,ad_creative_link_descriptions,ad_creative_link_captions,spend,impressions,publisher_platforms,estimated_audience_size,languages,ad_snapshot_url,ad_creative_bodies,demographic_distribution,target_gender,target_ages,target_locations,age_country_gender_reach_breakdown'
                }
        
                result = make_request(ADS_LIBRARY_BASE, params)
                
                if result and 'data' in result:
                    ads = result['data']
                    print(f"Found {len(ads)} ads for '{search_term}' in {country} (type: {config['ad_type']})")
                    
                    for ad in ads:
                        impressions = ad.get('impressions')
                        spend = ad.get('spend')
                        
                        has_impressions = (impressions and impressions != 'N/A' and 
                                         (isinstance(impressions, dict) or 
                                          (isinstance(impressions, str) and impressions.strip() != '')))
                        has_spend = (spend and spend != 'N/A' and 
                                   (isinstance(spend, dict) or 
                                    (isinstance(spend, str) and spend.strip() != '')))
                        
                        has_metrics = has_impressions or has_spend
                        
                        gender_info = {}
                        if 'demographic_distribution' in ad:
                            gender_info['demographic_distribution'] = ad['demographic_distribution']
                        if 'target_gender' in ad:
                            gender_info['target_gender'] = ad['target_gender']
                        if 'target_ages' in ad:
                            gender_info['target_ages'] = ad['target_ages']
                        if 'age_country_gender_reach_breakdown' in ad:
                            gender_info['age_country_gender_reach_breakdown'] = ad['age_country_gender_reach_breakdown']
                        
                        job_ad = {
                            'search_term': search_term,
                            'country': country,
                            'ad_type': config['ad_type'],
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
                            'has_metrics': has_metrics,
                            'gender_info': gender_info
                        }
                        all_job_ads.append(job_ad)
    
    # Process India searches
    for config in india_search_configurations:
        for search_term in config['terms']:
            for country in config['countries']:
                print(f"Searching for: '{search_term}' in {country} (type: {config['ad_type']}) - INDIA SPECIFIC")
                
                params = {
                    'access_token': ACCESS_TOKEN,
                    'ad_type': config['ad_type'],
                    'ad_reached_countries': country,
                    'search_terms': search_term,
                    'limit': config['limit'],
                    'fields': 'id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,page_name,ad_creative_link_titles,ad_creative_link_descriptions,ad_creative_link_captions,spend,impressions,publisher_platforms,estimated_audience_size,languages,ad_snapshot_url,ad_creative_bodies,demographic_distribution,target_gender,target_ages,target_locations,age_country_gender_reach_breakdown'
                }
        
                result = make_request(ADS_LIBRARY_BASE, params)
                
                if result and 'data' in result:
                    ads = result['data']
                    print(f"Found {len(ads)} ads for '{search_term}' in {country} (type: {config['ad_type']}) - INDIA SPECIFIC")
                    
                    for ad in ads:
                        impressions = ad.get('impressions')
                        spend = ad.get('spend')
                        
                        has_impressions = (impressions and impressions != 'N/A' and 
                                         (isinstance(impressions, dict) or 
                                          (isinstance(impressions, str) and impressions.strip() != '')))
                        has_spend = (spend and spend != 'N/A' and 
                                   (isinstance(spend, dict) or 
                                    (isinstance(spend, str) and spend.strip() != '')))
                        
                        has_metrics = has_impressions or has_spend
                        
                        gender_info = {}
                        if 'demographic_distribution' in ad:
                            gender_info['demographic_distribution'] = ad['demographic_distribution']
                        if 'target_gender' in ad:
                            gender_info['target_gender'] = ad['target_gender']
                        if 'target_ages' in ad:
                            gender_info['target_ages'] = ad['target_ages']
                        if 'age_country_gender_reach_breakdown' in ad:
                            gender_info['age_country_gender_reach_breakdown'] = ad['age_country_gender_reach_breakdown']
                        
                        job_ad = {
                            'search_term': search_term,
                            'country': country,
                            'ad_type': config['ad_type'],
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
                            'has_metrics': has_metrics,
                            'gender_info': gender_info
                        }
                        india_job_ads.append(job_ad)
    
    # Remove duplicates from regular ads
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
    
    # Remove duplicates from India ads
    seen_india_ids = set()
    unique_india_ads = []
    for ad in india_job_ads:
        if ad['id'] not in seen_india_ids:
            seen_india_ids.add(ad['id'])
            unique_india_ads.append(ad)
    
    india_job_ads = unique_india_ads
    india_job_ads.sort(key=lambda x: (
        x.get('has_metrics', False) if x.get('has_metrics') is not None else False
    ), reverse=True)
    
    return all_job_ads, india_job_ads

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



def save_job_ads(job_ads, region="global"):
    if not job_ads:
        return None
    
    if region == "india":
        csv_filename = f"analyst_ads_india_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        csv_filename = f"analyst_ads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'ad_id', 'company', 'search_term', 'country', 'ad_type', 'creation_date', 
                'delivery_start', 'delivery_stop', 'spend_lower', 'spend_upper', 
                'impressions_lower', 'impressions_upper', 'audience_size_lower', 
                'audience_size_upper', 'job_titles', 'descriptions', 'ad_content',
                'platforms', 'languages', 'has_metrics', 'ad_url',
                'demographic_distribution', 'target_gender', 'target_ages', 
                'age_country_gender_reach_breakdown'
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
                
                gender_info = ad.get('gender_info', {})
                demographic_distribution = json.dumps(gender_info.get('demographic_distribution', '')) if gender_info.get('demographic_distribution') else 'N/A'
                target_gender = gender_info.get('target_gender', 'N/A')
                target_ages = json.dumps(gender_info.get('target_ages', '')) if gender_info.get('target_ages') else 'N/A'
                age_country_gender_breakdown = json.dumps(gender_info.get('age_country_gender_reach_breakdown', '')) if gender_info.get('age_country_gender_reach_breakdown') else 'N/A'
                
                row = {
                    'ad_id': ad.get('id', ''),
                    'company': ad.get('company', ''),
                    'search_term': ad.get('search_term', ''),
                    'country': ad.get('country', ''),
                    'ad_type': ad.get('ad_type', ''),
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
                    'ad_url': ad.get('ad_snapshot_url', ''),
                    'demographic_distribution': demographic_distribution,
                    'target_gender': target_gender,
                    'target_ages': target_ages,
                    'age_country_gender_reach_breakdown': age_country_gender_breakdown
                }
                
                writer.writerow(row)
        
        return csv_filename
        
    except Exception as e:
        return None

def main():
    job_ads, india_job_ads = extract_job_ads()
    
    print(f"\n=== SUMMARY ===")
    print(f"Global ads found: {len(job_ads)}")
    print(f"India ads found: {len(india_job_ads)}")
    
    # Save global ads
    if job_ads:
        print("\nProcessing global ads...")
        display_job_ads(job_ads)
        filename = save_job_ads(job_ads, "global")
        if filename:
            print(f"Global ads saved to: {filename}")
    
    # Save India ads
    if india_job_ads:
        print("\nProcessing India ads...")
        display_job_ads(india_job_ads)
        india_filename = save_job_ads(india_job_ads, "india")
        if india_filename:
            print(f"India ads saved to: {india_filename}")
    
    if not job_ads and not india_job_ads:
        print("No ads found in any region.")

if __name__ == "__main__":
    main()