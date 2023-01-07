
If you give a man two numbers he will try to add them. One of the first things you're taught as a human is numbers and once you've got a handle on them you're taught to add them. Then you spend the next 20 years of your life being given numbers for your performance and having those numbers added together. But consider for a moment: what are the units of your GPA? If there is such a thing as utility, what are it's units?

It's not true that any two numbers can be added and a meaningful result obtained. Sometimes their types don't agree: what's $5 + 3cm? Some other quantities simply cannot be meaningfully added. What is 3 stars + 4 stars with regards to movie ratings?

But this is all very trite and obvious and of course the utilcels have thought of it.

# Why Should Utility be a Real Number?
<blockquote class="quote epigraph">
<p>God made preferences. All else is the work of man.</p>
<p>- Leopold Kronecker, basically</p></blockquote>

Let's begin my considering the utility of an individual before moving on to aggregation. For concreteness let it be my utility.

In the beginning there are preferences. I prefer green tea to black. I prefer my eggs fried to scrambled. At first glance if all I have to work with is preferences you might think all I could give you is an ordering of scenarios. I could say green tea gives me 5 utility and black tea 1 or green tea 3.89 utility and black tea -300 and it'd make no difference to what happens when you offer me my choice of beverage.

But there is a tool to make meaningful different utility functions besides ordering: randomized mixing. Say there are three outcomes:
- Green tea
- Black tea
- No drink
And I have the choice between Black tea or x% chance of Green tea otherwise nothing.
If I prefer Black tea to no drink than there should be some x where I would choose the guaranteed Black tea over the gamble. Once I've chosen random numbers for my utility for no drink and for black tea, say 0 and 1, My utility for green tea is determined. It is 1/x where x is the smallest probability for which I'd choose the gamble.

Of course none of this is original and if you work out the details you get the [Von Neumann-Morgenstern utility theorem](https://en.wikipedia.org/wiki/Von_Neumann%E2%80%93Morgenstern_utility_theorem). 

Already there are a number of possible objections:
### 1. What if there is no such x?
    This could mean I actually prefer no drink to black tea. That's fine, and we can mix up the gamble to determine exactly what negative utility I give to black tea. But what if I prefer black tea to no drink it's just my preference for green tea is so strong I'd always pick the gamble? With tea that maybe seems implausible but what if I'm choosing between tea or getting eaten by a shark? For someone who takes this very seriously see [Erik Hoel](https://erikhoel.substack.com/p/why-i-am-not-an-effective-altruist). I've never thought this is a particularly serious objection because I do risk a small probability of violent death for a little bit of entertainment all the time by getting in my car and driving. Maybe when you strip away the details and make it a pure trolley problem it's easy to have the intuition that you'd never choose a guaranteed beverage plus a small probability of death over staring at a wall but in practice everyone does take the gamble all the time.
### 2. Are we putting the cart before the horse?
    If our goal is to build a moral theory should we be asking how should I prefer green and black tea not how do I prefer green and black tea? In the case of tea this seems unimportant because how could the choice be morally relevant? But maybe I'm choosing between beef or tofu? Maybe I don't intrinsically have a preference for the ethical treatment of the livestock and produce I eat, but maybe I should?
### 3. But 0 and 1 are arbitrary. This doesn't uniquely determine a utility function.
    This isn't a problem if we're just looking at my value and decisions. But it becomes a problem when we wish to aggregate many people's preferences. It doesn't make sense to add together a bunch of functions which were determined in such a way as to be insensitive to shifts and scales! This brings us to Harsayni's Aggregation Theorem.

# Harsayni's Argument

Now it doesn't make sense to add a bunch of functions determined up to scale and shift but it sure would be convenient, since all we know how to do is add. One piece of evidence that we should add is Harsayni's 1955 argument which I will reproduce almost in its entirety here. We just require 3 (and one unmentioned by Harsayni) assumptions:

1. Individuals have (or can be given/assigned) a utility function \(U_i\) consistent with EV as discussed in the previous section. [[These utility functions need not be selfish. They shouldn't depend on each other or we may run into computability issues but they may depend on each other's inputs. e.g. It's fine for someone's utility to be lower if they have much more money than their friends.]]
2. Society, or the collective, can be given such a function \(\mathscr{U}\) as well.
3. Society's utility function is a function of the utility of the individuals. E.g. for two different worlds where everyone has the same utility, society's utility should be the same. I'll write \(\mathscr{U} = \mathscr{U}(U_1, \dots, U_n)\) when using this functional relationship.
3': There is some event for which all \(U_i = 0\) and on this event \(\mathscr{U} = 0\). Call this event \(O\). This isn't so much an assumption as fixing a scale because remember utility in the VN-M sense is only determined up to shift. 

Bonus assumption: Harsayni assumes this in his proof but as far as I can tell it doesn't follow from the previous 3 or is at all obvious: For each \(i\) there exists an event for which \(U_i = 1\) and the rest are \(0\). To me this is a big independence assumption. We don't assume the \(U_i\) are selfish or egoistic. They're just the utility functions people happen to have which could be selfish but could also be altruistic. In practice two individuals who are married or business partners could have extremely correlated utility functions. If they're identical there's no issue but the nightmare scenario is something like one business partner being risk loving and having a utility function which is company profits and the other having log profits so their utility functions are monotonically related. [[Though assuming \(U_i = 1\) in this scenario as opposed to any other nonzero value is no issue as the \(U_i\) are only determined up to scale.]] [[Linearity of Expected Value is so powerful I wouldn't be surprised if a more careful argument could remove this assumption. With this assumption though the proof is very easy.]]

From this we can deduce a result which at first blush may seem surprisingly strong but will follow from considering what the expected value of just a few mixed scenarios must be. One take away from the theorem is consistency over all randomized scenarios is actually an extremely strong assumption.

<p style="text-indent:0;"><em>Theorem</em>. \(\mathscr{U} = k_1 U_1 + \dots + k_n U_n\) where \(k_i\) is the total utility when individual \(i\) has utility \(1\) and all others have \(0\) e.g. Societal utility is a weighted sum of individual utility.</p>

<p style="text-indent:0;"><em>Proof</em>. First we prove \(\mathscr{U}\) is homogeneous in \(U_i\) that is,</p>

\[ \mathscr{U}(kU_1,\dots,kU_n) = k\mathscr{U}(U_1,\dots,U_n). \]

Let \(O\) denote an event for which all \(U_i\) are \(0\) and \(\mathscr{U}\) is \(0\). Let \(P\) be some other event for which the utility functions take the values \(u, u_1, \dots , u_n\) respectively. Now consider a mixing event which is \(P\) with probability \(p\) otherwise \(O\). Of course we have \(\mathscr{U} = p\cdot u\) and \(U_i = p u_i\) in this scenario. Which is exactly the homogeneous claim. Two notes:
1. I've only shown the homogeneous claim for \(k\leq 1\). Harsayni spends 4 times as much text dividing but I'll leave you to fill in the details or read the original paper.
2. It's not necessary in this step to assume the \(u_i\) could take on any value or even that they're nonzero.

Now let \(S_i\) denote a prospect for which individual \(i\) gets utility \(U_i\) and all other individuals get utility \(0\). As I said above that such a prospect exists is a big assumption but it slips in in the original paper. By our homogeneity result we know \(\mathscr{U} = k_i U_i\) on prospect \(S_i\).

Now take the mixed prospect that is equally likely to be each \(S_i\). By the linearity of expectation for each individual this prospect is worth \(U_i/n\) and for the collective it is worth \(\mathscr{U} = \sum k_i U_i/n\).

Using homogeneity once more we get \(\mathscr{U} = \sum k_i U_i\) for a prospect where each individual's utility is \(U_i\) (as opposed to \(U_i/n\) as it was in the previous paragraph).

<div style="text-align:right;">\(\blacksquare\)</div>

Like I said, not much of a proof. Somehow just from the linearity of expected value we've derived a whole moral philosophy [[For some deep ja3k/EV lore see <a href='https://www.tumblr.com/jaekmtg'>this 2016 tumblr post</a>.]].

## Aside on p-norms

I have a math friend who likes to joke that the problem of the repugnant conclusion is just a matter of choosing the right p-norm. At \(\ell^1\) we have Harsayni's addition, at \(\ell^\infty\) we have Rawl's (insane) position. By choosing the proper \(p\) in between \(1\) and \(\infty\) we can get an ethical theory to our tastes. But the choice of \(1\) is not arbitrary. It's the constant for which both the social utility and individual utility functions can both be rational in the Von Neumann-Morgenstern sense.

# Why I am not convinced

I had planned to write a blog post making the point in the first section in May 2022 before even knowing about the Von Neumann-Morgenstern Theorem. When the Effective Altruism (EA) criticism contest was announced I decided to do a little more research and make my post a little better [[Missed that boat unfortunately. Criticism is its own reward though so I'm posting anyway.]]. Having read Harsayni's Theorem I think there's better theoretical justification to add but I still have a number of qualms.

I am basically totally convinced that an organization founded to be altruistic has to be fundamentally utilitarian or irrational though. So in that sense this isn't a critique of EA but is possibly a critique of someone deciding to be EA.

- What the theorem of course can't tell you how to do is how to choose the weights. In practice maybe this is a weak critique though. In altruistic practice it seems people focus their giving on people plausibly maxing out the utility scale in the negative direction. Maybe you can't prove a nice theorem in this context like Harsayni was able to do, but it seems reasonable to say dying of cancer is about as bad as dying of malaria and both are much worse than not getting your favorite flavor of ice cream.
- I was turned onto Harsayni from [this interview](https://80000hours.org/podcast/episodes/will-macaskill-moral-philosophy/) where MacAskill gives the aggregation theorem as tied for his second favorite argument for utilitarianism along with rejection of personhood arguments behind track record. I think there's something contradictory about taking the aggregation theorem and personhood rejection as your top two reasons. Why do our utility functions have to respect expected value in this way? Because otherwise we're exploitable as agents. We can be dutch booked. But doesn't concern for this scenario imply a strong sense of self? Why would I care that as I wandered in circles over my choices I ended up worse off if I didn't have a strong sense of self identification?
- Similarly it seems like Preferentism is out of fashion. See this excellent [critique](https://users.ox.ac.uk/~sfop0060/pdf/can%20there%20be%20a%20preference-based%20utilitarianism.pdf). And listening to other 80k interviews it seems like hedonism is more mainstream than preferentism in the EA community [[Sorry if this is a mischaracterization or there are existing surveys. I looked at this [survey of philosophers](https://philpapers.org/surveys/results.pl) but it doesn't seem to get at quite this question.]]. But again it seems like the theory is built out of the primacy of preference.
