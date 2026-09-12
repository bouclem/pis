"""girlfriend — you have no girlfriend. this package reminds you."""

import random


ROASTS = [
    "you have no girlfriend. go touch grass.",
    "no girlfriend? again? bro...",
    "imagine having no girlfriend. oh wait, you don't have to imagine.",
    "you code more than you talk to girls. that's the problem.",
    "your IDE is your only companion. sad.",
    "no girlfriend detected. touch grass immediately.",
    "bro has a .pth file but no girlfriend path. tragic.",
    "you installed a package about not having a girlfriend. self-aware at least.",
    "git commit -m 'still no girlfriend'",
    "error 404: girlfriend not found in repo or real life.",
    "your love life has fewer entries than packages/index.json.",
    "pis install girlfriend? more like pis install cope.",
    "you have 1 package installed and 0 girlfriends. the math checks out.",
    "skill issue: cannot find girlfriend. try `pis install life`.",
    "your rizz is null. cannot invoke .flirt() on None.",
]


RATINGS = [
    (0, "negative rizz. you repel girls by existing."),
    (1, "1/10. your IDE theme gets more action than you."),
    (2, "2/10. even your code has better coupling than your love life."),
    (0, "0/10. you are a singularity of no rizz."),
    (3, "3/10. you talked to a girl once. she asked for directions."),
    (1, "1/10. your pull game is `git pull` and even that fails."),
    (0, "0/10. you are the .gitignore of girls — invisible."),
    (2, "2/10. you have more dependencies than dates."),
    (0, "0/10. not even a namespace package wants you."),
    (1, "1/10. your crush left you on read and on seen."),
    (0, "0/10. you are uninstalled from the dating pool."),
    (2, "2/10. you tried rizzing up a chatbot. it blocked you."),
    (0, "0/10. your love life is a syntax error no linter can fix."),
    (1, "1/10. you wrote a love letter. in python. it crashed."),
    (0, "0/10. even import girlfriend returns ImportError in real life."),
]


def roast() -> int:
    """Print a random roast about having no girlfriend."""
    print(random.choice(ROASTS))
    return 0


def rate() -> int:
    """Rate your chances of getting a girlfriend (always terrible)."""
    score, comment = random.choice(RATINGS)
    print(f"chances of getting a girlfriend: {score}/10")
    print(f"  {comment}")
    return 0
