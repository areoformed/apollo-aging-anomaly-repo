#!/bin/bash
# Cache Wikipedia group pages and military program pages (X-15, Dyna-Soar, MOL).
# Source: Session 8ed732b6 (May 18-20, 2026), line 3994.
# Creates directory structure and fetches HTML with browser user-agent.

BASE="./Claude Compiled Data/Cached Pages"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Group pages
echo "=== GROUP PAGES ==="
for entry in \
    "wiki-apollo-astronauts|https://en.wikipedia.org/wiki/List_of_Apollo_astronauts" \
    "wiki-astronauts-by-selection|https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection" \
    "wiki-group-6-scientists-1967|https://en.wikipedia.org/wiki/NASA_Astronaut_Group_6" \
    "wiki-group-7-mol-transfer|https://en.wikipedia.org/wiki/NASA_Astronaut_Group_7"
do
    IFS='|' read -r name url <<< "$entry"
    html="$BASE/$name/$name.html"
    mkdir -p "$(dirname "$html")"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "${size:-0}" -gt 10000 ]; then
        echo "OK: $name ($size bytes)"
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    echo "Fetched: $name ($(wc -c < "$html" | tr -d ' ') bytes)"
    sleep 0.5
done

# X-15 pilots
echo ""
echo "=== X-15 ==="
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
    echo "Fetched: $name ($(wc -c < "$html" | tr -d ' ') bytes)"
    sleep 0.5
done < [TMPDIR]/wiki-mil-urls.txt

# Dyna-Soar pilots
echo ""
echo "=== DYNA-SOAR ==="
for entry in \
    "dyna-soar/wiki-albert-crews|https://en.wikipedia.org/wiki/Albert_Crews" \
    "dyna-soar/wiki-boeing-x20-dyna-soar|https://en.wikipedia.org/wiki/Boeing_X-20_Dyna-Soar" \
    "dyna-soar/wiki-henry-gordon|https://en.wikipedia.org/wiki/Henry_C._Gordon" \
    "dyna-soar/wiki-russell-rogers|https://en.wikipedia.org/wiki/Russell_L._Rogers" \
    "dyna-soar/wiki-james-wood|https://en.wikipedia.org/wiki/James_W._Wood" \
    "dyna-soar/wiki-milton-thompson|https://en.wikipedia.org/wiki/Milton_Orville_Thompson" \
    "dyna-soar/wiki-william-dana|https://en.wikipedia.org/wiki/William_H._Dana" \
    "dyna-soar/wiki-william-knight|https://en.wikipedia.org/wiki/William_J._Knight"
do
    IFS='|' read -r path url <<< "$entry"
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
    echo "Fetched: $name ($(wc -c < "$html" | tr -d ' ') bytes)"
    sleep 0.5
done

# MOL astronauts
echo ""
echo "=== MOL ==="
for entry in \
    "mol/wiki-mol-program|https://en.wikipedia.org/wiki/Manned_Orbiting_Laboratory" \
    "mol/wiki-james-abrahamson|https://en.wikipedia.org/wiki/James_Abrahamson" \
    "mol/wiki-richard-lawyer|https://en.wikipedia.org/wiki/Richard_Lawyer" \
    "mol/wiki-robert-lawrence|https://en.wikipedia.org/wiki/Robert_Henry_Lawrence_Jr." \
    "mol/wiki-john-finley|https://en.wikipedia.org/wiki/John_L._Finley" \
    "mol/wiki-james-taylor|https://en.wikipedia.org/wiki/James_M._Taylor_(astronaut)" \
    "mol/wiki-lachlan-macleay|https://en.wikipedia.org/wiki/Lachlan_Macleay" \
    "mol/wiki-francis-neubeck|https://en.wikipedia.org/wiki/Francis_Neubeck" \
    "mol/wiki-robert-herres|https://en.wikipedia.org/wiki/Robert_Herres" \
    "mol/wiki-albert-crews|https://en.wikipedia.org/wiki/Albert_Crews" \
    "mol/wiki-michael-adams|https://en.wikipedia.org/wiki/Michael_J._Adams"
do
    IFS='|' read -r path url <<< "$entry"
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
    if [ "$newsize" -lt 5000 ]; then
        echo "POSSIBLY MISSING: $name ($newsize bytes)"
    else
        echo "Fetched: $name ($newsize bytes)"
    fi
    sleep 0.5
done
