I recently read The Timeless Way of Building by Christopher Alexander because of an anonymous Twitter recommendation. Though about physical architecture it spurred a lot of thoughts about software. Which I suppose is a kind of architecture.

## The Quality without a Name (Homeostasis)

The first part of the book concerns "The quality without a name". He gives a few different candidate words like alive, whole, comfortable, freedom, exact, egoless, eternal but to me the best word to describe the balancing of forces in a complex system is homeostasis.

We focus on progress. And what is new has more salience than what is constant. But the reality is the supermajority of people's time and energy are spent staying exactly where they are. Maintaining inner balance in their own lives and bodies and staying in harmony with the wider social context. Every hour slept, every meal eaten, every time you brush your teeth. It's all maintenance.

Seeing your bank account go up as you work feels like progress. But what is the money for? The majority goes to rent/mortgage/food, homeostasis. Savings go towards funding a retirement which is just a way to prolong homeostasis past the point where you can work. Work being just a way to serve the broader homeostasis of civilization.

The chapter introducing the quality is full of beautiful scenes of koi ponds and bird baths. And it is beautiful to dance through life. But the last sentence "It is a slightly bitter quality" gets to the heart of it. We swim lest we drown.

## Patterns of Events

What is all this software for? The more I work on llm powered codegen the more salient this question grows. Mostly software exists to enable a pattern of behavior, usually of people, across time. The most successful projects serve a need that happens frequently and acutely. For example:

* Person is bored -> Person checks twitter/facebook/instagram/etc.
* Person is lonely -> Person swipes on Tinder
* Person is curious -> Person Googles

And of course many projects will simultaneously satisfy many needs and in fact needs to in order to survive e.g.

* Person wants attention -> Person posts on twitter/facebook/instagram/etc.

Of course the desire for attention is much scarcer than the desire to be entertained but social networks survive by matching the small in percentage but large in number population of posters to the supermajority of scrollers. So the two desires can be simultaneously satisfied.

Tinder also has a major imbalance with far more men than woman. They haven't been able to solve it and I'd predict in the long term this will lead to a collapse of swipe based dating apps. Tinder's revenue has been flat for 3 years. But the long term may be a really long time in this case and I can't predict what will emerge to satisfy people's pair bonding desires in the future. Maybe not software at all.

I think this is one reason Cursor has been so successful relative to the full PR generation modality offered by Mentat, Codex or Juul [[Try [Mentat](mentat.ai)! It's the best. Honest!]]: It slots right into an existing entrenched pattern of behavior. Instead of:

* Engineer needs to do their job -> They open vscode.

They open Cursor. VSCode, now with AI! So the work is similar but now when another common pattern comes up "Engineer doesn't know something" they can use AI instead of stack overflow. And they don't have to be reminded to use the AI because tab completion suggestions are right there.

The full PR generation approach requires a totally different way of working. You have to start by writing up precisely what you want. It's sort of an unnatural first step because often to see exactly what change you want you have to bounce around the code a bit first. And now what do you do while the agent is working? One thing you could do is start another agent. But bouncing between tasks is an unnatural way to work. It's more productive to focus on one thing at a time.

The user's are just one group who's needs must be balanced by the software project. Hidden out of sight from the users the code itself must balance a variety of forces.
* It must be efficient to keep server costs manageable.
* It must be simple enough that new contributors can become productive.
* It must be modular enough that it can be practically changed.
* It must be tested enough to prevent regressions [[Side note on tests: I used to think the primary purpose was to improve the correctness of the code you're writing. But if you write some code and run it you can sort of see if it's right at least on the inputs you care about most. The primary purpose as I see it is to prevent your code from being broken after committing. Which it assuredly will be eventually if untested.]].

## Pattern Languages


