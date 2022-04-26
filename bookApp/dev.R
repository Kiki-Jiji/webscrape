
df = readr::read_csv("book_data.csv")

df_star = df %>%
  mutate(star_num = as.numeric(
    stringr::str_extract(df$star_rating_txt, "[0-9].[0-9]")
  )
  )

as.numeric(
stringr::str_remove(stringr::str_remove(df$price_txt, "[£$]"), "[.]")
)




df_star %>%
  mutate(price_txt = as.numeric(
    stringr::str_remove(stringr::str_remove(price_txt, "[£$]"), "[.]")
  ), star_num = ifelse(is.na(star_num), "None", star_num)) %>%
  group_by(star_num) %>%
  summarise(avg_price_pounds = mean(price_txt, na.rm=TRUE) / 100) %>%
ggplot(aes(star_num, avg_price_pounds, group = 1)) + geom_bar(stat="identity") + theme_bw()




plotly::ggplotly(
  ggplot(df_star, aes(star_num)) + geom_histogram() + theme_bw()
)
