In response to Predictit shutting down I've decided to also shutdown PredictionAlerts. The goal was to make it easy to get price alerts for various prediction markets. I succeeded in the basic goal but never got around to three stretch goals that would have been necessary to make the service actually valuable:
* Notifications on formulas. For example you might want a notification if the following happen:
    * Equivalent markets on different platforms have different prices
    * X wins the primary gets too close to X wins the presidency
    * The price of mutually exclusive contracts trades above 1
* Pattern based notifications. For example you might want to know:
    * The first time a market hits 90, if you're looking for bonds.
    * The first time a market hits 99 if you're looking for dead cat bounces.
    * When a market flips
    * Whenever a market moves 10+ points
* Data stream notifications. For example:
    * When the CDC site is updated
    * When 538 is updated
It's sort of a cliche, but I had less time than I expected with a full time job and a baby. And with only one legal US exchange remaining the site makes a little less sense. Kalshi also has two features that make my service less necessary: e-mails on order fills and expiring orders.
I sort of committed the cardinal bootstrapping sin of not selling as I was building so I never really had many users. But even so I learned a lot since I did a lot of things for the first time. Things I used for the first time on this project:
* Flask
* Sendgrid
* sqlalchemy
* Google Cloud
* Stripe
My main take away is it's really easy and cheap to make a fully featured web service but it's a little harder to make one that looks good with actual users. I made it a little harder on myself by doing a couple of things myself where I imagine there were good tools available:
- I made my own login page and managed things like setting the cookie and sending e-mail confirmation e-mails.
- I wrote my logo svg with vim.

# Strategic Mistakes

* Solving my problem at the wrong level of abstraction. My real problem is that I need money. I went down the abstraction hierarchy and took an interest in prediction markets (which also serve other human needs, like a desire to know the future), but then instead of picking some markets, collecting data and doing some analysis, I went back up the abstraction hierarchy and made a tool to help people trade on prediction markets.
    - Solving problems on the wrong level of abstraction is a common problem of mine. For instance when I decided to start a blog why did I wrote my own static site generator and CMS? What problem am I actually solving with my blog that wouldn't be better addressed by just talking with people?
    - I chose this tool because there are many moments, for example Cuomo winning the 2020 Democratic Presidential Nomination trading at 7c for a day in the summer, where sure things trade away from 99. The problem is it's hard to say when something moves from 99 to 93 if this is in response to new evidence or it's just a bubble. And my tool doesn't help answer this question. A lot of my best trades come from tips to look at markets I wouldn't have otherwise been paying attention to. A better strategy than making this tool would have been to just make more friends that share tips. 

# Technical Mistakes
* I started out using Google datastore for storage but switched to Postgres because I wanted to use a SQL database instead of a NoSQL one. But datastore (and noSQL dbs in general?) are basically free at small scales whereas running the smallest SQL instance is $70/month on gcloud. Once I transitioned to SQL I didn't want to transition back because I'd rewritten a lot of code to use sqlalchemy (which is great). Live and learn. I should have figured there was a reason gcloud pushed datastore as the default. It was sort of a big mistake because I'd just continue running the service for no users if I was using datastore but I can't justify spending $70/month for no reason.
* I used gcloud because I used google domains and I used flask because it's what the example documentation used. But I think I probably should have used Azure or AWS just to have a more main stream skill. Sort of seems like gcloud is never going to have significant market share. And I should have used node both because it's what I use at work and there's a more comprehensive collection of node packages for web development. I think I should have had a "planning phase" where I thought about all the technologies I'd need and which provider was best. But instead I jumped in and followed my nose and did whatever seemed most natural given what I'd done before when I realized I needed a new piece. Though to be honest that was the only way I was going to actually launch anything.

