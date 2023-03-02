I'm on the [record](https://ja3k.com/blog/surp) as a Substack hater. But there's no denying there's significant demand for newsletters and some people even want to pay. You can do both those things here now. There's a free and premium subscription. In either case you'll get the same newsletters to your inbox when I write them. The pay link is just a stripe checkout link. Please use the email you want to receive the newsletter to (though you can always email me later to receive it somewhere else).

In this post I'll give some brief thoughts on technology and also explain the Rube Goldberg newsletter system I've concocted.

## (Almost) All Tech is Social Technology

The most important technologies are social in nature.

- Ubers big innovation was normalizing getting into strangers cars. As well as making a complicated logistics problem as simple as pressing a button for consumers.
- Google and Facebook are made possible by ads which are of course a technology of social manipulation.
- Conventions like LLCs and employment are new (in the scope of civilization) social ways for people to interact which has enabled more people to coordinate to solve bigger problems.

Substack's big innovations seems to be making it normal for bloggers to ask for money. It's a little weird to put a pay me link in your blog. But Substack makes it normal.

Side note the New York Times most feel so bad looking at the prices these substackers charge. Two of the bigger substackers I'm familiar with are Noahpinion and Matt Yglesias who charge $9.99 and $8 respectively while NYT is begging me to subscribe for $5 a month.

Hopefully I can ride on their normalization coattails and introduce my own premium subscription status.

## How I did It

It's quite simple: If you enter your email in the subscribe text box a request is sent to an aws lambda which sends me an email with the contents. Then I write the email down in my list of emails. When it's time to send out a newsletter I send an email to the list. Super simple. I don't know why there are a dozen companies which provide this as a service as their business model.

The premium option is just a payment link I got from Stripe. I assume Stripe will give me the email and I'll then add it to my list. I'll find out when someone pays. 
