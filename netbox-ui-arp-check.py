import requests
import pynetbox

from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceBay, Rack, DeviceRole, DeviceType, Manufacturer, Site
from tenancy.models import Tenant

from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from nornir.core.filter import F

from extras.scripts import *

class Audit_Switch(Script):

    class Meta:
        name = "ARP Check NetBox Audit."
        description = "Script using Nornir & Napalm to query the ports of a switch and audit NetBox"

    device = ObjectVar(
        model=Device,
        query_params={'role': 'switch-layer-3', 'status': 'active', 'tag': 'napalm'}
    )

    def run(self, data, commit):
        """
        Mandatory to see any output in the NetBox UI.

        Run your scripts here and log the output to the screen for the user
        """
        session = requests.Session()
        session.verify = '/etc/ssl/certs'

        nb = pynetbox.api("<NB_URL>", "<NB_TOKEN>")
        nb.http_session = session

        # Device Object, from which you can get more details like --> device.name, device.id, device.device_role
        device = data['device']

        nr = InitNornir(config_file="./inventory/nornir_nb_layer-3.yaml")

        # Nornir uses NetBox username and password by default so we need to define them
        nr.inventory.defaults.username = '<USER>'
        nr.inventory.defaults.password = "<PASS>"

        # Pick one switch to run the audit against
        l3_filtered = nr.filter(F(name__contains=device.name))

        interfaces = []
        macs = []
        nb_ips = []
        output = []

        # use NAPALM to grab the arp table to find IP's and Interfaces to query NetBox
        arp_table = l3_filtered.run(task=napalm_get, getters=["get_arp_table"])

        for i in arp_table:
            arps = arp_table[i][0].result['get_arp_table']

            j = 0
            for k in arps:
                nb_ip = nb.ipam.ip_addresses.get(address=arps[j]['ip'])
                if not nb_ip:
                    arp_ip = (arps[j]['ip'] + " --> NOT FOUND IN NETBOX!!!")
                    self.log_success(arp_ip)
                    j += 1
                else:
                    interfaces.append(arps[j]['interface'])
                    macs.append(arps[j]['mac'])
                    nb_ip = nb.ipam.ip_addresses.get(address=arps[j]['ip'])
                    nb_ips.append(f"{nb_ip.dns_name} --> {nb_ip.status} --> {nb_ip.tenant}")
                    j += 1

            # Sort by interface for ease of use
            enum = [i[0] for i in sorted(enumerate(interfaces), key=lambda x:x[1])]

            for e in enum:
                output = [arp_table[device.name][0].result['get_arp_table'][e]['interface'], "-->",
                          arp_table[device.name][0].result['get_arp_table'][e]['ip'], "-->",
                          arp_table[device.name][0].result['get_arp_table'][e]['mac'], "-->",
                          nb_ips[e]]

                self.log_success(output)
