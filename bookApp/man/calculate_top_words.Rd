% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/utils.R
\name{calculate_top_words}
\alias{calculate_top_words}
\title{Get words usage}
\usage{
calculate_top_words(df, select_category = "all")
}
\arguments{
\item{df}{The word data}

\item{select_category}{A category to filter to, if "all" then use all categoryies}
}
\value{
data.frame
}
\description{
Calculates the number of time words are used
}
