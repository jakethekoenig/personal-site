I've been conducting most of my conversations with GPT in Vim in the small plugin I made (alright GPT mostly made it) you can see [here](https://github.com/jakethekoenig/ChatVim). There are a number of benefits to this:

You can paste code to and from the buffer using your favorite vim commands intead of clicking that copy button.
You don't have to alt tab to a browser and risk spending the next 30 minutes on your email/hackernews/twitter/whatever you're addicted to at the moment. This is sort of a compensation for a character flaw but I can't be the only one for who switching to a web browser is a risky activity.
Syntax highlighting works. You'll need to do your Q&A in a markdown file and add the following to your vimrc: 
```
let g:markdown_fenced_languages = ['html', 'js=javascript', 'python', 'clojure', 'javascript']
```
But then you nice syntax highlighting instead of the black on white on [the offical site](https://chat.openai.com/)
You can search your chats with grep or ctrl-f or whatever. I personally keep all my conversations in one ever growing text file. Open AI does a nice job of summarizing what a conversation is about but often I'll ask a lot of yes-and questions and if I have several conversations about the same project it can be hard to remember in which a topic came up. Since there's no global search it can be hard to find stuff.
You don't have to log in every day.
The plugin itself is very thin and it's easy to ask Chat GPT to write you your own for whatever your editor of choice is. 
