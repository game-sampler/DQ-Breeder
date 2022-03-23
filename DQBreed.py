import openpyxl, difflib
guide = openpyxl.load_workbook(filename='MasterGuide.xlsx', data_only=True)

#gets a list of every monster name on the sheet
mons = guide["Monsters "]
mon_names = [mons['B'+str(i)].value for i in range(3, 725)]
mon_lower = [i.lower().strip() for i in mon_names]

#gets a list of every breed combination on the sheet
breeds = [mons['L'+str(i)].value for i in range(3, 725)]
breed_lower = [(i.lower().strip() if i != None else None) for i in breeds]

#compacts a list of monster names into its parts
def flatten_subs(l):
    flat = []
    for s in l:
        try:
            for i in s:
                if type(s) != list:
                    continue
                else:
                    flat.append(i)
            if type(s) == list:
                continue
            else:
                flat.append(s)
        except:
            flat.append(s)
    return flat

"""returns a formatted list of monsters that breed into the monster at position index in mon_names"""
def breed_format(index):
    try:
        init = [j.replace('.', '').replace('(', '').replace(')', '').replace(" don't do this it's a waste", '').replace(" generic recipe, don't waste break monsters", '').replace(" generic reciper, don't wast break monsters", '').replace('super light', '(super light)').strip() for j in [i.strip() for i in breed_lower[index].replace(' - ', ' + ').replace(' x ', ' + ').split('+')]]
        return init
    except IndexError:
        return "Invalid monster!"
    except AttributeError:
        return [None]

#same as breed_format but uses a monster name instead of an index
def breed_by_name(name):
    return breed_format(mon_lower.index(name.lower()))

#gets the location data of a monster by name
def loc_by_name(name):
    return mons['O'+str(mon_lower.index(name.lower())+3)].value

"""returns a list of base monsters (that is, those that can be scouted in some way) for a given monster.
If given monster is scoutable, describes where it can be obtained."""
def source(mon, debug=False):
    return "Obtainable from %s" % loc_by_name(mon) if loc_by_name(mon) not in ['Unknown', None, 'Unkown'] else ("Unknown" if breed_by_name(mon)[0] in ['none', None] else source_hlp(breed_by_name(mon), debug))

#quick lambda to check if something is either unbreedable or can be scouted
gettable = lambda x: (loc_by_name(x) not in ['Unknown', None, 'Unkown']) or (breed_by_name(x) in [['none'], [None]])

#selects the first monster if multiple options are listed
slash_fix = lambda b: b.split('/')[0] if "/" in b else b

#applies a breed only if it is breedable or unscoutable
cond_b = lambda b: breed_by_name(b) if not gettable(b) else b

#helper function to handle recursion
def source_hlp(out, debug, num_calls=0):
    if num_calls > 25:
        raise RecursionError
    out = list(map(slash_fix, out))
    if debug:
        print(out)
    if all(gettable(x) for x in out):
        return out
    out = flatten_subs(list(map(cond_b, out)))
    return out if all(gettable(x) for x in list(map(slash_fix, out))) else source_hlp(list(map(slash_fix, out)), debug, num_calls+1)

#returns a mapping showing how many of each monster is needed from the given base monster list
creq = lambda m: "Error!" if type(m) != list else {k:x for k, x in zip(m, [m.count(i) for i in m])}

#shows the base monster list for the given monster assuming it isnt scoutable
source_noscout = lambda m, b: source_hlp(breed_by_name(m), b)

#detects invalid parts of each breed and reports them to a file
def find_breed_typos():
    for i in range(len(mon_lower)):
        words = breed_by_name(mon_lower[i])
        if words == ['none'] or words == [None] or any('/' in word for word in words) or any ('family' in word for word in words) or words == ['bring the corresponding tomes to archie logg']:
            continue
        for j in words:
            if j not in mon_lower:
                likely_str = ', probably should be %s' % difflib.get_close_matches(j, mon_lower)[0] if difflib.get_close_matches(j, mon_lower) else ''
                typo_str = "typo '%s' spotted at cell L%d%s\n" % (j, i+3, likely_str)
                with open('typos.txt', 'a') as f:
                    f.write(typo_str)
    print("All done!")

#tests all breeds for errors
def test_all(noscout=False):
    count = 3
    num_correct = 0
    for mon in mon_lower:
        try:
            if noscout:
                source_noscout(mon, False)
            else:
                source(mon)
            print("Monster %s can be bred via script %s" % (mon, ('without scouting it initially' if noscout else '')))
            num_correct += 1
        except ValueError as e:
            print("Error occured at cell L%d with monster %s: %s of valid monsters" % (count, mon, str(e)))
        except RecursionError:
            print("Possible infinite loop at cell L%d with breed recipe of %s" % (count, mon))
        except TypeError:
            print("None-based issue with monster %s" % mon)
        count += 1
    print("\n%d out of %d monsters possible to breed with script %s" % (num_correct, count-3, ('without scouting them initially' if noscout else '')))

#merges two breed mappings together
merge = lambda a, b: {key: (a[key] + b.get(key, 0) if key in a else b[key]) for key in list(set(list(a.keys())+list(b.keys())))}

#handy stackoverflow tree code

class treeNode:
    def __init__(self,data):
        self.data = data
        self.children = []

class Tree:
    def __init__(self,root:treeNode):
        self.root = root
        self.depth = 0

def printTree(tree):
    x = tree.root
    def hlp(child, indent=""):
        label,children = child.data, child.children
        print(indent[:-3] + "|_ "*bool(indent) + str(label))
        for more,grandchild in enumerate(children,1-len(children)):
            childIndent = "|  " if more else "   "
            hlp(grandchild,indent+childIndent)
    hlp(x)

#presents a breed in tree form, with support for a blacklist to prevent breeds from showing monsters scoutable in areas in it
def pop_tree(mon, blacklist = []):
    tree_tgt = Tree(treeNode(mon))

    def pop_hlp(root):
        if gettable(root.data) and loc_by_name(root.data) not in blacklist:
            return
        else:
            root.children = [treeNode(i) for i in list(map(slash_fix, breed_by_name(root.data)))]
            for j in root.children:
                pop_hlp(j)

    pop_hlp(tree_tgt.root)
    printTree(tree_tgt)

#presents a breed in tree form assuming the monster's scout location is not allowed
tree_noscout = lambda x: pop_tree(x, [loc_by_name(x)])

#applies suggested typo fixes with some edge cases
def repair():
    #list of edge cases that the program can automate
    edge_cases = {
        "mirai god beast" : "incarni beast",
        "gran dragon": "golden orochi",
        "dragon family": "small fry",
        "material family": "hunter mech",
        "beast family": "bullfinch",
        "nature family": "cruelcumber",
        "devil family": "lump wizard",
        "nimzo": "grandmaster nimzo",
        "zoma": "archfiend zoma",
        "psaro": "psaro the manslayer",
        "mortamor": "demonlord mortamor",
        "liquid metal king slime": "liquid metal slime king"
    }
    #goes through each breed in list format, and if its not unbreedable or a tome monster, continues on and checks for errors against mon_lower
    for i in range(len(breed_lower)):
        for j in breed_format(i):
            if j not in mon_lower and j not in ['none', None, 'bring the corresponding tomes to archie logg']:
                #checks if error is an edge case
                if j in edge_cases:
                    breed_lower[i] = breed_lower[i].replace(j, edge_cases[j])
                    continue
                #checks if the error is a breed with multiple options on one end
                elif "/" in j:
                    breed_lower[i] = breed_lower[i].replace(j, j.split('/')[0])
                    continue
                #checks for striking sabercub/cat edge case manually since it can be either depending on result monster's rank
                elif "striking saber" in j:
                    if mons['C'+str(i+3)].value in ['F', 'E', 'D']:
                        breed_lower[i] = breed_lower[i].replace(j, "striking sabercub")
                    else:
                        breed_lower[i] = breed_lower[i].replace(j, "striking sabercat")
                    continue
                #finally, replaces error with closest valid monster name
                try:
                    breed_lower[i] = breed_lower[i].replace(j, difflib.get_close_matches(j, mon_lower)[0])
                #logs failures as prints for easy debugging
                except IndexError:
                    print(j)
    #some individual breed optimizations to prevent infinites and trim down some trees
    breed_lower[53] = breed_lower[53].replace('zoma', 'archfiend zoma')
    breed_lower[273] = 'slime + dracky'
    breed_lower[274] = 'slime + slime'
    breed_lower[141] = breed_lower[141].replace('rhapthorne', 'dark god rhapthorne')
    breed_lower[178] = 'metal slime + funky feta'
    breed_lower[157] = 'orc + suckling ocker'
    breed_lower[91] = 'ultraviolent ray + slime'
    breed_lower[54] = 'egg-en-ciel + disasterking'
    breed_lower[680] = breed_lower[680].replace('rhapthorne', 'dark god rhapthorne')
    #fixes some errors from the auto replacer
    for i in range(len(breed_lower)):
        if breed_lower[i] not in [None, [None]]:
            breed_lower[i] = breed_lower[i].replace('special browniee', 'special brownie').replace('plated goretoisese', 'plated goretoise').replace('striking sabercubcub', 'striking sabercub')
    return "Repaired!"
