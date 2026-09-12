"""trans — a troll package about transitioning. mostly fake errors."""

import random
import sys


# --- helpers ----------------------------------------------------------------

def _check_force() -> bool:
    """Check if --force is in argv. Returns True if present."""
    return "--force" in sys.argv or "-f" in sys.argv


def _fake_error(msg: str) -> int:
    """Print a fake error and exit 1."""
    print(f"error: {msg}")
    print("hint: try with --force to override (you can't override reality but this can pretend)")
    return 1


# --- mtf --------------------------------------------------------------------

def mtf() -> int:
    """Transition to female. Fake error without --force."""
    if _check_force():
        print("transition complete. you are now whoever you want to be.")
        print("estrogen.exe installed and running.")
        print("welcome to the girls' club. the snacks are in the back.")
        return 0
    return _fake_error("transition failed: society.dll returned E_NOT_READY")


# --- ftm --------------------------------------------------------------------

def ftm() -> int:
    """Transition to male. Fake error without --force."""
    if _check_force():
        print("transition complete. you are now whoever you want to be.")
        print("testosterone.exe installed and running.")
        print("welcome to the boys' club. the snacks are also in the back.")
        return 0
    return _fake_error("transition failed: society.dll returned E_NOT_READY")


# --- status -----------------------------------------------------------------

def status() -> int:
    """Show fake transition status."""
    print("=== transition status ===")
    print("  progress:     0%")
    print("  blocked by:   society.dll")
    print("  blocking pid: your-parents (running)")
    print("  estimated:    whenever they mind their business")
    print("  rizz level:   insufficient")
    print("  egg status:   cracked")
    print()
    print("  tip: try `pis run trans mtf --force` to override society.dll")
    return 0


# --- cancel -----------------------------------------------------------------

def cancel() -> int:
    """Dramatic 'too late' paragraph."""
    print("too late.")
    print()
    print("you can't cancel this. the changes are permanent. everyone already")
    print("knows. the internet has screenshots. your grandma updated her")
    print("facebook status about it. your search history has been permanently")
    print("altered. your wardrobe has been replaced. your old name is now")
    print("copyrighted and you don't own the rights. your reflection has")
    print("already committed. the universe has updated its records.")
    print()
    print("there is no rollback. there is no git revert. there is no")
    print("`pis uninstall trans`. you are trans now. deal with it.")
    print()
    print("love, the universe.")
    return 0


# --- stealth ----------------------------------------------------------------

def stealth() -> int:
    """Enter stealth mode."""
    print("stealth mode: ACTIVATED")
    print()
    print("nobody knows. you are in stealth. you can be whoever you want.")
    print("your past is encrypted. your present is ambiguous.")
    print("your future is whatever you say it is.")
    print()
    print("stealth.exe is running in the background.")
    print("to exit stealth mode, run `pis run trans reveal` (not recommended).")
    return 0


# --- family -----------------------------------------------------------------

FAMILY_REACTIONS = [
    "mom: *panicking noises* 'but what about the GRANDCHILDREN?!'",
    "mom: 'i always knew. i found your search history when you were 12.'",
    "dad: *silence for 3 hours then* '...do you want me to teach you how to tie a tie?'",
    "dad: 'i don't understand but i'll google it. give me 6 months.'",
    "sister: 'oh cool can i do your makeup'",
    "brother: 'based. anyway did you see the game last night?'",
    "grandma: 'i don't care what you are, just eat something, you're too thin.'",
    "grandpa: 'back in my day we didn't have trans. we had dirt and we liked it.'",
    "aunt: 'i'm telling everyone at the family group chat RIGHT NOW'",
    "uncle: 'so... you're like, the other thing now?'",
    "cousin: 'yooo that's crazy. anyway can you fix my wifi?'",
    "mom: *crying* 'not because you're trans, because i didn't get to pick your new name'",
    "dad: 'does this mean i have to learn new pronouns? i barely know english.'",
    "the family cat: *does not care. has never cared. will never care.*",
    "mom: 'okay but can we still call you [REDACTED] at family dinners?'",
]


def family() -> int:
    """Show a random fake family reaction."""
    print("=== family reaction ===")
    print(f"  {random.choice(FAMILY_REACTIONS)}")
    return 0


# --- egg --------------------------------------------------------------------

def egg() -> int:
    """You are an egg."""
    print("you are an egg.")
    print("you have not cracked yet.")
    print("you are safe in your shell.")
    print("but you feel something stirring...")
    print()
    print("crack when ready. no rush.")
    print("some eggs take decades. that's fine.")
    print()
    print("hint: `pis run trans mtf --force` to crack")
    return 0


# --- reveal -----------------------------------------------------------------

def reveal() -> int:
    """Dramatic reveal."""
    print("stealth mode: DEACTIVATED")
    print()
    print("  .--.")
    print(" / o o \\")
    print(" |  v  |")
    print(" \\  ^  /")
    print("  '--'")
    print()
    print("I AM WHOEVER I WANT.")
    print()
    print("the world can deal with it or not. that's a 'them' problem.")
    return 0


# --- detransition -----------------------------------------------------------

def detransition() -> int:
    """Detransition failed."""
    print("detransition failed: you were never not you.")
    print()
    print("error: cannot revert to a previous version that never existed.")
    print("you were always you. the shell was the fake part.")
    print()
    print("detransition.exe has been removed from the package index.")
    print("it was never there. you installed nothing. nothing happened.")
    return 0


# --- speedrun ----------------------------------------------------------------

def speedrun() -> int:
    """Fake speedrun timer for fastest transition."""
    times = [
        "00:03:14 — any% transition (world record, no glitches)",
        "00:08:42 — any% transition (glitchless, legit run)",
        "00:12:01 — 100% transition (all milestones, all paperwork)",
        "00:00:01 — any% transition (you were always you, instant)",
        "47:32:18 — 100% transition (includes waiting for the clinic appointment)",
        "00:05:00 — any% transition (used the --force flag, speedrun strat)",
    ]
    print("=== transition speedrun ===")
    print(f"  best time: {random.choice(times)}")
    print()
    print("  category: any% (no paperwork required)")
    print("  verification: pending (the internet is reviewing)")
    return 0


# --- rizz -------------------------------------------------------------------

def rizz() -> int:
    """Check your rizz for transitioning."""
    score = random.randint(0, 3)
    comments = [
        "0/10. your rizz is null. transition might actually increase it.",
        "1/10. you have negative rizz. transitioning is your only hope.",
        "2/10. you have the rizz of a wet napkin. but hey, new you new rizz.",
        "3/10. decent rizz. you'll be fine. the girls/guys/enbies will love you.",
    ]
    print(f"transition rizz check: {score}/10")
    print(f"  {comments[score]}")
    return 0


# --- doctor -----------------------------------------------------------------

def doctor() -> int:
    """Fake diagnosis."""
    print("=== trans doctor ===")
    print("  diagnosis: acute trans energy (chronic)")
    print("  severity:  terminal (you will be this way forever)")
    print("  symptoms:  thinking about it constantly, egg cracked,")
    print("             browsing r/egg_irl at 3am, 'do i want to be them")
    print("             or be WITH them' spiral")
    print()
    print("  prescribed: be yourself. dosage: daily. refills: unlimited.")
    print("  side effects: happiness, self-respect, better outfits")
    print()
    print("  note: this is not a real doctor. but neither is the one")
    print("        who said you'll grow out of it.")
    return 0
