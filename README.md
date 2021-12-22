# netbox-ui-arp-checker

### Using NetBox, Nornir and Napalm to query a switch ARP table and compare the results to what is in NetBox

#### This script is to be run from within the NetBox GUI itself 

* Need to set username and password for NorNir
* Need to set NetBox URL and TOKEN
* Switch Filter criteria: role: "switch-layer-3", status: "active", tag: "napalm" 

<img width="1422" alt="ARP_CHECK" src="https://user-images.githubusercontent.com/50723251/147048825-e1502bdd-b91b-446c-9a66-173b3c80c7b0.png">
