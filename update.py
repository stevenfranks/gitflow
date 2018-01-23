import subprocess
import sys

print 'Updating gitflow..'
# get latest gitflow version
# process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
# output = process.communicate()[0]

try:
    output = subprocess.check_output(["git", "pull", "origin", "master"])
except subprocess.CalledProcessError as e:
    print 'Possible merge conflicts. Fix them before continuing'
    sys.exit()
