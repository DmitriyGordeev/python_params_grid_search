import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name',
                    nargs=None,
                    required=True,
                    help='Name')

args, common = parser.parse_known_args()

f = open("exe." + args.name + ".txt", "w")
for i in range(0, 10000):
    for j in range(0, 1000):
        print(args.name, ":", i * j)
        f.write(args.name + ":" + str(i * j) + "\n")
f.close()
