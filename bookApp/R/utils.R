
#' Get data from s3
#'
#' @return data.frame
#' @export
load_data <- function() {
  
  if (Sys.getenv("DEV") == "TRUE") {
    # load sample data to avoid aws
    df = readr::read_csv("books_data.csv")
    message("Loading sample data")
    return(df)
  }
  
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
  
  raw_data = aws.s3::get_object(object = "books.csv", 
                     bucket = BUCKET_NAME, 
                     key = KEY, 
                     secret = SECRET, 
                     region = "eu-west-2")

  data = readr::read_csv(rawToChar(raw_data))
  
  return(data)
}



#' Cleans the raw data
#'
#' @param df 
#'
#' @return
#' @export
#'
#' @examples
clean_data <- function(df) {
  
  df$date = as.Date(df$date, format = "%d_%m_%Y")
  df$book_rank_scrape = as.numeric(gsub("#", "", df$book_rank_scrape))
  df$star_rating_txt = as.numeric(stringr::str_extract(df$star_rating_txt, "[0-9].[0-9]"))
  df$price_txt = as.numeric(gsub("[$|£]", "", df$price_txt))
  
  df_clean = df %>%
    rename(book_rank = book_rank_scrape,
           book_title = book_title_txt,
           author = author_txt,
           star_rating = star_rating_txt,
           book_type = book_type_txt,
           price = price_txt,
           category = catagory) %>%
    arrange(desc(date))
  
  
  return(df_clean)
}


#' Get words usage
#' 
#' Calculates the number of time words are used
#'
#' @param df The word data
#' @param select_category A category to filter to, if "all" then use all categoryies
#'
#' @return data.frame
#' @export
calculate_top_words <- function(df, select_category = "all") {
  
  if(select_category == "all") {
    words_df = df[c("book_title")]
  } else {
    words_df = df %>%
      filter(category == select_category) %>%
      select(book_title)

  }
  
  words_df$book_title_trimmed =  stringr::str_extract(words_df$book_title, "[^:]+")
  
  
  word_counts = tm::termFreq(words_df$book_title_trimmed, control = list(
    removePunctuation = TRUE,
    removeNumbers = TRUE,
    stopwords = TRUE,
    stemming = TRUE)
  )
  
  word_counts = data.frame(word_counts)
  word_counts$word = row.names(word_counts)
  
  
  top_words_df = word_counts %>%
    rename(freq = word_counts) %>%
    mutate(freq = as.numeric(freq)) %>%
    select(word, freq) %>%
    arrange(desc(freq))
  
    return(top_words_df)
  
}




#' Title
#'
#' @param df 
#' @param select_category 1 or more catagories as a vector
#' @param number 
#'
#' @return
#' @export
#'
#' @examples
top_authors = function(df, select_category = "all", number = 10, min_date, max_date ) {
  
  df_trimmed <- df %>%
    filter(date >= min_date, date <= max_date)
  
  if(any(select_category %in% "all")) {
    ta_df = df_trimmed[c("author", "book_title")]
  } else {
    ta_df = df_trimmed %>%
      filter(category %in% select_category) %>%
      select(author, book_title)
  }
  
  plot_data = ta_df %>%
    group_by(author, book_title) %>%
    summarise(count = n()) %>%
    arrange(desc(count)) %>%
    count(author) %>%
    arrange(desc(n)) %>%
    ungroup()
  
  
  plot_data = plot_data %>%
    slice_head(n = number) 
  
  
  return(plot_data)
  
}
