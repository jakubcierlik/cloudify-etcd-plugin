#!/usr/bin/env python3
import argparse
import logging
import paramiko
import os
import sys
from time import sleep
import re

LOG_DIR = '/usr/local/nefeli/log/exp/nefeli-nfc/plugins/'
LOG_FILE = LOG_DIR + 'flexvnf_plugin.log'
ROOT_PASS = "versa123"

def time_stamped(fname, fmt='{fname}_%Y-%m-%d-%H-%M-%S'):
        return datetime.datetime.now().strftime(fmt).format(fname=fname)

class Flexvnf(object):

    def __init__(self, IP, port, username, password):
        self.host = IP
        self.port = port
        self.username = username
        self.password = password
        self.sshClient = paramiko.SSHClient()
        self.sshClient.load_system_host_keys()
        self.sshClient.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)

    def connect_ssh(self):

        try:
            self.sshClient.connect(self.host, port=self.port, banner_timeout=60,
                    username=self.username, password=self.password)
            return True
        except Exception as error:
            logging.error("Unable to ssh to flexvnf VM.\
                    {Error}".format(Error=error))
            return False

    def exec_ssh_command(self, commands, timeout, inpoot):
        try:
            cliShell = self.sshClient.invoke_shell()
        except paramiko.ssh_exception.SSHException as error:
            logging.error("Unable to invoke shell. Err:{err}".format(err=error))
            return False
        for command in commands:
            try:
                cliShell.send(command + "\n")
            except Exception as error:
                logging.warn("command '{cmd}'send"\
                        "failed. {err}".format(cmd=command, err=error))
                return False
            if inpoot:
                cliShell.send(inpoot + "\n")
            sleep(timeout)
            cmd_output = cliShell.recv(4096)
        return cmd_output

    def edit_config(self, local_id, remote_id, controller_ip_address, local_key, remote_key, wan_port, serial_number, wan_ip_addr, wan_gw_addr):
        if not self.connect_ssh():
            logging.error("Configuration edit failed. Unable to ssh to NF.")
            return False
        if not wan_ip_addr:
            cmd = ["sudo /opt/versa/scripts/staging.py -l {lid} -lk {lkey} -r {rid} -rk {rkey} -c {cip} -t staging -w {pn} -d -n {sn}".format(
                lid=local_id, lkey=local_key, rkey=remote_key, rid=remote_id, cip=controller_ip_address,pn=wan_port, sn=serial_number)]
        else:
            cmd = ["sudo /opt/versa/scripts/staging.py -l {lid} -lk {lkey} -r {rid} -rk {rkey} -c {cip} -t staging -w {pn} -s {wan_ip} -g {gw_ip} -n {sn}".format(
                lid=local_id, lkey=local_key, rkey=remote_key, rid=remote_id,cip=controller_ip_address,pn=wan_port, sn=serial_number, wan_ip=wan_ip_addr, gw_ip=wan_gw_addr)]
        logging.debug("command to activate VNF:%s",cmd)
        output = self.exec_ssh_command(cmd, 10, ROOT_PASS)
        output = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', output.decode()).replace('\b', '').replace('\r', '')
        logging.debug("Activating flexVNF [{sn}]. output{out}:".format(sn=serial_number, out=output))
        if "Loading generated config into CDB" not in output:
            logging.error("Error while activating flexVNF [{sn}]. Error{err}:".format(
                sn=serial_number, err=output))
            return False
        return True

    def liveness_check(self):
        logging.debug("sleeping for 10 mins.")
        sleep(600)
        if not self.connect_ssh():
            logging.error("Configuration edit failed. Unable to ssh to NF.")
            return False

        service_check_cmd = ["vsh status"]
        logging.debug("command to check versa services:%s",service_check_cmd)
        service_check_output = self.exec_ssh_command(service_check_cmd, 10, ROOT_PASS)
        service_check_output = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', service_check_output.decode()).replace('\b', '').replace('\r', '')
        logging.debug("flexVNF services status {out}:".format(out=service_check_output))
        if "stopped" in service_check_output:
            logging.error("versa service is stopped")
            return False

        connectivity_check_cmd = ["cli","show system managment-status"]
        logging.debug("command to check versa connectivity:%s",connectivity_check_cmd)
        connectivity_check_output = self.exec_ssh_command(connectivity_check_cmd, 10, None)
        connectivity_check_output = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', connectivity_check_output.decode()).replace('\b', '').replace('\r', '')
        logging.debug("flexVNF services status {out}:".format(out=connectivity_check_output))
        # FIXME: Remove "connecting" check after resolving NEF-5343.
        if "connected" in connectivity_check_output: #or "connecting" in connectivity_check_output:
            logging.debug("flexvnf is connected to director")
            return True
        else:
            logging.error("Liveness-check Failed")
            return False

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True, help='host')
    parser.add_argument("--port", required=True, help='port')
    parser.add_argument("--username", required=True, help='username')
    parser.add_argument("--password", required=True, help='password',
            default="")
    parser.add_argument("--local-id",
                       help=' local ID of device to active')
    parser.add_argument("--remote-id",
                       help=' remote ID')
    parser.add_argument("--local-key",
                       help='local psk key of device to active (default=1234)',
                       default='1234')
    parser.add_argument("--remote-key",
                       help='remote psk key (default=1234)',
                       default='1234')
    parser.add_argument("--controller-ip-address",
                       help='IP address of the Controller')
    parser.add_argument("--wan-port",
                       help='WAN port to use to reach the internet (e.g. 0 or 1)')
    parser.add_argument("--serial-number",
                       help='Serial number associated with the device')
    parser.add_argument("--wan-iface-address", 
                       help='IP address of the Controller')
    parser.add_argument("--wan-gateway-address",
                       help='IP address of the Controller')

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--edit-config", 
                       help='take a config and merge it in')
    group.add_argument("--liveness-check", action='store_true',
                       help='Heuristic check to see if device is live')

    parser.add_argument("-l", "--log", help='log level', default='DEBUG')
    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper(), None)
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(filename=LOG_FILE, level=loglevel,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %I:%M:%S %p')
    wan_iface_static_ip_address = None
    wan_iface_static_gw_address = None

    if args.edit_config:
        try:
            assert(args.local_id)
            assert(args.local_key)
            assert(args.remote_id)
            assert(args.remote_key)
            assert(args.controller_ip_address)
            assert(args.wan_port)
            assert(args.serial_number)
            try:
                assert(args.wan_iface_address)
                wan_iface_static_ip_address = args.wan_iface_address
                try:
                    assert(args.wan_gateway_address)
                    wan_iface_static_gw_address = args.wan_gateway_address
                except exception as err:
                    logging.error("Missing gateway address")
                    sys.exit(2)
            except Exception as dynamic:
                logging.debug("Opted DHCP for WAN interface address assignment.")
        except Exception as err:
            logging.error("Missing argument. please check --help")
            sys.exit(2)
        flexvnf = Flexvnf(args.host, args.port, args.username,
            args.password)
        if not flexvnf.edit_config(args.local_id, args.remote_id, args.controller_ip_address, args.local_key, args.remote_key,
                args.wan_port, args.serial_number, wan_iface_static_ip_address, wan_iface_static_gw_address):
            sys.exit(1)

    if args.liveness_check:
        flexvnf = Flexvnf(args.host, args.port, args.username,
            args.password)
        if not flexvnf.liveness_check():
            sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()