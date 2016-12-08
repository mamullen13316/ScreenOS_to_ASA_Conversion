This script will convert Juniper ScreenOS firewall rules to Cisco ASA firewall access-list syntax.

python ScreenOStoASA.py
Please enter the source ScreenOS configuration file name: Sample-Juniper-to-ASA-Comparison.txt
access-list BLOCK_ACCESS extended deny tcp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq 22
access-list BLOCK_ACCESS extended deny tcp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq 80
access-list BLOCK_ACCESS extended deny tcp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq ftp
access-list BLOCK_ACCESS extended deny tcp 192.168.10.0 255.255.255.0 192.168.20.0 255.255.255.0 eq 22
access-list BLOCK_ACCESS extended deny tcp 192.168.10.0 255.255.255.0 192.168.20.0 255.255.255.0 eq 443
access-list BLOCK_ACCESS extended permit tcp 192.168.30.0 255.255.255.0 192.168.40.0 255.255.255.0 eq 2200
access-list BLOCK_ACCESS extended permit tcp 192.168.30.0 255.255.255.0 192.168.40.0 255.255.255.0 eq 8080
access-list BLOCK_ACCESS extended permit tcp 192.168.30.0 255.255.255.0 192.168.40.0 255.255.255.0 eq 32000
access-list BLOCK_ACCESS_1 extended deny udp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq 53
access-list BLOCK_ACCESS_1 extended deny udp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq ntp
access-list BLOCK_ACCESS_1 extended deny udp 192.168.0.0 255.255.255.0 192.168.2.0 255.255.255.0 eq snmp
access-list BLOCK_ACCESS_1 extended permit tcp 192.168.10.0 255.255.255.0 192.168.20.0 255.255.255.0 eq 10000
