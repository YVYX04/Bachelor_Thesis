<details>
<summary>Metadata</summary>

```yaml
title: "In Search of Attention"
authors: ["Da, Zhi", "Engelberg, Joseph", "Gao, Pengjie"]
year: 2011
venue: "The Journal of Finance"
topic_tags: ["attention", "event-study", "liquidity", "Google", "SVI", "Russell 3000"]
my_relevance: "High"
status: "processing"
doi_or_url: "https://doi.org/10.1111/j.1540-6261.2011.01679.x"
citation_key: "DaEtal2011"
```
</details>

# In Search of Attention

**Da, Z., Engelberg J., & Gao, P. (2011).**

Summarized by Yvan Richard

*⚠️ This is not an exhaustive summary and I filter based on relevance for my thesis.*

## 1. Key Insights

This paper is directly relevant to my thesis because Da et al. (2011) leverage the Search Volume Index (SVI) from Google Trends to proxy for investor attention in a timely fashion. Furthermore, the researchers insist on the fact that the SVI is probably an attention proxy particularly revealing of the retail investors attention state. The main finding of this paper is the following:

> "An increase in SVI predicts higher stock prices in the next 2 weeks and an eventual price reversal within the year" (Da et al., 2011, p. 1461).

It is also pertinent to note that the SVI is a "direct measure" of investors attention since we know for sure that someone who is searching for a stock on Google is actively paying attention to it. This is in oppostion to the *news proxy* of [Barber & Odean (2008)](/BarberOdean_2008_All_That_Glitters.md), where the presence of a firm in a given journal does not necessarily mean that investors are attentive to it.


## 2. Research Question & Hypothesis

This paper tests multiple hypothesis but the two relevant to my scope of research are the following.

1. An increase at time $t$ in the SVI for a given stock $i$ is related to a positive price pressure for that given stock at time $t + k$ for $t, k \in \mathbb{R}$.

2. Ultimately, if a stock particularly captured the attention of the investors at time $t$ and the investors indeed overreacted (this behavioral bias is well documented in the literature), we observe a reversal at a later time $t+ k + u$, where $u \in \mathbb{R}$.


## 3. Data

### 3.1. Google Trends

During the period of observation (2004 - 2008), the SVI were collected for each individual stock $i$ in the Russell 3000 index with a weekly granularity.

It is worth mentionning that the authors specifically measure when the **stock ticker** is searched and not only the company name (e.g. a customer might search Amazon for ordering a product). They are also careful with tickers like "ALL", "BABY", or the ones which could have a dual meaning and become noise rather than actual proxies for attention.

### 3.2. Russell 3000 Stocks

The Russell 3000 is a U.S. stock market index (from FTSE Russell) designed to represent roughly the 3,000 largest publicly traded U.S. companies, selected and weighted by market capitalization. Da et al. (2011) collected the daily stock prices (close) over the period 2004 - 2008 and decided to mitigate **survivorship bias** by examining all 3,606 stocks ever included in the index during the
sampling period. Furthermore, to "avoid market microstructure-related concerns, [they] exclude stock-week observations for which the market price is less than three
dollars when testing the attention-induced price pressure hypothesis" (Da et al., 2011, p. 1466).


## 4. Empirical Design

### 4.1. Correlations

The authors first compare weekly log(SVI) to common attention/sentiment proxies: extreme (abnormal) returns, abnormal turnover, and Dow Jones/WSJ news coverage; quite in the spirit of [Barber & Odean (2008)](/BarberOdean_2008_All_That_Glitters.md). The key point is that correlations are positive on average but small in magnitude: SVI is related to these proxies yet clearly not the same object. They also show that SVI has little correlation with news-based negativity measures.  ￼

### 4.2. Lead–lag Dynamics (VAR)

They run stock-level weekly VARs (⚠️ I still need to understand this!) including log(SVI), log(turnover), absolute abnormal return, and log(1+Chunky News), with constant + time trend, and use block bootstrap p-values. Result: lagged log(SVI) positively predicts (leads) the other attention proxies. Interpretation: (i) investors may search before they trade, so SVI can lead turnover/returns; (ii) investors can also search ahead of scheduled events (e.g., earnings), so SVI can lead news measures.  ￼

### 4.3. Constructing the Main Attention Shock: ASVI

Their main "attention shock" variable is Abnormal SVI ($ASVI$):

$$
ASVI_{i,t} = \log(SVI_{i,t}) − \log(median(SVI_{i,t−1} … SVI_{i,t−8})).
$$

Using an 8-week rolling median (rather than mean) makes the baseline "normal attention" robust to outliers and removes slow-moving trends/seasonality, improving cross-sectional comparability. In panel regressions where $ASVI$ is explained by other attention proxies + fixed effects, the $R^2$ is low (only a small fraction of $ASVI$ is "explained"), reinforcing the claim that $ASVI$ contains incremental information relative to standard proxies.


## 5. Key Definitions

+ Dash-5 (SEC Rule 11Ac1-5 / Reg 605): monthly execution-quality reports for "covered orders" (mostly retail orders; excludes special-handling and large orders), used to proxy retail order flow. These reports were published by U.S. trading venues.


## 6. Main Results

### 6.1. Whose Attention Does SVI Capture?

Because post-decimalization trade-size heuristics are unreliable for identifying retail trades (this means that after the decimalization of the trading transaction, many funds segment their transaction in many different chunks for several reasons), the paper uses Dash-5 covered orders as a cleaner retail proxy. **Monthly changes in SVI strongly predict monthly changes in retail orders and retail turnover** even after controlling for returns, absolute returns, news, advertising, and other characteristics.  ￼

### 6.2. Attention-induced Price Pressure in Russell 3000 Stocks

The main findings are:

1.	Short-run continuation: ASVI predicts positive abnormal returns over the next 1–2 weeks. In the paper’s calibration, a one-standard-deviation increase in ASVI is associated with economically meaningful outperformance in week 1 and still positive in week 2.  ￼

2.	Dissipation and reversal: predictive power fades after week 2; by weeks 3–4 the effect turns toward zero/negative (reversal dynamics).  ￼

3.	Long-run reversal: looking at weeks 5–52 (skipping the first month), the ASVI coefficient is negative and similar in magnitude to the initial short-run price pressure—suggesting near-complete reversal within a year (statistical significance is weaker overall due to limited independent long-horizon observations; stronger among smaller stocks per appendix discussion).  ￼

A key identification point they stress: ASVI is the attention measure that predicts both (i) short-run run-up and (ii) long-run reversal, which is more consistent with temporary price pressure than with "ASVI reveals fundamentals". ￼

### 6.3. Cross-sectional Strength

The attention-induced price pressure is stronger in stocks with greater retail presence (higher Percent Dash-5 Volume), and the interaction terms are used to show that ASVI has more return impact when the stock is more retail-traded. This matches the mechanism: attention shocks matter more where marginal buying pressure comes from retail investors.