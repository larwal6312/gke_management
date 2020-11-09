import os
import json
import subprocess
from modules.gke_modules import *

command = 'find -L /usr/local/tomcat/webapps/ -type f -name "jdbc.properties" -exec grep "sqlserver" {} \;'

def main():
    print("Setting kubectl to UPDATE NAMESPACE HERE")
    os.system("kubectx UPDATE NAMESPACE HERE")
    podList = find_wave2_adportals()
    for pod in podList:
        badConnCount = 0
        print("\nChecking db connection string for %s" %(pod))
        checkDBstring = subprocess.Popen(['kubectl', 'exec', '-it', pod, '--', 'bash', '-c', command],
                                            shell=False,
                                            stdout=subprocess.PIPE)
        result = checkDBstring.stdout.read().splitlines()
        for line in result:
            if str(line.lower()) in ("wave2-g1-ag.gmti.gbahn.net", "wave2-g2-ag.gmti.gbahn.net"):
                print("Bad connection string found.\n")
                print(line.decode('utf-8'))
                badConnCount +=1
        if badConnCount == 0:
            print("Connection strings are valid")


if __name__ == '__main__':
    main()
