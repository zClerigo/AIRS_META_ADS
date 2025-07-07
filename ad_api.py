import requests
import json
import csv
from datetime import datetime

ACCESS_TOKEN = "EAAKFAZBK4LOQBPFW4L04ohmLrhNlcUiy1H038o5HWYWmqYF19Ihq3Ws2mUWpybZA7ca4QOzmUiiSLOXfxiKLyHjgZA1AggptgorHHuyOQLl28gA3bTv9uumKodO9XzZBIvSnmhEan8u0GT4DOO4ZBGAvgYttOpGgFnN6LOFOPfWTFvdAarEcJ42y634IzZApfmYNmMfQQy1YJW"

ADS_LIBRARY_BASE = "https://graph.facebook.com/v18.0/ads_archive"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def make_request(url, params=None):
    """Make API request with basic error handling"""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def extract_job_ads():
    """Extract data analyst job ads from Meta's Ads Library"""
    print_section("🔍 Extracting Data Analyst Job Ads")
    print("🎯 Searching for job-related ads and major company recruiters")
    print("📊 Collecting all relevant ads regardless of metrics availability")
    
    # Search parameters - broader search for job-related ads
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
                print(f"\n🔍 Searching for: '{search_term}' in {country}")
                
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
                    
                    # Filter for job-related ads and ads with actual data
                    job_keywords = ['job', 'career', 'position', 'hire', 'hiring', 'apply', 'work', 'employment', 'opportunity', 'team', 'role', 'analyst', 'engineer', 'scientist']
                    
                    # Also look for major tech companies and known employers
                    company_keywords = ['google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix', 'uber', 'airbnb', 'tesla', 'salesforce', 'oracle', 'ibm', 'accenture', 'deloitte', 'pwc', 'kpmg', 'ey']
                    
                    for ad in ads:
                        # Check if this looks like a job ad or from a major company
                        page_name = ad.get('page_name', '').lower()
                        link_titles = ad.get('ad_creative_link_titles', [])
                        link_descriptions = ad.get('ad_creative_link_descriptions', [])
                        ad_bodies = ad.get('ad_creative_bodies', [])
                        
                        # Combine all text to search for keywords
                        all_text = f"{page_name} {' '.join(link_titles)} {' '.join(link_descriptions)} {' '.join(ad_bodies)}".lower()
                        
                        # Check if it contains job-related keywords OR is from a major company
                        has_job_keywords = any(keyword in all_text for keyword in job_keywords)
                        is_major_company = any(company in page_name for company in company_keywords)
                        
                        # Prioritize ads with impression or spend data
                        impressions = ad.get('impressions')
                        spend = ad.get('spend')
                        
                        # Handle both string and object formats for impressions and spend
                        has_impressions = (impressions and impressions != 'N/A' and 
                                         (isinstance(impressions, dict) or 
                                          (isinstance(impressions, str) and impressions.strip() != '')))
                        has_spend = (spend and spend != 'N/A' and 
                                   (isinstance(spend, dict) or 
                                    (isinstance(spend, str) and spend.strip() != '')))
                        
                        has_metrics = has_impressions or has_spend
                        
                        if (has_job_keywords or is_major_company):
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
                                'has_metrics': has_metrics,
                                'is_major_company': is_major_company
                            }
                            all_job_ads.append(job_ad)
                else:
                    print(f"❌ No results for '{search_term}' in {country}")
    
    # Remove duplicates based on ad ID
    seen_ids = set()
    unique_ads = []
    for ad in all_job_ads:
        if ad['id'] not in seen_ids:
            seen_ids.add(ad['id'])
            unique_ads.append(ad)
    
    all_job_ads = unique_ads
    
    # Sort by priority: ads with metrics first, then major companies, then others
    all_job_ads.sort(key=lambda x: (
        x.get('has_metrics', False) if x.get('has_metrics') is not None else False,
        x.get('is_major_company', False) if x.get('is_major_company') is not None else False
    ), reverse=True)
    
    return all_job_ads

def display_job_ads(job_ads):
    """Display extracted job ads in a formatted way"""
    print_section(f"📋 Found {len(job_ads)} Data Analyst Job Ads")
    
    if not job_ads:
        print("❌ No job ads found. Try running the script again later.")
        return
    
    # Show summary of data quality
    with_metrics = sum(1 for ad in job_ads if ad.get('has_metrics', False))
    major_companies = sum(1 for ad in job_ads if ad.get('is_major_company', False))
    with_impressions = sum(1 for ad in job_ads if ad.get('impressions') and ad.get('impressions') != 'N/A' and (isinstance(ad.get('impressions'), dict) or (isinstance(ad.get('impressions'), str) and ad.get('impressions').strip() != '')))
    with_spend = sum(1 for ad in job_ads if ad.get('spend') and ad.get('spend') != 'N/A' and (isinstance(ad.get('spend'), dict) or (isinstance(ad.get('spend'), str) and ad.get('spend').strip() != '')))
    
    print(f"📊 Data Quality Summary:")
    print(f"   🔥 Ads with metrics: {with_metrics}/{len(job_ads)}")
    print(f"   ⭐ Major companies: {major_companies}/{len(job_ads)}")
    print(f"   👀 With impressions: {with_impressions}/{len(job_ads)}")
    print(f"   💰 With spend data: {with_spend}/{len(job_ads)}")
    print(f"   🌍 Countries covered: {len(set(ad.get('country', 'N/A') for ad in job_ads))}")
    print("")
    
    for i, job_ad in enumerate(job_ads, 1):
        # Highlight ads with metrics
        metrics_indicator = "🔥" if job_ad.get('has_metrics', False) else ""
        company_indicator = "⭐" if job_ad.get('is_major_company', False) else ""
        
        print(f"\n📋 JOB AD #{i} {metrics_indicator} {company_indicator}")
        print(f"Search Term: {job_ad['search_term']} (Country: {job_ad.get('country', 'N/A')})")
        print(f"Company: {job_ad['company']}")
        print(f"Ad ID: {job_ad['id']}")
        print(f"Created: {job_ad['creation_date']}")
        print(f"Delivery: {job_ad['delivery_start']} to {job_ad['delivery_stop']}")
        # Format spend for display
        spend_display = job_ad['spend']
        if isinstance(spend_display, dict):
            lower = spend_display.get('lower_bound', '0')
            upper = spend_display.get('upper_bound', lower)
            spend_display = f"${lower}-${upper}"
        
        # Format impressions for display
        impressions_display = job_ad['impressions']
        if isinstance(impressions_display, dict):
            lower = impressions_display.get('lower_bound', '0')
            upper = impressions_display.get('upper_bound', lower)
            impressions_display = f"{lower}-{upper}"
        
        # Format audience size for display
        audience_display = job_ad['estimated_audience_size']
        if isinstance(audience_display, dict):
            lower = audience_display.get('lower_bound', '0')
            upper = audience_display.get('upper_bound', lower)
            audience_display = f"{lower}-{upper}"
        
        print(f"💰 Spend: {spend_display}")
        print(f"👀 Impressions: {impressions_display}")
        print(f"🎯 Audience Size: {audience_display}")
        
        if job_ad.get('has_metrics', False):
            print("🔥 HAS METRICS - This ad has impression or spending data!")
        if job_ad.get('is_major_company', False):
            print("⭐ MAJOR COMPANY - This is from a well-known employer!")
        
        if job_ad['job_titles']:
            print(f"📋 Job Titles: {', '.join(job_ad['job_titles'])}")
        
        if job_ad['descriptions']:
            print("📝 Descriptions:")
            for desc in job_ad['descriptions']:
                print(f"  • {desc}")
        
        if job_ad['ad_creative_bodies']:
            print("📄 Ad Content:")
            for body in job_ad['ad_creative_bodies'][:2]:  # Show first 2
                if body:
                    print(f"  • {body[:100]}..." if len(body) > 100 else f"  • {body}")
        
        if job_ad['publisher_platforms']:
            print(f"📱 Platforms: {', '.join(job_ad['publisher_platforms'])}")
        
        if job_ad['languages']:
            print(f"🌐 Languages: {', '.join(job_ad['languages'])}")
        
        if job_ad['ad_snapshot_url']:
            print(f"🔗 Ad Preview: {job_ad['ad_snapshot_url']}")
        
        print("-" * 40)

def analyze_job_ads(job_ads):
    """Analyze the extracted job ads with comprehensive insights"""
    print_section("📊 Comprehensive Job Market Analysis")
    
    if not job_ads:
        return
    
    # Basic stats
    print(f"📊 Total job ads analyzed: {len(job_ads)}")
    
    # Companies analysis
    companies = [ad['company'] for ad in job_ads if ad['company']]
    unique_companies = set(companies)
    print(f"🏢 Unique companies: {len(unique_companies)}")
    
    if unique_companies:
        print("Top companies hiring:")
        for company in sorted(unique_companies)[:10]:  # Show top 10
            print(f"  • {company}")
    
    # Search terms breakdown
    search_breakdown = {}
    for ad in job_ads:
        term = ad['search_term']
        search_breakdown[term] = search_breakdown.get(term, 0) + 1
    
    print(f"\n📋 Job ads by search term:")
    for term, count in search_breakdown.items():
        print(f"  • {term}: {count} ads")
    
    # Impressions analysis
    print_section("👀 Impressions & Reach Analysis")
    impressions_data = []
    for ad in job_ads:
        impressions = ad.get('impressions')
        if impressions and impressions != 'N/A':
            try:
                # Handle different impression formats
                if isinstance(impressions, dict):
                    # Handle API object format with lower_bound and upper_bound
                    lower = int(impressions.get('lower_bound', 0))
                    upper = int(impressions.get('upper_bound', lower))
                    avg_impressions = (lower + upper) / 2
                elif isinstance(impressions, str):
                    # Parse range like "1,000-5,000"
                    if '-' in impressions:
                        range_parts = impressions.replace(',', '').split('-')
                        avg_impressions = (int(range_parts[0]) + int(range_parts[1])) / 2
                    else:
                        avg_impressions = int(impressions.replace(',', ''))
                else:
                    avg_impressions = int(impressions)
                
                impressions_data.append({
                    'company': ad['company'],
                    'impressions': avg_impressions,
                    'spend': ad.get('spend', 'N/A'),
                    'audience_size': ad.get('estimated_audience_size', 'N/A')
                })
            except (ValueError, TypeError):
                pass
    
    if impressions_data:
        total_impressions = sum(d['impressions'] for d in impressions_data)
        avg_impressions = total_impressions / len(impressions_data)
        
        print(f"📊 Ads with impression data: {len(impressions_data)}")
        print(f"📊 Total impressions: {total_impressions:,}")
        print(f"📊 Average impressions per ad: {avg_impressions:,.0f}")
        
        # Top performing ads by impressions
        sorted_impressions = sorted(impressions_data, key=lambda x: x['impressions'], reverse=True)
        print("\n🏆 Top performing ads by impressions:")
        for i, ad in enumerate(sorted_impressions[:5], 1):
            print(f"  {i}. {ad['company']}: {ad['impressions']:,} impressions")
    
    # Spending analysis
    print_section("💰 Spending Analysis")
    spending_data = []
    for ad in job_ads:
        spend = ad.get('spend')
        if spend and spend != 'N/A':
            try:
                # Handle different spend formats
                if isinstance(spend, dict):
                    # Handle API object format with lower_bound and upper_bound
                    lower = float(spend.get('lower_bound', 0))
                    upper = float(spend.get('upper_bound', lower))
                    avg_spend = (lower + upper) / 2
                elif isinstance(spend, str):
                    spend_str = spend.replace('$', '').replace(',', '')
                    if '-' in spend_str:
                        range_parts = spend_str.split('-')
                        avg_spend = (float(range_parts[0]) + float(range_parts[1])) / 2
                    else:
                        avg_spend = float(spend_str)
                else:
                    avg_spend = float(spend)
                
                spending_data.append({
                    'company': ad['company'],
                    'spend': avg_spend,
                    'impressions': ad.get('impressions', 'N/A')
                })
            except (ValueError, TypeError):
                pass
    
    if spending_data:
        total_spend = sum(d['spend'] for d in spending_data)
        avg_spend = total_spend / len(spending_data)
        
        print(f"💰 Ads with spending data: {len(spending_data)}")
        print(f"💰 Total ad spend: ${total_spend:,.2f}")
        print(f"💰 Average spend per ad: ${avg_spend:.2f}")
        
        # Top spending companies
        sorted_spending = sorted(spending_data, key=lambda x: x['spend'], reverse=True)
        print("\n🏆 Top spending companies:")
        for i, ad in enumerate(sorted_spending[:5], 1):
            print(f"  {i}. {ad['company']}: ${ad['spend']:,.2f}")
    
    # Content analysis
    print_section("📄 Ad Content Analysis")
    all_content = []
    for ad in job_ads:
        if ad.get('ad_creative_bodies'):
            all_content.extend(ad['ad_creative_bodies'])
    
    if all_content:
        print(f"📄 Total ad content pieces: {len(all_content)}")
        
        # Analyze common keywords in ad content
        content_text = ' '.join(all_content).lower()
        content_keywords = ['remote', 'hybrid', 'onsite', 'python', 'sql', 'excel', 'tableau', 'power bi', 'experience', 'years', 'bachelor', 'degree', 'skills', 'benefits', 'salary', 'competitive']
        
        print("Common keywords in ad content:")
        keyword_counts = []
        for keyword in content_keywords:
            count = content_text.count(keyword)
            if count > 0:
                keyword_counts.append((keyword, count))
        
        # Sort by count and show top keywords
        for keyword, count in sorted(keyword_counts, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • '{keyword}': {count} mentions")
    
    # Note about deprecated fields
    print_section("📊 Data Availability Note")
    print("ℹ️  Geographic and demographic distribution data is not available")
    print("   in the current API version (v18.0). The following data is available:")
    print("   • Company information and job titles")
    print("   • Impressions and spending data") 
    print("   • Platform distribution")
    print("   • Ad content and descriptions")
    print("   • Audience size estimates")
    
    # Platform analysis
    print_section("📱 Platform Analysis")
    all_platforms = []
    for ad in job_ads:
        if ad.get('publisher_platforms'):
            all_platforms.extend(ad['publisher_platforms'])
    
    if all_platforms:
        platform_counts = {}
        for platform in all_platforms:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        print("Most used platforms:")
        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {platform}: {count} ads")
    
    # Job titles analysis
    print_section("📋 Job Titles Analysis")
    all_titles = []
    for ad in job_ads:
        all_titles.extend(ad.get('job_titles', []))
    
    if all_titles:
        print(f"📋 Total job titles found: {len(all_titles)}")
        # Count keywords in titles
        title_text = ' '.join(all_titles).lower()
        keywords = ['analyst', 'data', 'scientist', 'engineer', 'business', 'senior', 'junior', 'remote', 'entry', 'lead', 'manager']
        
        print("Most common keywords in job titles:")
        keyword_counts = []
        for keyword in keywords:
            count = title_text.count(keyword)
            if count > 0:
                keyword_counts.append((keyword, count))
        
        # Sort by count
        for keyword, count in sorted(keyword_counts, key=lambda x: x[1], reverse=True):
            print(f"  • '{keyword}': {count} mentions")
    
    # Key insights
    print_section("💡 Key Market Insights")
    print("🎯 Platform & Content Insights:")
    print("• Multi-platform approach (Facebook, Instagram, etc.) is common for recruitment")
    print("• Ad spending varies significantly, indicating different recruitment budgets")
    print("• Ad content reveals key skills and requirements companies are seeking")
    print("\n📊 Impression & Spending Insights:")
    print("• High impression volumes suggest strong competition for data analyst talent")
    print("• Impressions data helps identify which companies are investing heavily in recruitment")
    print("• Cost-per-impression metrics reveal recruitment efficiency strategies")
    print("\n🚀 Actionable Recommendations:")
    print("• Target applications to companies with highest ad spend (shows hiring urgency)")
    print("• Focus on roles with high impression counts (indicates active recruitment)")
    print("• Analyze ad content for trending skills and requirements")
    print("• Consider platform preferences to understand company recruitment strategies")
    print("• Use audience size data to gauge market demand for specific roles")

def create_market_summary(job_ads):
    """Create a comprehensive market summary report"""
    if not job_ads:
        return {}
    
    # Calculate key metrics
    total_ads = len(job_ads)
    companies = list(set(ad['company'] for ad in job_ads if ad['company']))
    
    # Impression metrics
    total_impressions = 0
    impression_count = 0
    for ad in job_ads:
        impressions = ad.get('impressions')
        if impressions and impressions != 'N/A':
            try:
                if isinstance(impressions, dict):
                    # Handle API object format with lower_bound and upper_bound
                    lower = int(impressions.get('lower_bound', 0))
                    upper = int(impressions.get('upper_bound', lower))
                    avg_impressions = (lower + upper) / 2
                elif isinstance(impressions, str) and '-' in impressions:
                    range_parts = impressions.replace(',', '').split('-')
                    avg_impressions = (int(range_parts[0]) + int(range_parts[1])) / 2
                else:
                    avg_impressions = int(str(impressions).replace(',', ''))
                total_impressions += avg_impressions
                impression_count += 1
            except (ValueError, TypeError):
                pass
    
    # Spending metrics
    total_spend = 0
    spend_count = 0
    for ad in job_ads:
        spend = ad.get('spend')
        if spend and spend != 'N/A':
            try:
                if isinstance(spend, dict):
                    # Handle API object format with lower_bound and upper_bound
                    lower = float(spend.get('lower_bound', 0))
                    upper = float(spend.get('upper_bound', lower))
                    avg_spend = (lower + upper) / 2
                elif isinstance(spend, str):
                    spend_str = spend.replace('$', '').replace(',', '')
                    if '-' in spend_str:
                        range_parts = spend_str.split('-')
                        avg_spend = (float(range_parts[0]) + float(range_parts[1])) / 2
                    else:
                        avg_spend = float(spend_str)
                else:
                    avg_spend = float(spend)
                total_spend += avg_spend
                spend_count += 1
            except (ValueError, TypeError):
                pass
    
    # Platform analysis
    all_platforms = []
    for ad in job_ads:
        if ad.get('publisher_platforms'):
            all_platforms.extend(ad['publisher_platforms'])
    
    platform_counts = {}
    for platform in all_platforms:
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    # Search term analysis
    search_breakdown = {}
    for ad in job_ads:
        term = ad['search_term']
        search_breakdown[term] = search_breakdown.get(term, 0) + 1
    
    summary = {
        'total_ads': total_ads,
        'unique_companies': len(companies),
        'total_impressions': total_impressions,
        'average_impressions': total_impressions / impression_count if impression_count > 0 else 0,
        'total_spend': total_spend,
        'average_spend': total_spend / spend_count if spend_count > 0 else 0,
        'cost_per_impression': total_spend / total_impressions if total_impressions > 0 else 0,
        'top_platforms': sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        'search_breakdown': search_breakdown,
        'companies': companies[:20]  # Top 20 companies
    }
    
    return summary

def save_job_ads(job_ads):
    """Save job ads to CSV file with summary report"""
    if not job_ads:
        return None
    
    # Create summary
    summary = create_market_summary(job_ads)
    
    # CSV filename
    csv_filename = f"data_analyst_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        # Save job ads to CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define CSV headers
            fieldnames = [
                'ad_id', 'company', 'search_term', 'country', 'creation_date', 
                'delivery_start', 'delivery_stop', 'spend_lower', 'spend_upper', 
                'impressions_lower', 'impressions_upper', 'audience_size_lower', 
                'audience_size_upper', 'job_titles', 'descriptions', 'ad_content',
                'platforms', 'languages', 'has_metrics', 'is_major_company', 'ad_url'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write each job ad
            for ad in job_ads:
                # Format spend data
                spend = ad.get('spend', 'N/A')
                spend_lower = spend_upper = 'N/A'
                if isinstance(spend, dict):
                    spend_lower = spend.get('lower_bound', 'N/A')
                    spend_upper = spend.get('upper_bound', 'N/A')
                
                # Format impressions data
                impressions = ad.get('impressions', 'N/A')
                impressions_lower = impressions_upper = 'N/A'
                if isinstance(impressions, dict):
                    impressions_lower = impressions.get('lower_bound', 'N/A')
                    impressions_upper = impressions.get('upper_bound', 'N/A')
                
                # Format audience size data
                audience_size = ad.get('estimated_audience_size', 'N/A')
                audience_lower = audience_upper = 'N/A'
                if isinstance(audience_size, dict):
                    audience_lower = audience_size.get('lower_bound', 'N/A')
                    audience_upper = audience_size.get('upper_bound', 'N/A')
                
                # Prepare CSV row
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
                    'ad_content': '; '.join(ad.get('ad_creative_bodies', []))[:500],  # Truncate for CSV
                    'platforms': ', '.join(ad.get('publisher_platforms', [])),
                    'languages': ', '.join(ad.get('languages', [])),
                    'has_metrics': ad.get('has_metrics', False),
                    'is_major_company': ad.get('is_major_company', False),
                    'ad_url': ad.get('ad_snapshot_url', '')
                }
                
                writer.writerow(row)
        
        print(f"\n💾 Job ads saved to CSV: {csv_filename}")
        
        # Also save a simple summary report
        summary_filename = f"market_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_filename, 'w') as f:
            f.write("DATA ANALYST JOB MARKET SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Job Ads: {summary['total_ads']}\n")
            f.write(f"Unique Companies: {summary['unique_companies']}\n")
            f.write(f"Total Impressions: {summary['total_impressions']:,}\n")
            f.write(f"Average Impressions: {summary['average_impressions']:,.0f}\n")
            f.write(f"Total Ad Spend: ${summary['total_spend']:,.2f}\n")
            f.write(f"Average Ad Spend: ${summary['average_spend']:.2f}\n")
            f.write(f"Cost per Impression: ${summary['cost_per_impression']:.4f}\n\n")
            
            f.write("TOP PLATFORMS:\n")
            for platform, count in summary['top_platforms']:
                f.write(f"  • {platform}: {count} ads\n")
            
            f.write("\nSEARCH TERM BREAKDOWN:\n")
            for term, count in summary['search_breakdown'].items():
                f.write(f"  • {term}: {count} ads\n")
            
            f.write("\nCOMPANIES HIRING:\n")
            for company in summary['companies']:
                f.write(f"  • {company}\n")
        
        print(f"📄 Summary report saved to: {summary_filename}")
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Data Analyst Job Ads Extractor")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract job ads
    job_ads = extract_job_ads()
    
    if job_ads:
        # Display results
        display_job_ads(job_ads)
        
        # Analyze data
        analyze_job_ads(job_ads)
        
        # Save to file
        filename = save_job_ads(job_ads)
        
        print_section("✅ Enhanced Extraction Complete")
        print(f"📊 Successfully extracted {len(job_ads)} job ads")
        
        # Show improvement summary
        with_metrics = sum(1 for ad in job_ads if ad.get('has_metrics', False))
        major_companies = sum(1 for ad in job_ads if ad.get('is_major_company', False))
        
        print(f"\n🔥 Enhanced Search Results:")
        print(f"   • {with_metrics} ads with actual impression/spend data")
        print(f"   • {major_companies} ads from major companies")
        print(f"   • {len(job_ads) - with_metrics} ads with N/A metrics (still valuable for content analysis)")
        print(f"   • Multi-country search (US, CA, GB)")
        print(f"   • Broader search terms and company targeting")
        print(f"   • Duplicate removal and priority sorting")
        
        if filename:
            print(f"\n💾 Data saved to CSV: {filename}")
            print("📊 CSV columns include:")
            print("   • Company & job info (company, job_titles, descriptions)")
            print("   • Performance metrics (spend_lower/upper, impressions_lower/upper)")
            print("   • Targeting data (audience_size, platforms, languages)")
            print("   • Content analysis (ad_content, has_metrics, is_major_company)")
        
        print("\n🎯 Rich Data & Insights Available:")
        print("• 👀 Impressions data - see how many people viewed each ad")
        print("• 💰 Spending patterns - understand recruitment budgets")
        print("• 📄 Ad content analysis - extract keywords and requirements")
        print("• 📱 Platform distribution - see where companies advertise")
        print("• 📊 Market analysis - competitive landscape insights")
        print("• 🏆 Top performers - identify high-spending/high-impression ads")
        print("• 📈 Cost efficiency - cost per impression metrics")
        print("• 🎯 Audience sizing - estimated reach of job ads")
        print("• 📋 Excel/spreadsheet ready - analyze in your favorite tool")
        
        print("\n🎯 Use this data to:")
        print("• Target applications to companies with highest ad spend (shows hiring urgency)")
        print("• Focus on roles with high impression counts (indicates active recruitment)")
        print("• Understand competitive landscape and recruitment spending patterns")
        print("• Identify high-demand skills from ad content analysis")
        print("• Find companies using multi-platform recruitment strategies")
        print("• Analyze job requirements and qualifications mentioned in ads")
        print("• Optimize your job search strategy based on market spending data")
        
    else:
        print("❌ No job ads found. Please check your access token and try again.")

if __name__ == "__main__":
    main()
