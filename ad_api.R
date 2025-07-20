# Load required libraries
library(httr)
library(jsonlite)
library(dplyr)
library(readr)
library(purrr)

# Configuration
ACCESS_TOKEN <- "EAAKFAZBK4LOQBPFW4L04ohmLrhNlcUiy1H038o5HWYWmqYF19Ihq3Ws2mUWpybZA7ca4QOzmUiiSLOXfxiKLyHjgZA1AggptgorHHuyOQLl28gA3bTv9uumKodO9XzZBIvSnmhEan8u0GT4DOO4ZBGAvgYttOpGgFnN6LOFOPfWTFvdAarEcJ42y634IzZApfmYNmMfQQy1YJW"
ADS_LIBRARY_BASE <- "https://graph.facebook.com/v18.0/ads_archive"

# Function to make HTTP requests
make_request <- function(url, params = NULL) {
  tryCatch({
    response <- GET(url, query = params)
    
    if (status_code(response) == 200) {
      return(content(response, "parsed"))
    } else {
      cat("Error: HTTP", status_code(response), "\n")
      return(NULL)
    }
  }, error = function(e) {
    cat("Request failed:", e$message, "\n")
    return(NULL)
  })
}

# Function to process gender information
process_gender_info <- function(ad) {
  gender_info <- list()
  
  if ("demographic_distribution" %in% names(ad)) {
    gender_info$demographic_distribution <- ad$demographic_distribution
  }
  if ("target_gender" %in% names(ad)) {
    gender_info$target_gender <- ad$target_gender
  }
  if ("target_ages" %in% names(ad)) {
    gender_info$target_ages <- ad$target_ages
  }
  if ("age_country_gender_reach_breakdown" %in% names(ad)) {
    gender_info$age_country_gender_reach_breakdown <- ad$age_country_gender_reach_breakdown
  }
  
  return(gender_info)
}

# Function to check if ad has metrics
has_ad_metrics <- function(impressions, spend) {
  has_impressions <- !is.null(impressions) && 
                    impressions != "N/A" && 
                    (is.list(impressions) || (is.character(impressions) && nchar(trimws(impressions)) > 0))
  
  has_spend <- !is.null(spend) && 
               spend != "N/A" && 
               (is.list(spend) || (is.character(spend) && nchar(trimws(spend)) > 0))
  
  return(has_impressions || has_spend)
}

# Function to create job ad record
create_job_ad <- function(ad, search_term, country, ad_type) {
  impressions <- ad$impressions %||% "N/A"
  spend <- ad$spend %||% "N/A"
  
  has_metrics <- has_ad_metrics(impressions, spend)
  gender_info <- process_gender_info(ad)
  
  job_ad <- list(
    search_term = search_term,
    country = country,
    ad_type = ad_type,
    id = ad$id %||% "",
    company = ad$page_name %||% "",
    creation_date = ad$ad_creation_time %||% "",
    delivery_start = ad$ad_delivery_start_time %||% "",
    delivery_stop = ad$ad_delivery_stop_time %||% "",
    job_titles = ad$ad_creative_link_titles %||% list(),
    descriptions = ad$ad_creative_link_descriptions %||% list(),
    captions = ad$ad_creative_link_captions %||% list(),
    ad_creative_bodies = ad$ad_creative_bodies %||% list(),
    spend = spend,
    impressions = impressions,
    publisher_platforms = ad$publisher_platforms %||% list(),
    estimated_audience_size = ad$estimated_audience_size %||% "N/A",
    languages = ad$languages %||% list(),
    ad_snapshot_url = ad$ad_snapshot_url %||% "",
    has_metrics = has_metrics,
    gender_info = gender_info
  )
  
  return(job_ad)
}

# Main function to extract job ads
extract_job_ads <- function() {
  # Regular searches (non-India)
  search_configurations <- list(
    list(terms = "analyst", countries = "US", limit = 1000, ad_type = "ALL"),
    list(terms = "analyst", countries = "GB", limit = 1000, ad_type = "ALL"),
    list(terms = "analyst", countries = "US", limit = 1000, ad_type = "POLITICAL_AND_ISSUE_ADS"),
    list(terms = "analyst", countries = "CA", limit = 500, ad_type = "ALL")
  )
  
  # India-specific searches
  india_search_configurations <- list(
    list(terms = "analyst", countries = "IN", limit = 1000, ad_type = "ALL"),
    list(terms = "analyst", countries = "IN", limit = 1000, ad_type = "POLITICAL_AND_ISSUE_ADS")
  )
  
  all_job_ads <- list()
  india_job_ads <- list()
  
  # Process regular searches
  cat("=== Processing Global Searches ===\n")
  for (config in search_configurations) {
    search_term <- config$terms
    country <- config$countries
    cat(sprintf("Searching for: '%s' in %s (type: %s)\n", search_term, country, config$ad_type))
    
    params <- list(
      access_token = ACCESS_TOKEN,
      ad_type = config$ad_type,
      ad_reached_countries = country,
      search_terms = search_term,
      limit = config$limit,
      fields = "id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,page_name,ad_creative_link_titles,ad_creative_link_descriptions,ad_creative_link_captions,spend,impressions,publisher_platforms,estimated_audience_size,languages,ad_snapshot_url,ad_creative_bodies,demographic_distribution,target_gender,target_ages,target_locations,age_country_gender_reach_breakdown"
    )
    
    result <- make_request(ADS_LIBRARY_BASE, params)
    
    if (!is.null(result) && "data" %in% names(result)) {
      ads <- result$data
      cat(sprintf("Found %d ads for '%s' in %s (type: %s)\n", length(ads), search_term, country, config$ad_type))
      
      for (ad in ads) {
        job_ad <- create_job_ad(ad, search_term, country, config$ad_type)
        all_job_ads <- append(all_job_ads, list(job_ad))
      }
    }
  }
  
  # Process India searches
  cat("\n=== Processing India Searches ===\n")
  for (config in india_search_configurations) {
    search_term <- config$terms
    country <- config$countries
    cat(sprintf("Searching for: '%s' in %s (type: %s) - INDIA SPECIFIC\n", search_term, country, config$ad_type))
    
    params <- list(
      access_token = ACCESS_TOKEN,
      ad_type = config$ad_type,
      ad_reached_countries = country,
      search_terms = search_term,
      limit = config$limit,
      fields = "id,ad_creation_time,ad_delivery_start_time,ad_delivery_stop_time,page_name,ad_creative_link_titles,ad_creative_link_descriptions,ad_creative_link_captions,spend,impressions,publisher_platforms,estimated_audience_size,languages,ad_snapshot_url,ad_creative_bodies,demographic_distribution,target_gender,target_ages,target_locations,age_country_gender_reach_breakdown"
    )
    
    result <- make_request(ADS_LIBRARY_BASE, params)
    
    if (!is.null(result) && "data" %in% names(result)) {
      ads <- result$data
      cat(sprintf("Found %d ads for '%s' in %s (type: %s) - INDIA SPECIFIC\n", length(ads), search_term, country, config$ad_type))
      
      for (ad in ads) {
        job_ad <- create_job_ad(ad, search_term, country, config$ad_type)
        india_job_ads <- append(india_job_ads, list(job_ad))
      }
    }
  }
  
  # Remove duplicates from regular ads
  if (length(all_job_ads) > 0) {
    all_ids <- sapply(all_job_ads, function(x) x$id)
    unique_indices <- !duplicated(all_ids)
    all_job_ads <- all_job_ads[unique_indices]
    
    # Sort by has_metrics
    all_job_ads <- all_job_ads[order(sapply(all_job_ads, function(x) x$has_metrics), decreasing = TRUE)]
  }
  
  # Remove duplicates from India ads
  if (length(india_job_ads) > 0) {
    india_ids <- sapply(india_job_ads, function(x) x$id)
    unique_india_indices <- !duplicated(india_ids)
    india_job_ads <- india_job_ads[unique_india_indices]
    
    # Sort by has_metrics
    india_job_ads <- india_job_ads[order(sapply(india_job_ads, function(x) x$has_metrics), decreasing = TRUE)]
  }
  
  return(list(global_ads = all_job_ads, india_ads = india_job_ads))
}

# Function to display job ads summary
display_job_ads <- function(job_ads) {
  if (length(job_ads) == 0) {
    return()
  }
  
  cat(sprintf("Total ads: %d\n", length(job_ads)))
  cat(sprintf("Ads with metrics: %d\n", sum(sapply(job_ads, function(x) x$has_metrics))))
  
  # Display first few companies
  companies <- unique(sapply(job_ads, function(x) x$company))
  cat("Sample companies:", paste(head(companies, 5), collapse = ", "), "\n")
}

# Function to convert list to string for CSV
list_to_string <- function(lst) {
  if (is.null(lst) || length(lst) == 0) {
    return("")
  }
  return(paste(unlist(lst), collapse = "; "))
}

# Function to extract bounds from range objects
extract_bounds <- function(value, bound_type) {
  if (is.list(value) && bound_type %in% names(value)) {
    return(as.character(value[[bound_type]]))
  }
  return("N/A")
}

# Function to safely convert to JSON string
safe_json_convert <- function(data) {
  if (is.null(data) || length(data) == 0) {
    return("N/A")
  }
  
  tryCatch({
    if (is.list(data)) {
      return(toJSON(data, auto_unbox = TRUE))
    } else {
      return(as.character(data))
    }
  }, error = function(e) {
    return("N/A")
  })
}

# Function to save job ads to CSV
save_job_ads <- function(job_ads, region = "global") {
  if (length(job_ads) == 0) {
    return(NULL)
  }
  
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  
  if (region == "india") {
    csv_filename <- paste0("analyst_ads_india_", timestamp, ".csv")
  } else {
    csv_filename <- paste0("analyst_ads_", timestamp, ".csv")
  }
  
  tryCatch({
    # Create data frame
    df_list <- list()
    
    for (i in seq_along(job_ads)) {
      ad <- job_ads[[i]]
      
      # Extract spend bounds
      spend_lower <- extract_bounds(ad$spend, "lower_bound")
      spend_upper <- extract_bounds(ad$spend, "upper_bound")
      
      # Extract impressions bounds
      impressions_lower <- extract_bounds(ad$impressions, "lower_bound")
      impressions_upper <- extract_bounds(ad$impressions, "upper_bound")
      
      # Extract audience size bounds
      audience_lower <- extract_bounds(ad$estimated_audience_size, "lower_bound")
      audience_upper <- extract_bounds(ad$estimated_audience_size, "upper_bound")
      
      # Extract gender information safely
      gender_info <- ad$gender_info
      demographic_distribution <- safe_json_convert(gender_info$demographic_distribution)
      target_gender <- if (!is.null(gender_info$target_gender)) as.character(gender_info$target_gender) else "N/A"
      target_ages <- safe_json_convert(gender_info$target_ages)
      age_country_gender_breakdown <- safe_json_convert(gender_info$age_country_gender_reach_breakdown)
      
      # Truncate ad content
      ad_content <- list_to_string(ad$ad_creative_bodies)
      if (nchar(ad_content) > 500) {
        ad_content <- substr(ad_content, 1, 500)
      }
      
      df_list[[i]] <- data.frame(
        ad_id = as.character(ad$id),
        company = as.character(ad$company),
        search_term = as.character(ad$search_term),
        country = as.character(ad$country),
        ad_type = as.character(ad$ad_type),
        creation_date = as.character(ad$creation_date),
        delivery_start = as.character(ad$delivery_start),
        delivery_stop = as.character(ad$delivery_stop),
        spend_lower = as.character(spend_lower),
        spend_upper = as.character(spend_upper),
        impressions_lower = as.character(impressions_lower),
        impressions_upper = as.character(impressions_upper),
        audience_size_lower = as.character(audience_lower),
        audience_size_upper = as.character(audience_upper),
        job_titles = as.character(list_to_string(ad$job_titles)),
        descriptions = as.character(list_to_string(ad$descriptions)),
        ad_content = as.character(ad_content),
        platforms = as.character(list_to_string(ad$publisher_platforms)),
        languages = as.character(list_to_string(ad$languages)),
        has_metrics = as.logical(ad$has_metrics),
        ad_url = as.character(ad$ad_snapshot_url),
        demographic_distribution = as.character(demographic_distribution),
        target_gender = as.character(target_gender),
        target_ages = as.character(target_ages),
        age_country_gender_breakdown = as.character(age_country_gender_breakdown),
        stringsAsFactors = FALSE
      )
    }
    
    # Combine all rows
    final_df <- do.call(rbind, df_list)
    
    # Write to CSV
    write_csv(final_df, csv_filename)
    return(csv_filename)
    
  }, error = function(e) {
    cat("Error saving file:", e$message, "\n")
    return(NULL)
  })
}

# Main function
main <- function() {
  results <- extract_job_ads()
  job_ads <- results$global_ads
  india_job_ads <- results$india_ads
  
  cat("\n=== SUMMARY ===\n")
  cat(sprintf("Global ads found: %d\n", length(job_ads)))
  cat(sprintf("India ads found: %d\n", length(india_job_ads)))
  
  # Save global ads
  if (length(job_ads) > 0) {
    cat("\nProcessing global ads...\n")
    display_job_ads(job_ads)
    filename <- save_job_ads(job_ads, "global")
    if (!is.null(filename)) {
      cat(sprintf("Global ads saved to: %s\n", filename))
    }
  }
  
  # Save India ads
  if (length(india_job_ads) > 0) {
    cat("\nProcessing India ads...\n")
    display_job_ads(india_job_ads)
    india_filename <- save_job_ads(india_job_ads, "india")
    if (!is.null(india_filename)) {
      cat(sprintf("India ads saved to: %s\n", india_filename))
    }
  }
  
  if (length(job_ads) == 0 && length(india_job_ads) == 0) {
    cat("No ads found in any region.\n")
  }
}

# Run the main function
if (!interactive()) {
  main()
} 