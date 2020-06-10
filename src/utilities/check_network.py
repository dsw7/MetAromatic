from subprocess import Popen, DEVNULL

def is_network_good():
    process = Popen(['ping', '-n', '2', '8.8.8.8'], stdout=DEVNULL)
    process.wait()
    return process.returncode == 0
