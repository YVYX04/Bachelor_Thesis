<details>
<summary>Metadata</summary>

```yaml
title: "Attention-Induced Trading and Returns: Evidence from Robinhood Users"
authors: ["Barber, Brad", "Huang, Xing", "Odean, Terrance", "Schwarz, Christopher"]
year: 2022
venue: "The Journal of Finance"
topic_tags: ["attention", "event-study", "liquidity", "Robinhood"]
my_relevance: "High"
status: "processing"
doi_or_url: " https://doi.org/10.1111/jofi.13183"
citation_key: "BarberETall2022"
```
</details>

# Attention-Induced Trading and Returns: Evidence from Robinhood Users

**Barber, M. B., Huang X., Odean, T., & Schwarz, C. (2022).**

Summarized by Yvan Richard

*⚠️ This is not an exhaustive summary and I filter based on relevance for my thesis.*

## 1. Key Insights

### 1.1. The Key Finding

In this paper, Barber et al. (2022) uses a relatively new data set in the literature that comes from the online retail trading app *Robinhood*. Specifically, the authors focus on individual investors and they convincingly demonstrate that, "consistent with models of attention-induced trading, intense buying by Robinhood users forecasts negative returns".
They conclude that "average 20-day abnormal returns are $−4.7\%$ for the top stocks purchased each day".

### 1.2. Between Democratizing Trade & Aggressive Marketing

Importantly, the authors recognize that the technological developments of these past decades contributed to democratizing market access with online app that charge very small fees. On the other hand, they warn about the fact that these online apps "gamify" the experience of trading and use "aggressive tactics to attract inexperienced investors". They further proceed with demonstrating that Robinhood's investors' lack of experience is demonstrated by the extremely high number of transactions they engage in.

### 1.3. Sensitivity to Information Display

Furthermore, Barbet et al. (2022) notice that the platform Robinhood make certain features particularly salient to encourage investors to trade on their "intuition"; thus appealing to their "System 1" (Kahneman, 2011). Some of the features, such as the "top-movers" chart incentivize users to trade extreme gainers and losers and this is in fact what they tend to do. "This evidence indicates that the display of information affects investors' trading.

### 1.4. More Influence in Small-cap Stocks

Barber et al. (2022, p. 3146) also report that they find "negative returns following Robinhood herding events for stocks with market cap under $1 billion, but not for stocks with market cap over $1 billion".

## 2. Research Questions & Hypothesis 

1. "Does the choice of information display affect how retail investors trade?"
2. "Does herding episodes from retail investors help predict subsequent abnormal returns?"

## 3. Data

### 3.1. Robintrack Data

The primary data set for the authors' analysis is publicly available on the Robintrack [website](https://robintrack.net). The data sample runs from May 2, 2018 until August 13, 2020. "The Robintrack data set contains cross-sectional snapshots of user counts for individual securities (e.g., $645,535$ Robinhood users held Apple stock at 3:46 pm ET on August 3, 2020)". The authors merge these data with data from CRSP.

### 3.2. Herding Events

> "While we find that user changes are generally small, a number of extreme user change events are in our sample. These extreme events likely occur because Robinhood users are new to markets and more willing to speculate. These extreme events are also likely a good proxy for the behavior of investors who are unduly influenced by attention-grabbing events." (Barber et al., 2022, p. 3150).

In the following pages, the authors define precisely how they identifiy a *herding event*.

## 4. Empirical Design: Attention and Stock Selection

The authors have many goals:

1. Document the fact that Robinhood users show excessively concentrated trading activities.
2. Show that attention measures strongly predict Robinhood herding episodes and use the model to forecast the probability of herding episodes for individual stocks.
3. Convincingly show that Robinhood users are particularly prone to trading in attention-grabbing stocks by exploiting Robinhood trading outages and document sharper drops in retail volume for stocks with a high probability of a herding episode during these outages.

### 4.1. The Concentration of Buying versus Selling

The authors repeat that attention induced trading should be particularly marked when retail investors face *buying decisions* because this is where their attention is really challenged, i.e. choosing among thousands of stocks. On the other hand, when they face a *selling decision*, they only have so much stocks to consider ($3$ on average for users of the Robinhood platform).

The authors indeed find that the pattern observed supports an "attention" story: retail investors disproportionately direct buying into a small set of attention-grabbing stocks (top names), while selling is more dispersed (people sell a wider range of holdings for varied reasons like rebalancing, liquidity needs, tax motives, etc.).

![](/assets/images/concentration_of_buying.png)

### 4.2. Attention Proxies and Robinhood Herding Events

> "If attention is guiding the trading decisions of Robinhood investors, we expect proxies for investor attention to be strong predictors of Robinhood herding episodes" (Barber et al., 2022, p. 3155).

In this section, the authors study the correlation study the link between the data from Robintrack and a set of attention proxies. These attention proxies are:

- extreme absolute lagged returns
- lagged abnormal volume
- lagged user change (Robintrack)
- lagged level of users (Robintrack)
- lagged abnormal Google search volume (Da et al., 2011)
- lagged abnormal news coverage
- lagged earnings annoucement

Taken together, the results show that the extreme herding episodes of Robinhood investors are persistent and can be predicted by various attention measures. 

I do not cover the "outage" and "top-movers" sections here but they also give important confirmations regarding the expected behavior of retail investors.


## 5. Main Results

In my opinion, of the most interesting figure relative to the discovery about abnormal returns behavior around herding events is the following (Barber et al., 2022, p. 3171).

![](/assets/images/returns_herding_events_Robinhood.png)

> "Prior to the herding event, stocks have abnormal returns near zero. A day or two before the herding event, average returns increase and become statistically significant. The stocks then experience an extremely positive return on the herding day—averaging 14%. Interestingly, many stocks have negative returns the day prior to and on the day of the herding event. This is consistent with our prior results documenting that extreme negative returns draw the attention of Robinhood users as well. The pattern after the herding events is starkly different. Immediately after the herding event, returns turn significantly negative" (Barber et al., 2022, p. 3171).


## References 

- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *The journal of Finance*, 66(5), 1461-1499.
- Kahneman, D. (2011). *Thinking, fast and slow*. Macmillan.
