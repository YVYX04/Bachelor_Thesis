<details>
<summary>Metadata</summary>

```yaml
title: "All That Glitters: The Effect of Attention and News on the Buying Behavior of Individual and Institutional Investors"
authors: ["Barber, Brad M.", "Odean, Terrance"]
year: 2008
venue: "The Review of Financial Studies"
topic_tags: ["attention", "event-study", "liquidity"]
my_relevance: "High"
status: "read"
doi_or_url: "https://doi.org/10.1093/rfs/hhm079"
citation_key: "BarberOdean2008"
```
</details>

# All That Glitters: The Effect of Attention and News on the Buying Behavior of Individual and Institutional Investors

**Barber, B. M. & Odean, T. (2008).**

Summarized by Yvan Richard

*⚠️ This is not an exhaustive summary and I filter based on relevance for my thesis.*

## 1. Key Insights

The authors point out that retail investors, "individual investors", have limited attention because they lack the resources and time needed for research all the possible investable assets (institutional investors face the same issue, but to a lesser extent). "Thus, preferences determine choices after attention has determined the choice set" (Barber & Odean, 2008, p. 785).

Once this element is identified, the authors precise that this problem is faced by retail investors when making a *buying decision* (since retail investors face short-selling constraints). Indeed, individual investors search among thousands of stocks but only sell the ones they already hold. Strong evidence is proposed by the authors to show that "individual investors are more likely to buy attention-grabbing stocks than to sell them" (Barber & Odean, 2008, p. 786).

Finally, the researchers "confirm the hypothesis that individual investors are net buyers of attention-grabbing stocks, e.g., stocks in the news, stocks experiencing high abnormal trading volume, and stocks with extreme one-day returns" (Barber & Odean, 2008, p. 785).


## 2. Research Question & Hypothesis

In this paper, two main hypothesis are tested:

1. The buying behavior of individual investors is more heavily influenced by attention than is their selling behavior.

2. The buying behavior of individual investors is more heavily influenced by attention than is the buying behavior of professional investors.

## 3. Data

In this study, Barber & Odean (2008) leverage four main sources of data:

1. a large discount brokerage
2. a small discount brokerage
3. a large full-service brokerage
4. data from the Plexus group (tracking the trading of professional money managers)

The core focus is investors’ common stock purchases and sales.
They exclude from the current analysis investments in mutual funds (both open-
and closed-end), American depository receipts (ADRs), warrants, and options.

The financial data for the stocks come from the CRSP daily returns file.

## 4. Empirical Design

### 4.1. Attention Proxies

Since the researchers cannot survey every institutional and individual investor on which stock(s) caught their attention at a given time, they use three proxies for which we can establish time series:

1. A stock's abnormal daily trading volume.
2. The stock's (previous) one-day return.
3. Whether the firm appeared in the news that day.

### 4.2. Sort Methodology

#### Volume Sort

The daily trading volume of a stock is an attention proxy.
The abnormal trading volume for stock $i$ on day $t$ is defined as:

$$
AV_{i, t} = \frac{V_{i,t}}{\overline{V}_{i, t}}
$$

where $V_{i, t}$ is the dollar volume for stock $i$ traded on day $t$ as reported in the Center
for Research in Security Prices (CRSP) daily stock return files. Furthermore, $\overline{V}_{i, t}$ is defined by the average trading volume over the past year (252 trading days).

$$
\overline{V}_{i, t} = \sum_{d = t - 252}^{t - 1} \frac{V_{i, d}}{252}
$$

Each day, they sort stocks into deciles on the basis of that day’s abnormal trading volume. Based on these sorts, they construct a buy-sell imbalance (BSI) measure (Barber & Odean, 2008, p. 794).

#### Return Sort

The authors explain that extreme daily returns likely attract investors' attention. Hence, the authors aim to include these in their design.

For the day $t-1$, they sort all stocks for which returns are reported in the CRSP daily returns file into 10 deciles based on one day return. Once this is done (further split of upper and lower decile into vingtiles), they compute the BSI.

#### News Sort

Their news dataset is the daily news feed from Dow Jones
News Service for the period 1994 to 1999. The Dow Jones news feed includes the ticker symbols for each firm mentioned in each article. They partition stocks
into those for which there is a news story that day and those with no news. Hence, they generate a binary indicator.

## 5. Key Definitions

+ **Attention-grabbing stock**: A stock that captures or attracts the attention of investors in an "abnormal way" at a given time $t$.

## 6. Main Results

In this section, I compile the findings that are the most interesting for my personal research.

+ The researchers note that they compute BSI both with respect to value (significance of the moves but overweight the behavior of institutional or wealthy investors) and number of transactions.

+ "Investors at the large discount brokerage display the greatest amount of attention-driven buying. When imbalances are calculated by number of trades, the buy-sell imbalance is −18.15% for stocks in the lowest volume decile. For stocks in the highest volume vingtile, the buy-sell imbalance is +29.5% more" (Barber & Odean, 2008, p. 798).

+ "Investors at the large discount brokerage display the greatest amount of attention-driven buying for these returns sorts. When calculated by number of trades, the buy-sell imbalance of investors at the large discount brokerage is 29.4% for the vingtile of stocks with the worst return performance on the previous day" (Barber & Odean, 2008, p. 800).

+ "It appears from this analysis and from our univariate tests that abnormal trading volume is our single best indicator of attention. Returns come in second. Our simple news metric—whether a stock was or was not mentioned in that day’s news—is our least informative indicator of attention" (Barber & Odean, 2008, p. 803).

