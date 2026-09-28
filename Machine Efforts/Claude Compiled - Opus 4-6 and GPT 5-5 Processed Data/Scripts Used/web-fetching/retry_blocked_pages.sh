#!/bin/bash
#
# Retry all blocked Wikipedia pages with proper User-Agent header.
#
# Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
# Timestamps: 2026-05-20T09:21:28Z (line 3988) and 2026-05-20T09:23:54Z (line 3993)
# What it does: After initial fetch, Wikipedia returned 2173-byte block pages for all
#               requests (missing User-Agent). This script:
#   1. Writes URL maps to temp files (zsh-compatible, no bash associative arrays)
#   2. Checks each HTML file size; if < 10KB, retries with User-Agent header
#   3. Adds 0.5s delay between retries to be polite
#   4. Covers individual astronauts, group pages, and all military program pages
#
# Run from: anywhere (uses absolute paths)

BASE="./Claude Compiled Data/Cached Pages"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# === Individual astronaut URL map ===
cat > [TMPDIR]/wiki-urls.txt << 'URLS'
aldrin-buzz|https://en.wikipedia.org/wiki/Buzz_Aldrin
allen-joseph|https://en.wikipedia.org/wiki/Joseph_P._Allen
anders-william|https://en.wikipedia.org/wiki/William_Anders
armstrong-neil|https://en.wikipedia.org/wiki/Neil_Armstrong
bassett-charles|https://en.wikipedia.org/wiki/Charles_Bassett
bean-alan|https://en.wikipedia.org/wiki/Alan_Bean
bobko-karol|https://en.wikipedia.org/wiki/Karol_J._Bobko
borman-frank|https://en.wikipedia.org/wiki/Frank_Borman
brand-vance|https://en.wikipedia.org/wiki/Vance_Brand
bull-john|https://en.wikipedia.org/wiki/John_S._Bull
carpenter-scott|https://en.wikipedia.org/wiki/Scott_Carpenter
carr-gerald|https://en.wikipedia.org/wiki/Gerald_P._Carr
cernan-eugene|https://en.wikipedia.org/wiki/Eugene_Cernan
chaffee-roger|https://en.wikipedia.org/wiki/Roger_B._Chaffee
chapman-philip|https://en.wikipedia.org/wiki/Philip_K._Chapman
collins-michael|https://en.wikipedia.org/wiki/Michael_Collins_(astronaut)
conrad-pete|https://en.wikipedia.org/wiki/Pete_Conrad
cooper-gordon|https://en.wikipedia.org/wiki/Gordon_Cooper
crippen-robert|https://en.wikipedia.org/wiki/Robert_Crippen
cunningham-walter|https://en.wikipedia.org/wiki/Walter_Cunningham
duke-charles|https://en.wikipedia.org/wiki/Charles_Duke
eisele-donn|https://en.wikipedia.org/wiki/Donn_Eisele
england-anthony|https://en.wikipedia.org/wiki/Anthony_W._England
engle-joseph|https://en.wikipedia.org/wiki/Joe_Engle
evans-ronald|https://en.wikipedia.org/wiki/Ronald_Evans_(astronaut)
freeman-theodore|https://en.wikipedia.org/wiki/Theodore_Freeman
fullerton-gordon|https://en.wikipedia.org/wiki/C._Gordon_Fullerton
garriott-owen|https://en.wikipedia.org/wiki/Owen_Garriott
gibson-edward|https://en.wikipedia.org/wiki/Edward_Gibson_(astronaut)
givens-edward|https://en.wikipedia.org/wiki/Edward_Givens
glenn-john|https://en.wikipedia.org/wiki/John_Glenn
gordon-richard|https://en.wikipedia.org/wiki/Richard_F._Gordon_Jr.
graveline-duane|https://en.wikipedia.org/wiki/Duane_Graveline
grissom-gus|https://en.wikipedia.org/wiki/Gus_Grissom
haise-fred|https://en.wikipedia.org/wiki/Fred_Haise
hartsfield-henry|https://en.wikipedia.org/wiki/Henry_Hartsfield
henize-karl|https://en.wikipedia.org/wiki/Karl_Henize
holmquest-donald|https://en.wikipedia.org/wiki/Donald_Holmquest
irwin-james|https://en.wikipedia.org/wiki/James_Irwin
kerwin-joseph|https://en.wikipedia.org/wiki/Joseph_Kerwin
lenoir-william|https://en.wikipedia.org/wiki/William_B._Lenoir
lind-don|https://en.wikipedia.org/wiki/Don_Lind
llewellyn-anthony|https://en.wikipedia.org/wiki/Anthony_Llewellyn
lousma-jack|https://en.wikipedia.org/wiki/Jack_Lousma
lovell-jim|https://en.wikipedia.org/wiki/Jim_Lovell
mattingly-ken|https://en.wikipedia.org/wiki/Ken_Mattingly
mccandless-bruce|https://en.wikipedia.org/wiki/Bruce_McCandless_II
mcdivitt-james|https://en.wikipedia.org/wiki/James_McDivitt
michel-curt|https://en.wikipedia.org/wiki/F._Curtis_Michel
mitchell-edgar|https://en.wikipedia.org/wiki/Edgar_Mitchell
musgrave-story|https://en.wikipedia.org/wiki/Story_Musgrave
oleary-brian|https://en.wikipedia.org/wiki/Brian_O%27Leary
overmyer-robert|https://en.wikipedia.org/wiki/Robert_Overmyer
parker-robert|https://en.wikipedia.org/wiki/Robert_A._R._Parker
peterson-donald|https://en.wikipedia.org/wiki/Donald_H._Peterson
pogue-william|https://en.wikipedia.org/wiki/William_Pogue
roosa-stuart|https://en.wikipedia.org/wiki/Stuart_Roosa
schirra-wally|https://en.wikipedia.org/wiki/Wally_Schirra
schmitt-harrison|https://en.wikipedia.org/wiki/Harrison_Schmitt
schweickart-russell|https://en.wikipedia.org/wiki/Rusty_Schweickart
scott-david|https://en.wikipedia.org/wiki/David_Scott
see-elliot|https://en.wikipedia.org/wiki/Elliot_See
shepard-alan|https://en.wikipedia.org/wiki/Alan_Shepard
slayton-deke|https://en.wikipedia.org/wiki/Deke_Slayton
stafford-thomas|https://en.wikipedia.org/wiki/Thomas_P._Stafford
swigert-jack|https://en.wikipedia.org/wiki/Jack_Swigert
thornton-william|https://en.wikipedia.org/wiki/William_E._Thornton
truly-richard|https://en.wikipedia.org/wiki/Richard_Truly
weitz-paul|https://en.wikipedia.org/wiki/Paul_Weitz
white-ed|https://en.wikipedia.org/wiki/Ed_White_(astronaut)
williams-clifton|https://en.wikipedia.org/wiki/Clifton_Williams
worden-alfred|https://en.wikipedia.org/wiki/Al_Worden
young-john|https://en.wikipedia.org/wiki/John_Young_(astronaut)
URLS

echo "=== INDIVIDUAL ASTRONAUTS ==="
ok=0; retried=0; failed=0
while IFS='|' read -r name url; do
    html="$BASE/wiki-individual/$name/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        ok=$((ok+1))
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    if [ "$newsize" -gt 10000 ]; then
        echo "Retried OK: $name ($newsize bytes)"
        retried=$((retried+1))
    else
        echo "STILL BLOCKED: $name ($newsize bytes)"
        failed=$((failed+1))
    fi
    sleep 0.5
done < [TMPDIR]/wiki-urls.txt
echo "Individual: $ok already OK, $retried retried, $failed still blocked"

# === Group pages ===
cat > [TMPDIR]/wiki-group-urls.txt << 'URLS'
wiki-apollo-astronauts|https://en.wikipedia.org/wiki/List_of_Apollo_astronauts
wiki-astronauts-by-selection|https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection
wiki-group-6-scientists-1967|https://en.wikipedia.org/wiki/NASA_Astronaut_Group_6
wiki-group-7-mol-transfer|https://en.wikipedia.org/wiki/NASA_Astronaut_Group_7
URLS

echo ""
echo "=== GROUP PAGES ==="
while IFS='|' read -r name url; do
    html="$BASE/$name/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        echo "OK: $name ($size bytes)"
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    echo "Retried: $name ($newsize bytes)"
    sleep 0.5
done < [TMPDIR]/wiki-group-urls.txt

# === Military X-15 ===
cat > [TMPDIR]/wiki-mil-urls.txt << 'URLS'
x-15/wiki-joe-engle-x15|https://en.wikipedia.org/wiki/Joe_Engle
x-15/wiki-robert-white|https://en.wikipedia.org/wiki/Robert_Michael_White
x-15/wiki-robert-rushworth|https://en.wikipedia.org/wiki/Robert_A._Rushworth
x-15/wiki-joseph-walker|https://en.wikipedia.org/wiki/Joseph_A._Walker
x-15/wiki-neil-armstrong-x15|https://en.wikipedia.org/wiki/Neil_Armstrong
x-15/wiki-north-american-x-15|https://en.wikipedia.org/wiki/North_American_X-15
x-15/wiki-william-dana|https://en.wikipedia.org/wiki/William_H._Dana
x-15/wiki-william-knight|https://en.wikipedia.org/wiki/William_J._Knight
x-15/wiki-milton-thompson|https://en.wikipedia.org/wiki/Milton_Orville_Thompson
x-15/wiki-list-of-x15-flights|https://en.wikipedia.org/wiki/List_of_X-15_flights
x-15/wiki-michael-adams|https://en.wikipedia.org/wiki/Michael_J._Adams
x-15/wiki-scott-crossfield|https://en.wikipedia.org/wiki/Albert_Scott_Crossfield
x-15/wiki-john-mckay|https://en.wikipedia.org/wiki/John_B._McKay
x-15/wiki-forrest-petersen|https://en.wikipedia.org/wiki/Forrest_S._Petersen
URLS

echo ""
echo "=== X-15 ==="
while IFS='|' read -r path url; do
    name=$(basename "$path")
    html="$BASE/military-programs/$path/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        echo "OK: $name ($size bytes)"
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    echo "Retried: $name ($newsize bytes)"
    sleep 0.5
done < [TMPDIR]/wiki-mil-urls.txt

# === Dyna-Soar ===
cat > [TMPDIR]/wiki-ds-urls.txt << 'URLS'
dyna-soar/wiki-albert-crews|https://en.wikipedia.org/wiki/Albert_Crews
dyna-soar/wiki-boeing-x20-dyna-soar|https://en.wikipedia.org/wiki/Boeing_X-20_Dyna-Soar
dyna-soar/wiki-henry-gordon|https://en.wikipedia.org/wiki/Henry_C._Gordon
dyna-soar/wiki-russell-rogers|https://en.wikipedia.org/wiki/Russell_L._Rogers
dyna-soar/wiki-james-wood|https://en.wikipedia.org/wiki/James_W._Wood
dyna-soar/wiki-milton-thompson|https://en.wikipedia.org/wiki/Milton_Orville_Thompson
dyna-soar/wiki-william-dana|https://en.wikipedia.org/wiki/William_H._Dana
dyna-soar/wiki-william-knight|https://en.wikipedia.org/wiki/William_J._Knight
URLS

echo ""
echo "=== DYNA-SOAR ==="
while IFS='|' read -r path url; do
    name=$(basename "$path")
    dir="$BASE/military-programs/$path"
    mkdir -p "$dir"
    html="$dir/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        echo "OK: $name ($size bytes)"
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    echo "Fetched: $name ($newsize bytes)"
    sleep 0.5
done < [TMPDIR]/wiki-ds-urls.txt

# === MOL ===
cat > [TMPDIR]/wiki-mol-urls.txt << 'URLS'
mol/wiki-mol-program|https://en.wikipedia.org/wiki/Manned_Orbiting_Laboratory
mol/wiki-james-abrahamson|https://en.wikipedia.org/wiki/James_Abrahamson
mol/wiki-richard-lawyer|https://en.wikipedia.org/wiki/Richard_Lawyer
mol/wiki-robert-lawrence|https://en.wikipedia.org/wiki/Robert_Henry_Lawrence_Jr.
mol/wiki-john-finley|https://en.wikipedia.org/wiki/John_L._Finley
mol/wiki-james-taylor|https://en.wikipedia.org/wiki/James_M._Taylor_(astronaut)
mol/wiki-lachlan-macleay|https://en.wikipedia.org/wiki/Lachlan_Macleay
mol/wiki-francis-neubeck|https://en.wikipedia.org/wiki/Francis_Neubeck
mol/wiki-robert-herres|https://en.wikipedia.org/wiki/Robert_Herres
mol/wiki-albert-crews|https://en.wikipedia.org/wiki/Albert_Crews
mol/wiki-michael-adams|https://en.wikipedia.org/wiki/Michael_J._Adams
URLS

echo ""
echo "=== MOL ==="
while IFS='|' read -r path url; do
    name=$(basename "$path")
    dir="$BASE/military-programs/$path"
    mkdir -p "$dir"
    html="$dir/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        echo "OK: $name ($size bytes)"
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    echo "Fetched: $name ($newsize bytes)"
    sleep 0.5
done < [TMPDIR]/wiki-mol-urls.txt

echo ""
echo "=== ALL RETRIES COMPLETE ==="
