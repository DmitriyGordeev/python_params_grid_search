import os

os.system("mkdir -p ~/edge-logs/")

for i in range(1, 50):
    print "[edge_configs.py]: config = edge-configs/YM800-" + str(i)
    os.system("python carle.zip -d 20190101-20200424 -c edge-configs/YM800-" + str(i) + ".xml -e \"6E=0q\"")
    os.system("mv logs edge-logs/logs-" + str(i))
    os.system("mkdir logs")