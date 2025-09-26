import textwrap

story = '''You are a young adventurer living in a small town, and you've just gotten your first bike!
Your grandmother has told you stories about a mysterious hidden key somewhere in town that unlocks
a treasure chest she buried years ago.

Today feels like the perfect day for an adventure. You've saved up some pocket money and,
after the breakfast, you're full of energy, ready to explore every corner of your town.
Your bike is your trusty companion: it can take you anywhere, but riding uses up your energy,
especially when traveling long distances.

The town is laid out in a neat grid, with 25 different locations to explore. Each place might
hold surprises - some good, some not so good. You might find money scattered around, discover
hidden energy drink stashes, or even encounter some local bullies who might try to take your
hard-earned cash.

Your mission is clear: explore the town, find that hidden key, and make it back home safely
before you run out of energy and money. You can always stop by the local store to buy energy
drinks with your money - after all, staying energized is crucial for your bike adventure!

Remember, both distance and road conditions matter! The town has various types of paths:
smooth paved roads that make biking easier, bumpy side streets that tire you out faster,
and even rough dirt paths near the coast that require serious effort. Some routes between
locations are well-maintained while others might surprise you with their difficulty.
Plan your route wisely, considering not just how far you're going, but what kind of
terrain you'll encounter along the way!

The treasure awaits, but only if you can find the key and return home safely. Good luck,
young explorer!'''

# Set column width to 80 characters
wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)


def get_story():
    return word_list
