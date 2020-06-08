import sys
from subprocess import Popen, PIPE

def check_network_connection():
    process = Popen(['ping', '-n', '2', '8.8.8.8'], stdout=PIPE)
    stdout = process.communicate()
    process.wait()
    if "Destination host unreachable" in stdout[0].decode():
        sys.exit('Cannot establish network connection.')
