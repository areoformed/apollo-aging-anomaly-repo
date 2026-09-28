#!/bin/bash
#
# Fetch all Wikipedia HTML pages for the Apollo Aging Anomaly dataset.
#
# Source: Conversation 8ed732b6-ca07-4e46-a666-94fc1f98b7f8
# Timestamps: 2026-05-20T09:18:30Z through 2026-05-20T09:19:18Z (lines 3944-3952)
# What it does: Downloads raw Wikipedia HTML for all 73 core astronauts,
#               4 group/list pages, and ~28 military program pages.
#               Organized into 6 parallel batches to avoid rate limiting.
#
# NOTE: Initial curl calls were blocked by Wikipedia (2173-byte response).
#       A retry script with User-Agent header was needed (see retry_blocked_pages.sh).
#
# Run from: anywhere (uses absolute paths)

BASE="./Claude Compiled Data/Cached Pages"

echo "=== Batch 1: Individual astronauts A-C (15 pages) ==="
curl -sL -o "$BASE/wiki-individual/aldrin-buzz/aldrin-buzz.html" "https://en.wikipedia.org/wiki/Buzz_Aldrin" &
curl -sL -o "$BASE/wiki-individual/allen-joseph/allen-joseph.html" "https://en.wikipedia.org/wiki/Joseph_P._Allen" &
curl -sL -o "$BASE/wiki-individual/anders-william/anders-william.html" "https://en.wikipedia.org/wiki/William_Anders" &
curl -sL -o "$BASE/wiki-individual/armstrong-neil/armstrong-neil.html" "https://en.wikipedia.org/wiki/Neil_Armstrong" &
curl -sL -o "$BASE/wiki-individual/bassett-charles/bassett-charles.html" "https://en.wikipedia.org/wiki/Charles_Bassett" &
curl -sL -o "$BASE/wiki-individual/bean-alan/bean-alan.html" "https://en.wikipedia.org/wiki/Alan_Bean" &
curl -sL -o "$BASE/wiki-individual/bobko-karol/bobko-karol.html" "https://en.wikipedia.org/wiki/Karol_J._Bobko" &
curl -sL -o "$BASE/wiki-individual/borman-frank/borman-frank.html" "https://en.wikipedia.org/wiki/Frank_Borman" &
curl -sL -o "$BASE/wiki-individual/brand-vance/brand-vance.html" "https://en.wikipedia.org/wiki/Vance_Brand" &
curl -sL -o "$BASE/wiki-individual/bull-john/bull-john.html" "https://en.wikipedia.org/wiki/John_Bull_(astronaut)" &
curl -sL -o "$BASE/wiki-individual/carpenter-scott/carpenter-scott.html" "https://en.wikipedia.org/wiki/Scott_Carpenter" &
curl -sL -o "$BASE/wiki-individual/carr-gerald/carr-gerald.html" "https://en.wikipedia.org/wiki/Gerald_P._Carr" &
curl -sL -o "$BASE/wiki-individual/cernan-eugene/cernan-eugene.html" "https://en.wikipedia.org/wiki/Eugene_Cernan" &
curl -sL -o "$BASE/wiki-individual/chaffee-roger/chaffee-roger.html" "https://en.wikipedia.org/wiki/Roger_B._Chaffee" &
curl -sL -o "$BASE/wiki-individual/chapman-philip/chapman-philip.html" "https://en.wikipedia.org/wiki/Philip_K._Chapman" &
wait
echo "Batch 1 done"

echo "=== Batch 2: Individual astronauts C-G (15 pages) ==="
curl -sL -o "$BASE/wiki-individual/collins-michael/collins-michael.html" "https://en.wikipedia.org/wiki/Michael_Collins_(astronaut)" &
curl -sL -o "$BASE/wiki-individual/conrad-pete/conrad-pete.html" "https://en.wikipedia.org/wiki/Pete_Conrad" &
curl -sL -o "$BASE/wiki-individual/cooper-gordon/cooper-gordon.html" "https://en.wikipedia.org/wiki/Gordon_Cooper" &
curl -sL -o "$BASE/wiki-individual/crippen-robert/crippen-robert.html" "https://en.wikipedia.org/wiki/Robert_Crippen" &
curl -sL -o "$BASE/wiki-individual/cunningham-walter/cunningham-walter.html" "https://en.wikipedia.org/wiki/Walter_Cunningham" &
curl -sL -o "$BASE/wiki-individual/duke-charles/duke-charles.html" "https://en.wikipedia.org/wiki/Charles_Duke" &
curl -sL -o "$BASE/wiki-individual/eisele-donn/eisele-donn.html" "https://en.wikipedia.org/wiki/Donn_Eisele" &
curl -sL -o "$BASE/wiki-individual/england-anthony/england-anthony.html" "https://en.wikipedia.org/wiki/Anthony_W._England" &
curl -sL -o "$BASE/wiki-individual/engle-joseph/engle-joseph.html" "https://en.wikipedia.org/wiki/Joe_Engle" &
curl -sL -o "$BASE/wiki-individual/evans-ronald/evans-ronald.html" "https://en.wikipedia.org/wiki/Ronald_Evans_(astronaut)" &
curl -sL -o "$BASE/wiki-individual/freeman-theodore/freeman-theodore.html" "https://en.wikipedia.org/wiki/Theodore_Freeman" &
curl -sL -o "$BASE/wiki-individual/fullerton-gordon/fullerton-gordon.html" "https://en.wikipedia.org/wiki/C._Gordon_Fullerton" &
curl -sL -o "$BASE/wiki-individual/garriott-owen/garriott-owen.html" "https://en.wikipedia.org/wiki/Owen_Garriott" &
curl -sL -o "$BASE/wiki-individual/gibson-edward/gibson-edward.html" "https://en.wikipedia.org/wiki/Edward_Gibson_(astronaut)" &
curl -sL -o "$BASE/wiki-individual/givens-edward/givens-edward.html" "https://en.wikipedia.org/wiki/Edward_Givens" &
wait
echo "Batch 2 done"

echo "=== Batch 3: Individual astronauts G-L (15 pages) ==="
curl -sL -o "$BASE/wiki-individual/glenn-john/glenn-john.html" "https://en.wikipedia.org/wiki/John_Glenn" &
curl -sL -o "$BASE/wiki-individual/gordon-richard/gordon-richard.html" "https://en.wikipedia.org/wiki/Richard_F._Gordon_Jr." &
curl -sL -o "$BASE/wiki-individual/graveline-duane/graveline-duane.html" "https://en.wikipedia.org/wiki/Duane_Graveline" &
curl -sL -o "$BASE/wiki-individual/grissom-gus/grissom-gus.html" "https://en.wikipedia.org/wiki/Gus_Grissom" &
curl -sL -o "$BASE/wiki-individual/haise-fred/haise-fred.html" "https://en.wikipedia.org/wiki/Fred_Haise" &
curl -sL -o "$BASE/wiki-individual/hartsfield-henry/hartsfield-henry.html" "https://en.wikipedia.org/wiki/Henry_Hartsfield" &
curl -sL -o "$BASE/wiki-individual/henize-karl/henize-karl.html" "https://en.wikipedia.org/wiki/Karl_Henize" &
curl -sL -o "$BASE/wiki-individual/holmquest-donald/holmquest-donald.html" "https://en.wikipedia.org/wiki/Donald_Holmquest" &
curl -sL -o "$BASE/wiki-individual/irwin-james/irwin-james.html" "https://en.wikipedia.org/wiki/James_Irwin" &
curl -sL -o "$BASE/wiki-individual/kerwin-joseph/kerwin-joseph.html" "https://en.wikipedia.org/wiki/Joseph_Kerwin" &
curl -sL -o "$BASE/wiki-individual/lenoir-william/lenoir-william.html" "https://en.wikipedia.org/wiki/William_B._Lenoir" &
curl -sL -o "$BASE/wiki-individual/lind-don/lind-don.html" "https://en.wikipedia.org/wiki/Don_Lind" &
curl -sL -o "$BASE/wiki-individual/llewellyn-anthony/llewellyn-anthony.html" "https://en.wikipedia.org/wiki/Anthony_Llewellyn" &
curl -sL -o "$BASE/wiki-individual/lousma-jack/lousma-jack.html" "https://en.wikipedia.org/wiki/Jack_Lousma" &
curl -sL -o "$BASE/wiki-individual/lovell-jim/lovell-jim.html" "https://en.wikipedia.org/wiki/Jim_Lovell" &
wait
echo "Batch 3 done"

echo "=== Batch 4: Individual astronauts M-S (15 pages) ==="
curl -sL -o "$BASE/wiki-individual/mattingly-ken/mattingly-ken.html" "https://en.wikipedia.org/wiki/Ken_Mattingly" &
curl -sL -o "$BASE/wiki-individual/mccandless-bruce/mccandless-bruce.html" "https://en.wikipedia.org/wiki/Bruce_McCandless_II" &
curl -sL -o "$BASE/wiki-individual/mcdivitt-james/mcdivitt-james.html" "https://en.wikipedia.org/wiki/James_McDivitt" &
curl -sL -o "$BASE/wiki-individual/michel-curt/michel-curt.html" "https://en.wikipedia.org/wiki/F._Curtis_Michel" &
curl -sL -o "$BASE/wiki-individual/mitchell-edgar/mitchell-edgar.html" "https://en.wikipedia.org/wiki/Edgar_Mitchell" &
curl -sL -o "$BASE/wiki-individual/musgrave-story/musgrave-story.html" "https://en.wikipedia.org/wiki/Story_Musgrave" &
curl -sL -o "$BASE/wiki-individual/oleary-brian/oleary-brian.html" "https://en.wikipedia.org/wiki/Brian_O%27Leary" &
curl -sL -o "$BASE/wiki-individual/overmyer-robert/overmyer-robert.html" "https://en.wikipedia.org/wiki/Robert_Overmyer" &
curl -sL -o "$BASE/wiki-individual/parker-robert/parker-robert.html" "https://en.wikipedia.org/wiki/Robert_A._R._Parker" &
curl -sL -o "$BASE/wiki-individual/peterson-donald/peterson-donald.html" "https://en.wikipedia.org/wiki/Donald_H._Peterson" &
curl -sL -o "$BASE/wiki-individual/pogue-william/pogue-william.html" "https://en.wikipedia.org/wiki/William_Pogue" &
curl -sL -o "$BASE/wiki-individual/roosa-stuart/roosa-stuart.html" "https://en.wikipedia.org/wiki/Stuart_Roosa" &
curl -sL -o "$BASE/wiki-individual/schirra-wally/schirra-wally.html" "https://en.wikipedia.org/wiki/Wally_Schirra" &
curl -sL -o "$BASE/wiki-individual/schmitt-harrison/schmitt-harrison.html" "https://en.wikipedia.org/wiki/Harrison_Schmitt" &
curl -sL -o "$BASE/wiki-individual/schweickart-russell/schweickart-russell.html" "https://en.wikipedia.org/wiki/Rusty_Schweickart" &
wait
echo "Batch 4 done"

echo "=== Batch 5: Individual astronauts S-Y + group pages (17 pages) ==="
curl -sL -o "$BASE/wiki-individual/scott-david/scott-david.html" "https://en.wikipedia.org/wiki/David_Scott" &
curl -sL -o "$BASE/wiki-individual/see-elliot/see-elliot.html" "https://en.wikipedia.org/wiki/Elliot_See" &
curl -sL -o "$BASE/wiki-individual/shepard-alan/shepard-alan.html" "https://en.wikipedia.org/wiki/Alan_Shepard" &
curl -sL -o "$BASE/wiki-individual/slayton-deke/slayton-deke.html" "https://en.wikipedia.org/wiki/Deke_Slayton" &
curl -sL -o "$BASE/wiki-individual/stafford-thomas/stafford-thomas.html" "https://en.wikipedia.org/wiki/Thomas_P._Stafford" &
curl -sL -o "$BASE/wiki-individual/swigert-jack/swigert-jack.html" "https://en.wikipedia.org/wiki/Jack_Swigert" &
curl -sL -o "$BASE/wiki-individual/thornton-william/thornton-william.html" "https://en.wikipedia.org/wiki/William_E._Thornton" &
curl -sL -o "$BASE/wiki-individual/truly-richard/truly-richard.html" "https://en.wikipedia.org/wiki/Richard_Truly" &
curl -sL -o "$BASE/wiki-individual/weitz-paul/weitz-paul.html" "https://en.wikipedia.org/wiki/Paul_Weitz" &
curl -sL -o "$BASE/wiki-individual/white-ed/white-ed.html" "https://en.wikipedia.org/wiki/Ed_White_(astronaut)" &
curl -sL -o "$BASE/wiki-individual/williams-clifton/williams-clifton.html" "https://en.wikipedia.org/wiki/Clifton_Williams" &
curl -sL -o "$BASE/wiki-individual/worden-alfred/worden-alfred.html" "https://en.wikipedia.org/wiki/Al_Worden" &
curl -sL -o "$BASE/wiki-individual/young-john/young-john.html" "https://en.wikipedia.org/wiki/John_Young_(astronaut)" &
# Group pages
curl -sL -o "$BASE/wiki-apollo-astronauts/wiki-apollo-astronauts.html" "https://en.wikipedia.org/wiki/List_of_Apollo_astronauts" &
curl -sL -o "$BASE/wiki-astronauts-by-selection/wiki-astronauts-by-selection.html" "https://en.wikipedia.org/wiki/List_of_astronauts_by_year_of_selection" &
curl -sL -o "$BASE/wiki-group-6-scientists-1967/wiki-group-6-scientists-1967.html" "https://en.wikipedia.org/wiki/NASA_Astronaut_Group_6" &
curl -sL -o "$BASE/wiki-group-7-mol-transfer/wiki-group-7-mol-transfer.html" "https://en.wikipedia.org/wiki/NASA_Astronaut_Group_7" &
wait
echo "Batch 5 done"

echo "=== Batch 6: All military programs (28 pages) ==="
# X-15
curl -sL -o "$BASE/military-programs/x-15/wiki-joe-engle-x15/wiki-joe-engle-x15.html" "https://en.wikipedia.org/wiki/Joe_Engle" &
curl -sL -o "$BASE/military-programs/x-15/wiki-robert-white/wiki-robert-white.html" "https://en.wikipedia.org/wiki/Robert_Michael_White" &
curl -sL -o "$BASE/military-programs/x-15/wiki-robert-rushworth/wiki-robert-rushworth.html" "https://en.wikipedia.org/wiki/Robert_A._Rushworth" &
curl -sL -o "$BASE/military-programs/x-15/wiki-joseph-walker/wiki-joseph-walker.html" "https://en.wikipedia.org/wiki/Joseph_A._Walker" &
curl -sL -o "$BASE/military-programs/x-15/wiki-neil-armstrong-x15/wiki-neil-armstrong-x15.html" "https://en.wikipedia.org/wiki/Neil_Armstrong" &
curl -sL -o "$BASE/military-programs/x-15/wiki-north-american-x-15/wiki-north-american-x-15.html" "https://en.wikipedia.org/wiki/North_American_X-15" &
curl -sL -o "$BASE/military-programs/x-15/wiki-william-dana/wiki-william-dana.html" "https://en.wikipedia.org/wiki/William_H._Dana" &
curl -sL -o "$BASE/military-programs/x-15/wiki-william-knight/wiki-william-knight.html" "https://en.wikipedia.org/wiki/William_J._Knight" &
curl -sL -o "$BASE/military-programs/x-15/wiki-milton-thompson/wiki-milton-thompson.html" "https://en.wikipedia.org/wiki/Milton_Orville_Thompson" &
curl -sL -o "$BASE/military-programs/x-15/wiki-list-of-x15-flights/wiki-list-of-x15-flights.html" "https://en.wikipedia.org/wiki/List_of_X-15_flights" &
curl -sL -o "$BASE/military-programs/x-15/wiki-michael-adams/wiki-michael-adams.html" "https://en.wikipedia.org/wiki/Michael_J._Adams" &
curl -sL -o "$BASE/military-programs/x-15/wiki-scott-crossfield/wiki-scott-crossfield.html" "https://en.wikipedia.org/wiki/Albert_Scott_Crossfield" &
curl -sL -o "$BASE/military-programs/x-15/wiki-john-mckay/wiki-john-mckay.html" "https://en.wikipedia.org/wiki/John_B._McKay" &
curl -sL -o "$BASE/military-programs/x-15/wiki-forrest-petersen/wiki-forrest-petersen.html" "https://en.wikipedia.org/wiki/Forrest_S._Petersen" &
# Dyna-Soar
curl -sL -o "$BASE/military-programs/dyna-soar/wiki-albert-crews/wiki-albert-crews.html" "https://en.wikipedia.org/wiki/Albert_Crews" &
curl -sL -o "$BASE/military-programs/dyna-soar/wiki-boeing-x20-dyna-soar/wiki-boeing-x20-dyna-soar.html" "https://en.wikipedia.org/wiki/Boeing_X-20_Dyna-Soar" &
curl -sL -o "$BASE/military-programs/dyna-soar/wiki-henry-gordon/wiki-henry-gordon.html" "https://en.wikipedia.org/wiki/Henry_C._Gordon" &
curl -sL -o "$BASE/military-programs/dyna-soar/wiki-russell-rogers/wiki-russell-rogers.html" "https://en.wikipedia.org/wiki/Russell_L._Rogers" &
curl -sL -o "$BASE/military-programs/dyna-soar/wiki-james-wood/wiki-james-wood.html" "https://en.wikipedia.org/wiki/James_W._Wood" &
# MOL
curl -sL -o "$BASE/military-programs/mol/wiki-mol-program/wiki-mol-program.html" "https://en.wikipedia.org/wiki/Manned_Orbiting_Laboratory" &
curl -sL -o "$BASE/military-programs/mol/wiki-james-abrahamson/wiki-james-abrahamson.html" "https://en.wikipedia.org/wiki/James_Abrahamson" &
curl -sL -o "$BASE/military-programs/mol/wiki-richard-lawyer/wiki-richard-lawyer.html" "https://en.wikipedia.org/wiki/Richard_Lawyer" &
curl -sL -o "$BASE/military-programs/mol/wiki-robert-lawrence/wiki-robert-lawrence.html" "https://en.wikipedia.org/wiki/Robert_Henry_Lawrence_Jr." &
curl -sL -o "$BASE/military-programs/mol/wiki-john-finley/wiki-john-finley.html" "https://en.wikipedia.org/wiki/John_L._Finley" &
curl -sL -o "$BASE/military-programs/mol/wiki-james-taylor/wiki-james-taylor.html" "https://en.wikipedia.org/wiki/James_M._Taylor_(astronaut)" &
curl -sL -o "$BASE/military-programs/mol/wiki-lachlan-macleay/wiki-lachlan-macleay.html" "https://en.wikipedia.org/wiki/Lachlan_Macleay" &
curl -sL -o "$BASE/military-programs/mol/wiki-francis-neubeck/wiki-francis-neubeck.html" "https://en.wikipedia.org/wiki/Francis_Neubeck" &
curl -sL -o "$BASE/military-programs/mol/wiki-robert-herres/wiki-robert-herres.html" "https://en.wikipedia.org/wiki/Robert_Herres" &
wait
echo "Batch 6 done (28 pages: 14 X-15 + 5 Dyna-Soar + 9 MOL)"

echo ""
echo "All batches complete. Check for blocked pages with verify_html_files.sh"
