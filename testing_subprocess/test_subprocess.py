import os, time, sys, subprocess

print "starting process 1"

FNULL = open(os.devnull, 'w')

subprocess.Popen(['python',
                  "/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/testing_subprocess/exe.py",
                  '-n', "1"], close_fds=True, stdout=FNULL, stderr=subprocess.STDOUT)

print "starting process 2"

subprocess.Popen(['python',
                  "/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/testing_subprocess/exe.py",
                  '-n', "2"], close_fds=True, stdout=FNULL, stderr=subprocess.STDOUT)

print "starting process 3"

p = subprocess.Popen(['python',
                  "/home/dima/Projects/PyCharmProjects/CarleGeneral/Grid/testing_subprocess/exe.py",
                  '-n', "3"], close_fds=True, stdout=FNULL, stderr=subprocess.STDOUT)

while p.poll() is None:
    print "p3 [" + str(p.pid) + "] is running"

