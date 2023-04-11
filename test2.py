import itertools

my_list = ["Pop","Chill","R&B","EDM"]

for a, b in itertools.combinations(my_list, 2):
    print(a, b)