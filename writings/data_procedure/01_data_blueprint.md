# Bachelor Thesis

Yvan Richard
University of St. Gallen, Spring Term 2026

## Data Blueprint

### Foreword

In this file, I lay down the foundations for the organization of
my data blueprint. I intend to explicit what are the data sets I
am using, what are the cleaning procedures I use, where those ideas
come from, and what the final data set prodcut should look like.

### 1. Robintrack Data

This data set is the bottleneck of my study. In my opinion,
I should handle this data set first because it will determine how
I structure the granularity and align/merge the other data sets.

The structure of my data cleaning process for this data set will
be closely aligned with Barber et al. (2022). I note down the important
elements outline in their study.

1. "Our main results include all Robintrack securities."
2. "We merge the Robintrack data to the Center of Research in Security Prices (CRSP) [...] by using the ticker on Robintrack.
3. $users\_close$: measures the total number of users in a stock prior to the close of trading (4 pm ET) but after 2 pm on the same day."
4. $users\_change$ measure the daily change in $users\_close$.
5. $users\_ratio = users_close(t)/users_close(t - 1)$
6. $users\_last$ is the last number of users oberved in the day.

At this point, I already have enough information to construct the primary variables of
my theis (regarding the Robinhood app). I have to establish a daily granularity of $users\_close$ for all the tickers present in the Robinhood data set. Then, I will be able
to verify the summary statistis of my data set against the one of Barber et al. (2022).
Once this is done, I proceed with building the herding events.



### References

+ Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention‐induced trading and returns: Evidence from Robinhood users. *The Journal of Finance*, 77(6), 3141-3190.


