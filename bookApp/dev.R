
#df = readr::read_csv("book_data.csv")

df = load_data()
df = tibble::tibble(df)


library(wordcloud)
library(tm)

word_counts = termFreq(df$book_title_txt, control = list(
  removePunctuation = TRUE,
  removeNumbers = TRUE,
  stopwords = TRUE,
  stemming = TRUE)
)

word_counts = data.frame(word_counts)
word_counts$word = row.names(word_counts)


hat = word_counts %>%
  rename(freq = word_counts) %>%
  mutate(freq = as.numeric(freq)) %>%
  select(word, freq)


shapes = c("circle", "star", "cardioid", "diamond", "triangle-forward", "triangle", "pentagon")

library(wordcloud2)

wordcloud2(data=hat, minSize = 1, shape = shapes[4])






figPath = system.file("examples/t.png",package = "wordcloud2")

wordcloud2(hat, figPath = "book.png")






key = "AKIASFBKEY236QV464EC"
secret = "rgr/9BL3F99Z+UaGx31O75JvTeBPKAqCmf4vjkPp"
region = "eu-west-2"


bucket = aws.s3::get_bucket(bucket = bucket_name,
                   key = key,
                   secret = secret, 
                   region = region)




load_data()
