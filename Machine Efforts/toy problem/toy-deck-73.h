/* toy-deck-73.h — the full-size toy pool for Game 1 practice.
 * Isomorphic to the real problem: 73 cards total, deal a hand of 29.
 *   - Cards 0-28:  a hand-picked party of 29 — they play the role of
 *                  "the Apollo 29", the hand history dealt.
 *   - Cards 29-72: wild Hoenn species — they play the 44 non-Apollo
 *                  astronauts, the comparison pool.
 * Face value = the species' real Gen-3 base HP — numbers with receipts.
 * The toy question, identical in shape to Game 1: shuffle all 73, deal 29
 * at random, count the chonkers (hp >= 70, threshold adjustable) —
 * how often does a random hand out-chonk the picked party?
 */

#ifndef TOY_DECK_73_H
#define TOY_DECK_73_H

typedef struct {
    const char *name;    /* nickname, or species for the wilds */
    const char *species; /* what the card art would show */
    int hp;              /* face value printed on the card */
} Card;

#define DECK_SIZE 73
#define HAND_SIZE 29

static const Card deck[DECK_SIZE] = {
    /* --- the picked party, first squad --- */
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
    /* --- the picked party, second squad --- */
    { "Silt",    "Marshtomp", 70 },
    { "Veil",    "Kirlia",    38 },
    { "Quill",   "Skarmory",  65 },
    { "Burp",    "Numel",     60 },
    { "Sog",     "Lombre",    60 },
    { "Wisp",    "Illumise",  65 },
    /* --- the wild pool: 44 Hoenn species, the comparison cohort --- */
    { "Pelipper",  "Pelipper",  60 },
    { "Mightyena", "Mightyena", 70 },
    { "Linoone",   "Linoone",   78 },
    { "Beautifly", "Beautifly", 60 },
    { "Dustox",    "Dustox",    60 },
    { "Ludicolo",  "Ludicolo",  80 },
    { "Nuzleaf",   "Nuzleaf",   70 },
    { "Shiftry",   "Shiftry",   90 },
    { "Swellow",   "Swellow",   60 },
    { "Loudred",   "Loudred",   84 },
    { "Exploud",   "Exploud",  104 },
    { "Hariyama",  "Hariyama", 144 },
    { "Nosepass",  "Nosepass",  30 },
    { "Delcatty",  "Delcatty",  70 },
    { "Mawile",    "Mawile",    50 },
    { "Lairon",    "Lairon",    60 },
    { "Aggron",    "Aggron",    70 },
    { "Meditite",  "Meditite",  30 },
    { "Medicham",  "Medicham",  60 },
    { "Manectric", "Manectric", 70 },
    { "Plusle",    "Plusle",    60 },
    { "Volbeat",   "Volbeat",   65 },
    { "Roselia",   "Roselia",   50 },
    { "Gulpin",    "Gulpin",    70 },
    { "Swalot",    "Swalot",   100 },
    { "Carvanha",  "Carvanha",  45 },
    { "Sharpedo",  "Sharpedo",  70 },
    { "Wailmer",   "Wailmer",  130 },
    { "Wailord",   "Wailord",  170 },
    { "Camerupt",  "Camerupt",  70 },
    { "Torkoal",   "Torkoal",   70 },
    { "Spoink",    "Spoink",    60 },
    { "Grumpig",   "Grumpig",   80 },
    { "Spinda",    "Spinda",    60 },
    { "Trapinch",  "Trapinch",  45 },
    { "Vibrava",   "Vibrava",   50 },
    { "Flygon",    "Flygon",    80 },
    { "Cacnea",    "Cacnea",    50 },
    { "Cacturne",  "Cacturne",  70 },
    { "Swablu",    "Swablu",    45 },
    { "Altaria",   "Altaria",   75 },
    { "Zangoose",  "Zangoose",  73 },
    { "Seviper",   "Seviper",   73 },
    { "Barboach",  "Barboach",  50 },
};

#endif /* TOY_DECK_73_H */
