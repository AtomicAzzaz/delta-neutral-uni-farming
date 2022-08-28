# On uniswap delta neutral farming

This python project aims to build, analyze, benchmark, and run a delta neutral farming strategy on UniswapV2 and similar forks.

## Motivation

For several months now, UniswapV2 forks have been multiplying, promising liquidity providers increasingly large APYs. Would it be possible to take advantage of these high APYs, without taking risks?

## The strategy

In this document, I will focus on USD/token pools. The idea is to benefit from liquidity provider APYs while being delta neutral, that is not being exposed to the market.
So having provided a unit of liquidity (= 1 USDT/Stablecoin + the equivalent of 1 USD in the form of another token T), how can we be delta neutral? The first idea is to short 1 USD of T. But as a liquidity provider, our exposure to the market depends on the price of the underlying asset T.
Indeed, with \
$Q_s$ the amount of stablecoins S in the pool\
$Q_t$ the amount of token T in the pool\
$P$ the price of a token T in stablecoin S\
We have the following (cf UniswapV2 [whitepaper](https://uniswap.org/whitepaper.pdf)):\
$Q_s * Q_t = k$ with $k$ constant\
$P = Q_s / Q_t$\
Those equations hold with $Qs$ and $Qt$ being the amount redeemable by a single liquidity provider (with, of course, another $k$). We can solve for $Q_t$ and $Q_s$:  
$Q_t = \sqrt{\frac{k}{P}}\\
Q_s = \sqrt{k*P}$.\
 Thus, by shorting the non-constant amount $\sqrt{\frac{k}{P}}$ of token T we become market neutral, while profiting from fees.

### Proof
Let's introduce time canonically, and let a unit of time pass. We must not gain/lose directly from price variations.

$
P(t+1) = P(t) + dP$

$Q_s(t+1)  = \sqrt{kP(t+1)} = \sqrt{k(P(t) + dP)} = Q(s) * \sqrt{1 + k dP}$

First order development:

$
Q_s(t+1) \simeq Q_s(t) * (1 + \frac{1}{2}kdP) \implies dQ_s = \frac{1}{2}Q_s(t)kdP
$

And we also have

$Q_t(t+1) = \frac{Q_s(t+1)}{P(t+1)} = \frac{Q_s(t)+dQ_s}{P(t)+dP} = \frac{Q_s(t)}{P(t)}  \frac{1}{1+\frac{dP}{P(t)}} + \frac{dQ_s}{P(t)}  \frac{1}{1+\frac{dP}{P(t)}}
$

First order development:

$Q_t(t+1)\simeq (Q_t(t)+ \frac{dQ_s}{P(t)}) * (1 - \frac{dP}{P(t)}) \simeq Q_t(t) + \frac{dQ_s - Q_t(t)dP}{P(t)}  $









## Openings

One may focus on token/token pools. There might be interesting positively correlated pairs where the pools is thus less exposed to market movements. Furthermore, having two shorts implies the earning of two funding rates fees.