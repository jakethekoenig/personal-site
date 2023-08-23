Everyone and their mom has their own Twitter clone. Even worse some of the twitter clones e.g. Mastodon are closer to schemas for generating twitter clones than twitter clones. So what's a poster to do? Simple: use [string-poaster](https://www.npmjs.com/package/string-poaster) to post everywhere simultaneously. Previously I would have said just use twitter but they seem worryingly close to losing the mandate of heaven. And besides who wants to identify with their social network. I don't care if my beer is woke or anti-woke. I'm just here for the posts.

# Usage

Install:

```
npm i -g string-poaster
pip install farcaster # If you want to post on farcaster. Unfortunately the node library doesn't support images.
poast-login # This will prompt you for the credentials of the accounts you want to use.
```

Use:
```
poast "Hello world"
poast -xf "Hello twitter and farcaster" # Only posts to twitter and farcaster
poast -p "Checkout this image" # Dumps the clipboard and attaches the image to the first post. Only works on ubuntu with xclip and convert installed.
poast "Checkout this thread with 3 images" image1.png image2.png "Second post" image3.png
```

# Moral Qualms

For a bit I was worried there was something morally off about cross posting to every social network. Of course I owe Musk and Zuckerberg and everyone else who wants to stand up a textbox and an infinite scroll nothing. But there is something of a social contract between follower and followee. A sense of being in the same space posting at each other is maybe lost if I'm posting from termux. It is after all SOCIAL media.

But after thinking about it a little more I decided the opposite is true. It's unethical to only be on one of the networks because then I could become a reason why someone does or doesn't migrate. Right now it seems like Twitter is really popping and the other networks are sort of ghost towns (though to be honest the problem may just be that it's a lot of work to make a social network a super stimulus. It doesn't happen overnight. And I haven't put in the work anywhere else. And perhaps that's good and I never should have done it the first time.). So if someone wants to migrate social networks, perhaps the X is too much, they may find it difficult if everyone is only posting on Twitter. But if everyone was posting everywhere than anyone would be free to choose their app of choice based on deep moral principles and how satisfying the scroll motion feels.

And I will engage on any platform. I should get notifications [[Actually the notifications on every platform besides twitter have been really flaky for me, so maybe not.]] anywhere and am happy to reply under any of my posts. For the time being I'll probably only see your tweets on twitter. But that could change.

# A view towards the future

Social networks require a lot of work from poster and postee that seems like in a world of LLMs might finally be eliminated. For example:

* If I want to see Zvi's magic posts but not his covid posts how can I accomplish that? Zvi could make two accounts? Or I could make a complicated series of mute words. But what if I want to see someone else's covid posts?
    - In the future I can just tell an LLM: share Zvi's magic posts with me but not his covid posts.
* If someone is posting a variety of stuff on a variety of platforms it can be difficult to see it all. But perhaps in the future I'll just tell the LLM: show me the best stuff from Zvi no matter where he posts it. And the LLM will read the internet and determine which posts are from Zvi that I'd like to see.

I'm sort of inspired by louis02x's [skyline](https://louis02x.com/blog/skyline) here.

Note this is sort of the opposite direction that social networks have been trying to take us. They want to become a protocol and define what a post is. But perhaps in the future an LLM can bring the posts I care about to me and hide their underlying site context.

