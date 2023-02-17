This post breaks one of my informal rules for writing: "Don't write about the current thing" [[I intended to write a "my rules for writing" post at some point but at this point the only two I remember are this one, "no advice", which maybe I've broken from time to time but kept to the spirit of, and "no politics" which I've sort of broken twice.]]. But Chat GPT and now Bing have been swallowing up everything and I wanted to say some things. I'm sort of being this guy:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">A person sees a crowd gathered in a park. Wading through he sees a man playing chess with a dog. <br><br>&quot;What a smart dog&quot; they exclaim.<br><br>&quot;Not really&quot;, replies a member of the crowd. &quot;It&#39;s down two to five&quot;.<br><br>This is basically how I feel when people discuss current AI abilities.</p>&mdash; ja3k (27/35 tokens remaining) (@ja3k_) <a href="https://twitter.com/ja3k_/status/1275787443292299266?ref_src=twsrc%5Etfw">June 24, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

But to be clear I'm not saying the dog isn't impressive. I'm just saying I don't want it to be my tutor.

I've tried to use Chat GPT three times and all three times it failed so then I stopped trying. I tried to use it to edit my utilitarian post. I pasted one paragraph at a time and asked for feedback. Here is the transcript up until the point where I gave up:
![edit_transcript edit_transcript](/asset/pic/gpt/edit_transcript.png)

Note two things:

- It's very nice. I think humans have this fault too where when you ask them to be edit they often focus on the positive.
- When I do push it to be more critical it makes something up about what I wrote. It says to replace centimeter with cm but it is cm in my original writing.

I recently put [prediction alerts](https://www.predictionalerts.com) back online. I ended up just provisioning a smaller shared core postgres db instance which will cost $0.20 a day. But before I settled on that I was considering bundling in an sqlite db and using the local file system to run it all out of one ec2 instance.
![aws aws](/asset/pic/gpt/aws.png)
In the very first bullet it tells me to go the AWS management console. Also maybe this is expecting too much but using sqlite in this way is sort of a bad idea and it should tell me that.

I wanted to learn more about dark energy, so I asked it where I could see astronomical data and it didn't even try to help me:
![dark_energy dark_energy](/asset/pic/gpt/astro.png)

Probably I'm both expecting too much and bad at prompt engineering. But for the time being I'm sticking to google and documentation.
