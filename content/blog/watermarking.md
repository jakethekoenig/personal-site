Recently [Anthropic announced](https://www.anthropic.com/news/claude-text-watermark) they would watermark Claude output going forward. People I respect said this was [fine](https://x.com/tenobrus/status/2089080656026566806) and that was my first impression also but when digging into my confusions about how it worked I came to view it as an on net bad thing.

# How it doesn't work

Of course LLM tokens are already sampled randomly and that's fine. You might naively come up with an algorithm like this:

1. When sampling a token use a hash of the full prefix up to that point as the random seed to sample a number between 0 and 1. 
2. Line up the tokens and see where this number falls in the probability mass. Sample that token.

I would be totally fine with this algorithm. It would clearly not affect quality or the distribution. But it's also totally useless:

1. When guessing if a snippet of text is LLM generated you don't know the input. Or even if it's at the beginning of the LLM response.
2. It's very sensitive to even slight perturbations to the point that if you changed just one token at the beginning you'd get no signal at all.

# How it actually works

When we look at a snippet of text we can't know for any given word the logprob distribution it was sampled from. So we need a fully local algorithm to bias the distribution. Then we can measure whether the text is correlated with our bias or not. The rough algorithm is:

1. Use the preceding 4 tokens to generate a random seed.
2. Use that randomness to give every token 0 or 1. (Call this assignment the tournament function)
3. Sample two tokens according to the underlying distribution. Then if one has 1 and the other 0 sample it, otherwise sample uniformly between them.

See [this paper](https://www.nature.com/articles/s41586-024-08025-4) for details.

There are knobs to tune in (1) how many preceding tokens factor into the seed and (3) how many rounds of the tournament you run for one sample.

So why am I against this?

## 1. Global Entropy Reduction

I was fine with the global algorithm because it was highly sensitive to the input. But this algorithm only depends on the previous 4 tokens. And it's global across all completions. Imagine completing the following sentence:

> My favorite fruit is

Suppose the underlying LLM is split between apple and banana with 50-50 probability. But the tournament function gives 1 to apple and 0 to banana. Now the probability we sample apple is 75% instead of 50%. The 50-50 depends on what came earlier in the context than "My favorite fruit is" but the direction of the bias is the same. The LLM will have a global preference to complete the phrase in this way across all LLM completions. 

It's not a huge deal but LLMs have already caused a huge collapse in the variety of text. It seems not prudent to give more away without a corresponding large benefit.

Of course I'm not the first to observe this and it was acknowledged in the SynthID paper. I just think it matters enough not to do it:

> For our experiments, we configure SynthID-Text to be single-sequence non-distortionary; this preserves text quality and provides good detectability, while having some reduction to inter-response diversity.

Note you make think in addition to reducing inter-response diversity it would also change intra-response diversity by causing repeated snippets to be more correlated than they should but the solution to that is to only use this biased sampling the first time a sequence of 4 tokens appears in the response.

## 2. Uselessness

There are a lot of reasons this isn't very useful technology:

1. It's actually very easy to get around this algorithm. One could ask Claude to write [test](https://chatgpt.com/share/6aaab0c7-cfd0-83e8-8914-7d283a97a092) between every word of output and then remove those words before posting. This would throw off the tournament algorithm.

2. As LLMs get stronger their distributions get more concentrated. The closer the most likely token's probability gets to 1 the more text you need to sample before getting signal.

3. Presumably every LLM will have its own tournament function. If you're paranoid about a given snippet of text will you check every provider's watermarking api? What about open source models which can be sampled as the user pleases.

4. We already have Pangram which isn't strongly affected by any of the above 3 issues.

## No big deal

So to sum up I'm against LLM watermarking. But at the same time I concede it has no effect on quality in a given completion, humans can't distinguish watermarked text and I am broadly in favor of AI detection tools. So I don't feel that strongly about it either.
