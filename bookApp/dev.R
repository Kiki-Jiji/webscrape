
library(bookApp)
library(dplyr)
library(ggplot2)
library(plotly)

# each dollar is worth 81p
dollar_pound_rate =  0.81
Sys.setenv("DEV" = "TRUE")
df = load_data()
df = clean_data(df)
df = df %>%
  filter(date != "2022-05-07")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# popularity of authors

plot_data = df %>%
  group_by(author, book_title) %>%
  summarise(count = n()) %>%
  arrange(desc(count)) %>%
  count(author) %>%
  arrange(desc(n)) %>% 
  ungroup()



plot_data = plot_data %>%
  slice_head(n = 10) 



xform <- list(categoryorder = "array",
              categoryarray = plot_data$author)

plot_ly(
  x = plot_data$author,
  y = plot_data$n,
  name = "SF Zoo",
  type = "bar"
) %>% 
layout(xaxis = xform)


a %>%
  filter(n > 2) %>%
  ggplot() +
  aes(x = author, weight = n) +
  geom_bar(fill = "#112446") +
  coord_flip() +
  theme_minimal()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

cats = unique(df$category)

cat = cats[2]
size = 10

calculate_top_words(df) |>
  slice_head(n = 20) |>
  wordcloud2::wordcloud2(size = 0.6)






#############################################################
# words




words_df = df[c("book_title")]



txt = "The Dream Weavers: A spellbinding and gripping new historical fiction novel from the Sunday Times bestse"


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



