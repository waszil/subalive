import sys
import subprocess
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading
import time

__all__ = ['SubAliveMaster', 'SubAliveSlave']


# period for alive keeping in [s]
_AlivePeriod_s = 5
# max value of alive counter
_AliveCounterMax = 256
# RPC server address
_RPC_IP = 'localhost'
_RPC_PORT = 8000
_RPC_ADDRESS = (_RPC_IP, _RPC_PORT)
# RPC server URI
_RPC_URI = f"http://{_RPC_IP}:{_RPC_PORT}/"


class SubAliveMaster:
    """
    Class for starting a python script in a subprocess (slave), and sending periodic alive ping
    for it. The slave closes by its own if the alive stops.
    """

    def __init__(self, subprocess_file_path: str):
        """
        Init for master
        :param subprocess_file_path: file path that contains the script to be started in a
        subprocess, that uses the SubAliveSlave
        """
        self.subprocess_file_path = subprocess_file_path
        # alive ping period
        self.alive_period_s = _AlivePeriod_s
        self.alive_cnt = 0
        self.slave_alive_service = xmlrpc.client.ServerProxy(_RPC_URI)
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen([sys.executable,
                          self.subprocess_file_path],
                         creationflags=DETACHED_PROCESS, shell=True)
        # start periodic alive sending
        self.send_alive_ping()

    def send_alive_ping(self):
        """
        Periodic task for sending alive ping
        """
        # send alive ping via RPC
        try:
            self.slave_alive_service.alive(self.alive_cnt)
        except (ConnectionRefusedError,
                ConnectionResetError,
                ConnectionAbortedError,
                ConnectionError) as e:
            print(f'Slave process might have terminated ({e}). Stop alive keeping.')
            return
        # incrementing alive counter
        self.alive_cnt = (self.alive_cnt + 1) % _AliveCounterMax
        # restart periodic alive sending
        threading.Timer(self.alive_period_s, self.send_alive_ping).start()


class SubAliveSlave:
    """
    Class for handling a master's alive pings. If the alive timeouts, we can quit.
    """

    def __init__(self):
        # print('starting with master alive period', master_alive_period_s)
        self.alive_check_period_s = _AlivePeriod_s * 1.5
        # last time the master pinged alive
        self.prev_alive_ping_time = time.time()
        # previously received alive counter
        self.prev_alive_cnt = None
        # start RPC server for alive ping
        self.server = SimpleXMLRPCServer(_RPC_ADDRESS, logRequests=False)
        # register alive ping function, to be called by the master process
        self.server.register_function(self.alive, 'alive')
        # create and start the RPC server in a separate thread
        self.rpc_thread = threading.Thread(target=self.server.serve_forever)
        self.rpc_thread.start()
        # start the periodic timeout checker
        self.check_timeout()

    def alive(self, alive_cnt: int):
        """
        Method to be called via RPC by the master
        :param alive_cnt: master increments it modulo _AliveCounterMax
        :return: 0, because xmlrpc requires something.
        """
        # print('alive received', alive_cnt)
        if self.prev_alive_cnt is not None:
            if (alive_cnt - self.prev_alive_cnt) not in [1, 1 - _AliveCounterMax]:
                print('Invalid alive received.')
        self.prev_alive_cnt = alive_cnt
        self.prev_alive_ping_time = time.time()
        return 0

    def check_timeout(self):
        """
        Periodic timeout check for the master's alive ping
        """
        # print('checking timeout')
        if time.time() - self.prev_alive_ping_time >= self.alive_check_period_s:
            # timeout, shutdown RPC server and quit.
            self.server.shutdown()
            print('timeout, closing.')
            self.rpc_thread.join(timeout=5)
            # time.sleep(2)
            exit(0)
        else:
            pass
            # print('  ok')
        # reschedule timeout checking
        threading.Timer(self.alive_check_period_s, self.check_timeout).start()
