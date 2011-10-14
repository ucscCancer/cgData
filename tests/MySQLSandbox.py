import atexit
import os
import shutil
from signal import SIGTERM
from string import Template
from sys import exit
import subprocess

class Sandbox(object):
    nextPort = 30000+os.getpid()
    mysqld = "/usr/sbin/mysqld"
    mysql = "/usr/bin/mysql"
    mysql_install_db = "/usr/bin/mysql_install_db"

    cnfTemplate = Template(
"""
[mysqld]
datadir=${datadir}
port=${port}
bind-address=127.0.0.1
socket=${datadir}/socket
console

[client]
port=${port}
socket=${datadir}/socket
host=localhost
user=root
""")

    @classmethod
    def __portGet__(cls):
        p = cls.nextPort
        cls.nextPort += 1
        return p

    def __init__(self, name=None):
        from time import sleep
        self.port = self.__portGet__()
        if name == None:
            name = self.port
        self.datadir = "%s/%s_datadir" % (os.getcwd(), name)
        self.defaults = "%s/sandbox.cnf" % self.datadir
        if os.path.isdir(self.datadir):
            shutil.rmtree(self.datadir)
        os.mkdir(self.datadir)
        cnf = open(self.defaults, 'w')
        cnf.write(self.cnfTemplate.substitute(datadir=self.datadir, port=str(self.port)))
        cnf.close()

        # XXX dropping output on the floor
        subprocess.check_output([self.mysql_install_db, "--datadir=%s" % self.datadir,
            "--defaults-file=%s" % self.defaults])

        log = open("%s/mysqld.log" % self.datadir, "w")
        self.process = subprocess.Popen([self.mysqld, "--defaults-file=%s" % self.defaults], stdout=log, stderr=log)
        count = 15
        while count > 0 and not os.path.exists('%s/socket' % self.datadir):
            sleep(0.5)
            count -= 1
        if count == 0:
            raise Exception('mysqld not up')

        atexit.register(lambda: self.shutdown())

    def shutdown(self):
        self.process.poll()
        if self.process.returncode == None:
            self.process.terminate()
            self.process.wait()
        if os.path.isdir(self.datadir):
            shutil.rmtree(self.datadir)

if __name__ == '__main__':
    from time import sleep
    sb1 = Sandbox('foo')
    sb2 = Sandbox('bar')
    sb3 = Sandbox()
    sleep(5)
