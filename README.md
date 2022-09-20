## DQ-Breeder
Set of tools for visualizing and analyzing breed trees in Dragon Quest Monsters Joker 3 Professional

# Requirements

Python 3.10

DQMJ3 Pro Master's Guide

https://docs.google.com/spreadsheets/d/1oAOL4wj39wknnP2iIHIX3jBoVQ6iUERwiVBLu63sBxU/edit#gid=0

Openpyxl Library

https://pypi.org/project/openpyxl/

# Instructions

To use, download the Master's guide above as an xlsx file and rename it to "MasterGuide".

Make sure the guide is in the same folder as the script before running it.

# Utility Listing

pop_tree: Given a monster name and an optional location blacklist, prints a tree outlining the steps to breed it using scoutable monsters.

tree_noscout: Given a monster name, calls pop_tree with the blacklist updated to contain the input monster's location.

source: Given a monster name, shows where to obtain it. If it cannot be scouted, outputs a list of all scoutable monsters required to breed it.

source_noscout: similar to source, but checks assuming the input monster name cannot be scouted

creq: Given a list of monsters from source or similar, makes a dictionary showing each one and how many are required.

merge: Combines two creq dictionaries together.

test_all: Tries to run the source function on each monster name in the sheet and reports whether source ran successfully or not. Can optionally use a no scout flag that checks source assuming it cannot be scouted.

find_breed_typos: Checks breed components against the list of monster names, reporting errors to typos.txt.

repair: Attempts to auto fix some guide issues using difflib.

# Functionality Statistics (Unmodified Guide, Tested 9/20/2022)

Without repair calls, noscout flag off: 543/722 monsters can be bred

Without repair calls, noscout flag on: 342/722 monsters can be bred

With repair calls, noscout flag off: 719/722 monsters can be bred

With repair calls, noscout flag on: 611/722 monsters can be bred
