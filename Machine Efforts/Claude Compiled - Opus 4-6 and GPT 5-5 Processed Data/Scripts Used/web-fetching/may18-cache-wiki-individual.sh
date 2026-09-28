#!/bin/bash
# Cache all 73 individual NASA astronaut Wikipedia pages as HTML files.
# Source: Session 8ed732b6 (May 18-20, 2026), line 3989.
# Retries blocked pages with a browser user-agent and 0.5s delay between requests.
# Pages are stored in Cached Pages/wiki-individual/{name}/{name}.html

BASE="./Claude Compiled Data/Cached Pages"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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

ok=0; retried=0; failed=0
while IFS='|' read -r name url; do
    html="$BASE/wiki-individual/$name/$name.html"
    size=$(wc -c < "$html" 2>/dev/null | tr -d ' ')
    if [ "$size" -gt 10000 ]; then
        ok=$((ok+1))
        continue
    fi
    curl -sL -A "$UA" -o "$html" "$url"
    newsize=$(wc -c < "$html" | tr -d ' ')
    if [ "$newsize" -gt 10000 ]; then
        retried=$((retried+1))
    else
        echo "FAILED: $name ($newsize bytes)"
        failed=$((failed+1))
    fi
    sleep 0.5
done < [TMPDIR]/wiki-urls.txt
echo ""
echo "Individual: $ok already good, $retried retried OK, $failed failed"
