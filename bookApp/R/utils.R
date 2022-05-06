
#' Get data from s3
#'
#' @return data.frame
#' @export
load_data <- function() {
  
  BUCKET_NAME = Sys.getenv("BUCKET_NAME")
  if(BUCKET_NAME == "") stop("Missing BUCKET_NAME envar")
  
  KEY = Sys.getenv("KEY")
  if(KEY == "") stop("Missing KEY envar")
  
  SECRET = Sys.getenv("SECRET")
  if(SECRET == "") stop("Missing SECRET envar")
  
  
  bucket = aws.s3::get_bucket(bucket = BUCKET_NAME,
                              key = KEY,
                              secret = SECRET, 
                              region = "eu-west-2")
  
  all_data = lapply(1:length(bucket), function(x) {
    
    load_day_df(bucket[[x]]$Key, bucket_name = BUCKET_NAME, key = KEY, secret = SECRET)
    
  })
  
  final_data = do.call(rbind, all_data)
  
  return(final_data)
  
}



load_day_df <- function(s3_object_name, bucket_name, key, secret) {
  
  
  raw_data = jsonlite::fromJSON(rawToChar(
    aws.s3::get_object(object = s3_object_name, bucket = bucket_name, key = key, secret = secret, 
                       region = "eu-west-2")
  ))
  
  
  df_data = convert_list_df(raw_data)
  
  if(!all(names(df_data) %in% c("book_rank_scrape", "book_title_txt", "author_txt", 
                                "star_rating_txt", "book_type_txt",
                                "price_txt", "category", "date" ))) stop("column names wrong")
  
  return(df_data)
  
}





convert_list_df <- function(s3_data) {
  
  list_rows = lapply(names(s3_data$data), function(x) {
    
    df = do.call(rbind, s3_data$data[[x]])
    df = data.frame(df)
    df['category'] = x
    
    
    return(df)
  })
  
  
  
  day_data = data.frame(do.call(rbind, list_rows))
  
  day_data['date'] = s3_data$date
  
  return(day_data)
}
