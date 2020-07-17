import re
import subprocess
from datetime import datetime
from time import sleep, time

DEBUG = True  # print out messages to terminal
Max_debug = True
TEST_IPs = [ "8.8.8.8",  # Google's DNS server
             "208.69.38.205",  # OpenDNS
             "4.2.2.2" ]  # Level 3 Communications
OUTAGE_DURATION_SEC = 60  # shortest detectable outage

ONLINE = "Online"
OUTAGE = "Outage"
UNREACHABLE = "Network Unreachable"
HIGHLATENCY = 'High Latency'


def main() :
    poll_sec = OUTAGE_DURATION_SEC / 4.0  # Nyquist sampling rate
    try :
        while True :
            for ip in TEST_IPs :
                status = ping_loop( ip )
                if status == ONLINE :
                    print( 'No reported outages' )
                    sleep( poll_sec / len( TEST_IPs ) )
    except KeyboardInterrupt :
        exit()


def ping_loop( ip ) :
    ping_msg = get_ping_msg( ip )
    ping_time = get_ping_time( ping_msg )
    network_status = get_network_status( ping_msg, ping_time )
    timestamp = time()
    date_str = get_date_str( timestamp )
    time_str = get_time_str( timestamp )
    s = "{}, {}, {}, {}, {}, {}".format( ip, timestamp, date_str, time_str, network_status, ping_time )
    if DEBUG and network_status == OUTAGE or False :
        print( s )
    try:
        with open( get_filename(), "a" ) as logfile :
            logfile.write( s + "\n" )
    except PermissionError or FileNotFoundError:
        print('File error')
    return network_status


def get_filename() :
    timestamp = time()
    date_str = get_date_str( timestamp )
    filename = "{}.csv".format( date_str )
    return filename


def get_ping_msg( ip ) :
    ping_process = subprocess.Popen( [ "ping", '-c', '1', ip ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
    pingp = str( ping_process.stdout.read() )
    if False :
        print( pingp.split( '\n' ) )
    return pingp


def get_network_status( ping_msg, ping_time ) :
    if re.search( r'100.0% packet loss|100% packet loss', ping_msg ) != None :
        return OUTAGE
    elif re.search( r'Network is unreachable', ping_msg ) != None :
        return UNREACHABLE
    elif ping_time >= 200:
        return HIGHLATENCY
    else :
        return ONLINE


def get_ping_time( ping_msg ) :
    # match = re.search( r'\/\d{2,4}\.\d{3}\/', ping_msg )
    match = re.search( r'Average\s=\s[0-9]{1,1000}', ping_msg )
    if match is not None :
        # ping_time = float( match.group( 0 ).replace( "/", '' ) )
        ping_time = float( match.group( 0 ).split( '=' )[1] )
    else :
        ping_time = None
    if False :
        print( ping_time )
    return ping_time


def get_date_str( timestamp ) :
    dt = datetime.fromtimestamp( timestamp )
    return dt.strftime( "%Y-%m-%d" )


def get_time_str( timestamp ) :
    dt = datetime.fromtimestamp( timestamp )
    return dt.strftime( "%H:%M:%S" )


if __name__ == "__main__" :
    main()
