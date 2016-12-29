python ScreenOStoASAv2.py Juniper-To-ASA-Conversion-v2.txt
Please enter the source ScreenOS configuration file name: Juniper-To-ASA-Conversion-v2.txt
object service DNS
 service udp destination eq 53

object service FTP
 service TCP destination eq 21

object service GRE
 service gre

object service H.323
 service tcp destination eq 1720

object service HTTP
 service tcp destination eq 80

object service HTTPS
 service tcp destination eq 443

object service ICMP-ANY
 service icmp

object service LDAP
 service tcp destination eq 389

object service NTP
 service udp destination eq 123

object service PPTP
 service tcp destination eq 1723

object service RDP
 service tcp destination eq 3389

object service SMTP
 service tcp destination eq 25

object service SNMP
 service udp destination eq 161

object service SSH
 service tcp destination eq 22

object service SYSLOG
 service udp destination eq 514

object service TCP_1494
 service tcp destination eq 1494

object service TCP_45201-203
 service tcp destination range 45201 45203

object service TCP_8443
 service tcp destination eq 8443

object service TELNET
 service tcp destination eq 23

object service TFTP
 service udp destination eq 69

object-group service App_Services
 service-object object TCP 45201-203
 service-object object TCP 8443


object-group service Term_Srvr_Ports
 service-object object RDP
 service-object object TCP 1494


object network 10.1.1.0/24
 subnet 10.1.1.0 255.255.255.0

object network 10.1.1.10/32
 host 10.1.1.10

object network 10.1.1.11/32
 host 10.1.1.11

object network 10.1.1.12/32
 host 10.1.1.12

object network 10.2.2.10/32
 description Web Srvr 1
 host 10.2.2.10

object network 10.2.2.11/32
 description Web Srvr 2
 host 10.2.2.11

object network 10.3.3.0/24
 subnet 10.3.3.0 255.255.255.0

object network 10.3.3.10/32
 description Term Srvr 1
 host 10.3.3.10

object network 10.3.3.12/32
 host 10.3.3.12

object network 10.4.4.0/24
 description VLAN 4
 subnet 10.4.4.0 255.255.255.0

object network Inside_Net_5
 subnet 10.5.5.0 255.255.255.0

object network Inside_Net_6
 subnet 10.6.6.0 255.255.255.0

object network Inside_Net_7
 subnet 10.7.7.0 255.255.255.0

object network Net_2
 description VLAN 2
 subnet 10.2.2.0 255.255.255.0

object network Outside_Net_1
 subnet 99.99.99.0 255.255.255.0

object network Outside_Net_2
 subnet 88.88.88.0 255.255.255.0

object network Outside_Net_3
 subnet 77.77.77.0 255.255.255.0

object network SMTP_Svr_1
 description SMTP Server 1
 host 10.4.4.10

object network SMTP_Svr_2
 description SMTP Server 2
 host 10.4.4.11

object network Some_remote_user
 host 99.99.99.99

object-group network SMTP_Servers
 network-object object SMTP_Svr_1
 network-object object SMTP_Svr_2


object-group network Term_Srvrs
 network-object object 10.3.3.10/32
 network-object object 10.3.3.11/32


object-group network VLAN_30_Hosts
 network-object object 10.3.3.10/32
 network-object object 10.3.3.11/32


object-group network Web_Servers
 network-object object 10.2.2.10/32
 network-object object 10.2.2.11/32


----------------------------------------------------------------------------------------------------
Policy ID:      100
From Zone:      Outside   To Zone: Inside
Source(s):      Any
Destination(s): Any
Service(s)    : ICMP-ANY
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 100
access-list Outside-IN extended permit object-group ICMP-ANY object-group Any object-group Any
----------------------------------------------------------------------------------------------------
Policy ID:      101
From Zone:      Outside   To Zone: Inside
Source(s):      Any
Destination(s): Web_Srvrs
Service(s)    : HTTP
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 101
access-list Outside-IN extended permit object-group HTTP object-group Any object-group Web_Srvrs
----------------------------------------------------------------------------------------------------
Policy ID:      102
From Zone:      Outside   To Zone: Inside
Source(s):      Any, 10.3.3.10/32, 10.3.3.11/32
Destination(s): SMTP_Servers
Service(s)    : SMTP
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 102
access-list Outside-IN extended permit object-group SMTP object-group Any object-group SMTP_Servers
access-list Outside-IN extended permit object-group SMTP object-group 10.3.3.10/32 object-group SMTP_Servers
access-list Outside-IN extended permit object-group SMTP object-group 10.3.3.11/32 object-group SMTP_Servers
----------------------------------------------------------------------------------------------------
Policy ID:      103
From Zone:      Outside   To Zone: Inside
Source(s):      Web_Srvr
Destination(s): App_Srvr
Service(s)    : App_Services, App Services
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 103
access-list Outside-IN extended permit object-group App_Services object-group Web_Srvr object-group App_Srvr
access-list Outside-IN extended permit object-group App Services object-group Web_Srvr object-group App_Srvr
----------------------------------------------------------------------------------------------------
Policy ID:      104
From Zone:      Outside   To Zone: Inside
Source(s):      Any
Destination(s): Term_Srvrs
Service(s)    : RDP, TCP 1494
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 104
access-list Outside-IN extended permit object-group RDP object-group Any object-group Term_Srvrs
access-list Outside-IN extended permit object-group TCP 1494 object-group Any object-group Term_Srvrs
----------------------------------------------------------------------------------------------------
Policy ID:      105
From Zone:      Outside   To Zone: Inside
Source(s):      Some_remote_user
Destination(s): 10.1.1.10/32, 10.1.1.11/32
Service(s)    : HTTP
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 105
access-list Outside-IN extended permit object-group HTTP object-group Some_remote_user object-group 10.1.1.10/32
access-list Outside-IN extended permit object-group HTTP object-group Some_remote_user object-group 10.1.1.11/32
----------------------------------------------------------------------------------------------------
Policy ID:      106
From Zone:      Outside   To Zone: Inside
Source(s):      Outside_Net_1
Destination(s): Inside_Net_5, Inside Net 6, Inside Net 7
Service(s)    : TCP_45201-203, FTP, HTTP, TCP 8443
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 106
access-list Outside-IN extended permit object-group TCP_45201-203 object-group Outside_Net_1 object-group Inside_Net_5
access-list Outside-IN extended permit object-group TCP_45201-203 object-group Outside_Net_1 object-group Inside Net 6
access-list Outside-IN extended permit object-group TCP_45201-203 object-group Outside_Net_1 object-group Inside Net 7
access-list Outside-IN extended permit object-group FTP object-group Outside_Net_1 object-group Inside_Net_5
access-list Outside-IN extended permit object-group FTP object-group Outside_Net_1 object-group Inside Net 6
access-list Outside-IN extended permit object-group FTP object-group Outside_Net_1 object-group Inside Net 7
access-list Outside-IN extended permit object-group HTTP object-group Outside_Net_1 object-group Inside_Net_5
access-list Outside-IN extended permit object-group HTTP object-group Outside_Net_1 object-group Inside Net 6
access-list Outside-IN extended permit object-group HTTP object-group Outside_Net_1 object-group Inside Net 7
access-list Outside-IN extended permit object-group TCP 8443 object-group Outside_Net_1 object-group Inside_Net_5
access-list Outside-IN extended permit object-group TCP 8443 object-group Outside_Net_1 object-group Inside Net 6
access-list Outside-IN extended permit object-group TCP 8443 object-group Outside_Net_1 object-group Inside Net 7
----------------------------------------------------------------------------------------------------
Policy ID:      107
From Zone:      Outside   To Zone: Inside
Source(s):      Outside_Net_1, Outside Net 2
Destination(s): Inside_Net_1, Inside Net 2
Service(s)    : HTTP, FTP
Action:         permit

access-list Outside-IN remark from Outside to Inside policy id 107
access-list Outside-IN extended permit object-group HTTP object-group Outside_Net_1 object-group Inside_Net_1
access-list Outside-IN extended permit object-group HTTP object-group Outside_Net_1 object-group Inside Net 2
access-list Outside-IN extended permit object-group FTP object-group Outside_Net_1 object-group Inside_Net_1
access-list Outside-IN extended permit object-group FTP object-group Outside_Net_1 object-group Inside Net 2
access-list Outside-IN extended permit object-group HTTP object-group Outside Net 2 object-group Inside_Net_1
access-list Outside-IN extended permit object-group HTTP object-group Outside Net 2 object-group Inside Net 2
access-list Outside-IN extended permit object-group FTP object-group Outside Net 2 object-group Inside_Net_1
access-list Outside-IN extended permit object-group FTP object-group Outside Net 2 object-group Inside Net 2