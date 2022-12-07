# Communicate

Creates interactive GUI for tackling problem of entering letters when texting/typing infeasible and need bigger display.

This project is for a very real problem of limited communication with immobile people who may only be anle to use their arms to point or fingers 1-5.

To communicate efficiently, there are 3 methods:
    1. Point - In real life put 5 letters on each page, skim through pages until patient points to letter on page or finger up for index of letter on page.
    2. Grid - Get full view of grid 5x5 where patient uses one finger to choose row then next to choose column corresponding to letter in it.
    3. GridPoint - Patient can't use fingers so looks at grid and picks row by selecting 1-5 on paper, then within row 1-5 for letter

Efficiency gains of these methods are stark compared to verbal saying each letter (Is it A,B,C,D...) for every letter.
    1. (M letters, N in alphabet) Computational Complexity formerly M*N since do N letters M times, but now with grid/point it is on order of M*N^1/2 since square grid and indexing reduces space by square factor.
    2. Procedural complexity reduced as M iterations of N alphabet letters, average N/2 attempts per M letter yields M * 26/2 = 13M for M letter word, now really on order O(1) for lookup 1-5 and 2 lookups needed so 2M, so 13M->2M is 6.5x speedup
    3. Even more efficiencies in here using language corpus since we can eliminate non existent follow on letters to constructed word and reduce/tune space of lookups as we build word so lookup itself shortened 1-5, to 1-3 etc. as less letters become possible.
    4. Even can order letters in grid by common usage so lookup of common letters in (1,1) topleft corner of grid more often, giving more speedup and localization to used letters in setup.

Build Out Interfactive UI for Communication, first with CLI but for atual Patient Usage/visibility/ precision of pointing (if no fingers) we make GUI. Can construct full sentences.

Use grid of letters, then option to reduce grid with only letters of valid words from substring or disable letters.

Also use nltk word library for most common english words and letters given name substring thus far, and can sort letters by common occurance and filter out invalid letters to make word if so choose. Also allow entry of autocomplete siggestions.

## Installation
PreReqs: install python3, python3-pip, python3-tk, python3-venv. pip install nltk.