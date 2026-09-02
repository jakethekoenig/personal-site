It is said that every tech blog has two posts: One about their intent to write more and one about how the site is hosted. The first may be repeated sometime later [[I don't like the mockery. Too often after setting the intention to write one has the uncomfortable realization they have nothing to say.]]. But I think after 104 posts I've earned a little post about the site itself. There have been a lot of updates since [the last one](https://ja3k.com/blog/su4).

# Cross Posting

My blogging has fallen off a bit since 2020 when I started to tweet more and more. I reach more people and I think the enforced brevity is good. Most books could be a blog post, most blog posts could be a tweet and most tweets don't need to be sent. But I do have some reservations about the platform:

* Twitter increasingly makes it hard to view when logged out. My tweets are for everyone!
* They've had more downtime and incidents since Elon's takeover. I fear one day it will go down for the last time.
* The search is bad.

I've fixed all these issues by cross posting my tweets to my own site. You can read them [here](https://ja3k.com/shortform). Searching your own tweets with ctrl-f is incredible. You have to try it. No network calls. Just grep over 7000 tweets.

Technically this is accomplished via a [gh action cron job](https://github.com/jakethekoenig/personal-site/actions/workflows/sync-bluesky.yml) that checks my Bluesky every 5 minutes and if there are new posts mirrors them to Twitter and my site. I also [backfilled from my Twitter archive](https://github.com/jakethekoenig/personal-site/tree/master/scripts/one_off/tweet_migration). I've tried [cross posting](https://www.npmjs.com/package/string-poaster) before but actually working from the CLI was annoying for images and on mobile. It's a lot easier to have the Bluesky feed be canonical and copied to other places I want to post.

Morally something feels off about cross posting. But I think it's actually better. People don't like Twitter for a lot of reasons and I don't want to be part of the network effect that keeps everyone there. People should be able to read my posts on whatever client they prefer. I will see engagement and engage socially on any of the three platforms.

The biggest issue is that a lot of my posting is quote tweets on Twitter which don't get cross posted. Which is maybe for the best since they're sort of first-class replies.

# RSS

My site has improved RSS feeds! The [RSS feed](https://ja3k.com/feed.xml) for the blog was temporarily broken when an [outside contributor](https://github.com/jakethekoenig/personal-site/commit/61c31997d442a6028b234feba46dcf291795e92b) tried to put the content inside the feed, which I didn't notice was broken since my reader, feeder, renders the content from the permalink. That's right this personal site accepts outside contributions, feel free to open a pull request! So anyway that's fixed now and hopefully all my Elfeed readers are able to read the site in their preferred client.

There is also an RSS feed for the [cross poasted tweets](https://ja3k.com/tweet.xml) and the now defunct [podcast](https://ja3k.com/pod.xml).

# Newsletter

You can subscribe to the blog as a newsletter in the bottom right. It's not the best process since I have to manually copy the posts into Gmail and send them out. And I haven't implemented an unsubscribe button.

# General Site Improvements

We now have a sitemap, robots.txt (welcome robot overlords!), an llms.txt and Open Graph metadata. The site also builds and deploys in GitHub CI. As of the last site update I manually ran the scripts. You really do get a lot for free when you use Substack. 

# Site Update 4 Roadmap

I totally forgot but in [my last update](https://ja3k.com/blog/su4) I made a roadmap for the site. Let's check in on how that went:

> I want to decouple my website repository into an independent static site generator and the actual unique content. Just in case anyone else wants to make another website which looks exactly like this one.

I did this and then this year undid it. I realized inventing my own markup and templating system and static site generator were all insane things to do and what I have will never be feature complete or stable and no one should ever use it. And having everything in one repo is easier.

> I want more RSS feeds. No one subscribes of course. But it'd make sense to have one for every category... 

I did some of this but didn't make per-category RSS feeds. Doesn't seem that important.

> Something vaguely related is I want to have a way to link related posts together.

I didn't do this. Doesn't seem like such a valuable thing. Probably better to just write out links on the top when relevant.

> Support for website content written in markdown.

I now do write my posts in markdown!

> A script which starts a new blog post. My current workflow involves copying a json file and editing the fields I want for the new post.

This is still my workflow. Works fine.

> Dark mode?!

I've switched back to light mode everywhere, `:colorscheme shine`. I don't think I'll ever do this now.

# The Road Ahead

* Self-host git and deploy locally. GitHub and GitHub Actions lowkey suck. I want to self host git under ja3k.com/source. And run the deploy and Bluesky sync scripts locally. GitHub actions cron is particularly awful offering no guarantees and often only running once every several hours.
* Cross post to more places. I want to cross poast to Threads, Mastodon and Farcaster at least.
* Automate the newsletter and add an unsubscribe mechanism.
* Improve comments. Right now when you submit a comment, nothing appears until you refresh which looks a little broken. Also it'd be nice to give people edit/delete affordances and the ability to add links and have persistent accounts.

Thanks everyone for reading! I plan to post a bit more going forward. I fell off a bit with work and kids but suddenly feel like I have a lot of ideas.
