/* toy-deck-29.h — the 29-card toy deck for the Apollo Monte Carlo warm-up.
 * Face value = the species' real Gen-3 base HP — numbers with receipts.
 * Generated card stock for the practice games (shuffle, deal, count).
 */

#ifndef TOY_DECK_29_H
#define TOY_DECK_29_H

typedef struct {
    const char *name;    /* nickname on the card */
    const char *species; /* what the card art would show */
    int hp;              /* face value printed on the card */
} Card;

#define DECK_SIZE 29

static const Card deck[DECK_SIZE] = {
    /* --- first squad --- */
    { "Wick",    "Combusken", 60 },
    { "Burr",    "Poochyena", 35 },
    { "Squall",  "Wingull",   40 },
    { "Pinch",   "Zigzagoon", 38 },
    { "Floss",   "Wurmple",   45 },
    { "Buoy",    "Marill",    70 },
    { "Bog",     "Lotad",     40 },
    { "Lull",    "Slakoth",   60 },
    { "Loam",    "Shroomish", 60 },
    { "Flit",    "Taillow",   40 },
    { "Blare",   "Whismur",   64 },
    { "Pith",    "Nincada",   31 },
    { "Doze",    "Abra",      25 },
    { "Reign",   "Goldeen",   45 },
    { "Pounce",  "Skitty",    50 },
    { "Shard",   "Sableye",   50 },
    { "Clad",    "Aron",      50 },
    { "SCREECH", "Zubat",     40 },
    { "Bop",     "Makuhita",  72 },
    { "Quartz",  "Geodude",   40 },
    { "Arc",     "Electrike", 40 },
    { "Minuet",  "Minun",     60 },
    { "Tuft",    "Oddish",    45 },
    /* --- second squad --- */
    { "Silt",    "Marshtomp", 70 },
    { "Veil",    "Kirlia",    38 },
    { "Quill",   "Skarmory",  65 },
    { "Burp",    "Numel",     60 },
    { "Sog",     "Lombre",    60 },
    { "Wisp",    "Illumise",  65 },
};

#endif /* TOY_DECK_29_H */
