'''This script will convert a Juniper ScreenOS access rules to the equivalent access-list commands
on the Cisco ASA platform'''
import shlex


def FileToList(fn):
    'Read in the source file and store each line in a list'
    with open(fn,mode='r') as f:
        srcconfig = f.readlines()
    return srcconfig

def MaskConvert(s):
    mask_dict = {'/8':'255.0.0.0',
                 '/9':'255.128.0.0',
                 '/10':'255.192.0.0',
                 '/11':'255.224.0.0',
                 '/12':'255.240.0.0',
                 '/13':'255.248.0.0',
                 '/14':'255.252.0.0',
                 '/15':'255.254.0.0',
                 '/16':'255.255.0.0',
                 '/17':'255.255.128.0',
                 '/18':'255.255.192.0',
                 '/19':'255.255.224.0',
                 '/20':'255.255.240.0',
                 '/21':'255.255.248.0',
                 '/22':'255.255.252.0',
                 '/23':'255.255.254.0',
                 '/24':'255.255.255.0',
                 '/25':'255.255.255.128',
                 '/26':'255.255.255.192',
                 '/27':'255.255.255.224',
                 '/28':'255.255.255.240',
                 '/29':'255.255.255.248',
                 '/30':'255.255.255.252',
                 '/31':'255.255.255.254',
                 '/32':'255.255.255.255'}
    for key in mask_dict.keys():
        if key in s:
            mask = mask_dict[key]
    return mask

def LineParser(src_config):
    result_dict = {}
    if not 'svc_dict' in result_dict:
        result_dict['svc_dict'] = {}
    result_dict['svc_group_dict'] = {}
    defaults_dict = {'DNS': {'proto': 'udp', 'port': '53'}, 'FTP': {'proto': 'TCP', 'port': '21'},
                     'H.323': {'proto': 'tcp', 'port': '1720'}, 'HTTP': {'proto': 'tcp', 'port': '80'},
                     'HTTPS': {'proto': 'tcp', 'port': '443'}, 'ICMP-ANY': {'proto': 'icmp'}, 'GRE': {'proto': 'gre'},
                     'LDAP': {'proto': 'tcp', 'port': '389'}, 'NTP': {'proto': 'udp', 'port': '123'},
                     'PPTP': {'proto': 'tcp', 'port': '1723'}, 'SMTP': {'proto': 'tcp', 'port': '25'},
                     'SNMP': {'proto': 'udp', 'port': '161'}, 'SSH': {'proto': 'tcp', 'port': '22'},
                     'SYSLOG': {'proto': 'udp', 'port': '514'}, 'TELNET': {'proto': 'tcp', 'port': '23'},
                     'TFTP': {'proto': 'udp', 'port': '69'}}
    for svc in defaults_dict.keys():
        result_dict['svc_dict'][svc] = {}
        result_dict['svc_dict'][svc]['proto'] = defaults_dict[svc]['proto']
        if 'port' in defaults_dict[svc]:
            result_dict['svc_dict'][svc]['begin_dst_port'] = defaults_dict[svc]['port']
            result_dict['svc_dict'][svc]['end_dst_port'] = defaults_dict[svc]['port']
    multi_svc = False

    for line in src_config:
        orig_line = line
        if 'timeout' in line:
            line = line[0:line.find('timeout')]
        if 'tunnel vpn' in line:
            continue
        if ('set service' in line) and (len(line.split()) > 4):
            s,sv,svc_object,p,proto,sp,src_port,d,dst_port = shlex.split(line)
            svc_object = svc_object.replace(' ','_')
            if not svc_object in result_dict['svc_dict'] and not p == '+':
                result_dict['svc_dict'][svc_object] = {}
                multi_svc = False
                begin_dst_port, end_dst_port = dst_port.split('-')
                result_dict['svc_dict'][svc_object] = {}
                result_dict['svc_dict'][svc_object]['proto'] = proto
                result_dict['svc_dict'][svc_object]['srcport'] = src_port
                result_dict['svc_dict'][svc_object]['begin_dst_port'] = begin_dst_port
                result_dict['svc_dict'][svc_object]['end_dst_port'] = end_dst_port

            if p == '+' and not multi_svc:
                result_dict['svc_dict'][svc_object+'_t1'] = result_dict['svc_dict'][svc_object]
                result_dict['svc_dict'].pop(svc_object)
                multi_svc = True
                t = 1
                result_dict['svc_group_dict'][svc_object] = {}
                result_dict['svc_group_dict'][svc_object]['service'] = [svc_object +'_t1']

            if p == '+' and multi_svc:
                begin_dst_port, end_dst_port = dst_port.split('-')
                result_dict['svc_dict'][svc_object + '_t' + str(t + 1)] = {}
                result_dict['svc_dict'][svc_object + '_t' + str(t + 1)]['proto'] = proto
                result_dict['svc_dict'][svc_object + '_t' + str(t + 1)]['srcport'] = src_port
                result_dict['svc_dict'][svc_object + '_t' + str(t + 1)]['begin_dst_port'] = begin_dst_port
                result_dict['svc_dict'][svc_object + '_t' + str(t + 1)]['end_dst_port'] = end_dst_port
                result_dict['svc_group_dict'][svc_object]['service'].append(svc_object + '_t' + str(t + 1))
                t = t + 1

        if 'set group service' in line:
            if not 'svc_group_dict' in result_dict:
                result_dict['svc_group_dict'] = {}
            if 'comment' in line:
                s,g,sv,svc_name,c,comment = shlex.split(line)
                svc_name = svc_name.replace(' ','_')
                if not svc_name in result_dict['svc_group_dict']:
                    result_dict['svc_group_dict'][svc_name] = {}
                result_dict['svc_group_dict'][svc_name]['comment'] = comment
            if 'add' in line:
                s,g,s,svc_name,a,service = shlex.split(line)
                svc_name = svc_name.replace(' ','_')
                if not svc_name in result_dict['svc_group_dict']:
                    result_dict['svc_group_dict'][svc_name] = {}
                if not 'service' in result_dict['svc_group_dict'][svc_name]:
                    result_dict['svc_group_dict'][svc_name]['service'] = []
                result_dict['svc_group_dict'][svc_name]['service'].append(service)
        if 'set address' in line:
            if not 'net_obj_dict' in result_dict:
                result_dict['net_obj_dict'] = {}
            if len(shlex.split(line)) == 7:
                s,a,intf,object_name,ip_addr,mask,desc = shlex.split(line)
                desc_flag = True
                mask_flag = True
            elif len(shlex.split(line)) == 6:
                s,a,intf,object_name,ip_addr,mask = shlex.split(line)
                desc_flag = False
                mask_flag = True
            elif len(shlex.split(line)) == 5:
                s,a,intf,object_name,ip_addr = shlex.split(line)
                desc_flag = False
                mask_flag = False
            object_name = object_name.replace(' ','_')
            if not object_name in result_dict['net_obj_dict']:
                result_dict['net_obj_dict'][object_name] = {}
            result_dict['net_obj_dict'][object_name]['intf'] = intf
            result_dict['net_obj_dict'][object_name]['ip_addr'] = ip_addr
            if desc_flag:
                result_dict['net_obj_dict'][object_name]['desc'] = desc
            if mask_flag:
                result_dict['net_obj_dict'][object_name]['mask'] = mask

        if 'set group address' in line:
            if not 'net_obj_group_dict' in result_dict:
                result_dict['net_obj_group_dict'] = {}
            if len(shlex.split(line)) == 7:
                s,g,a,intf,object_name,a,added_obj = shlex.split(line)
                added_obj = added_obj.replace(' ','_')
            elif len(shlex.split(line)) == 5:
                s,g,a,intf,object_name = shlex.split(line)
                object_name = object_name.replace(' ','_')
                added_obj = ''
            object_name = object_name.replace(' ','_')
            if not object_name in result_dict['net_obj_group_dict']:
                result_dict['net_obj_group_dict'][object_name] = {}
            result_dict['net_obj_group_dict'][object_name]['intf'] = intf
            if not 'added_list' in result_dict['net_obj_group_dict'][object_name]:
                result_dict['net_obj_group_dict'][object_name]['added_list'] = []
            if not added_obj == '':
                result_dict['net_obj_group_dict'][object_name]['added_list'].append(added_obj)
        if 'set policy id' in line and len(shlex.split(line)) > 4:
            nat = False
            if 'log' in line:
                line = line[0:line.find('log')]
            if 'no-session-backup' in line:
                line = line[0:line.find('no-session-backup')]
            if 'nat src' in line:
                s,p,i,id_nbr,n,bs,f,from_if,t,to_if,src_object,dst_object,dst_svc,nat,nsrc,action = shlex.split(line)
                nat = True
            elif 'name' in line:
                s,p,i,id_nbr,n,bs,f,from_if,t,to_if,src_object,dst_object,dst_svc,action = shlex.split(line)
            else:
                s,p,i,id_nbr,f,from_if,t,to_if,src_object,dst_object,dst_svc,action = shlex.split(line)
            src_object = src_object.replace(' ','_')
            dst_object = dst_object.replace(' ','_')
            dst_svc = dst_svc.replace(' ','_')
            if not 'acl_entry_dict' in result_dict:
                result_dict['acl_entry_dict'] = {}
            result_dict['acl_entry_dict'][id_nbr] = {}
            result_dict['acl_entry_dict'][id_nbr]['from_if'] = from_if
            result_dict['acl_entry_dict'][id_nbr]['to_if'] = to_if
            if not 'src_object_list' in result_dict['acl_entry_dict'][id_nbr]:
                result_dict['acl_entry_dict'][id_nbr]['src_object_list'] = []
            if not 'dst_object_list' in result_dict['acl_entry_dict'][id_nbr]:
                result_dict['acl_entry_dict'][id_nbr]['dst_object_list'] = []
            if not 'dst_svc_list' in result_dict['acl_entry_dict'][id_nbr]:
                result_dict['acl_entry_dict'][id_nbr]['dst_svc_list'] = []
            result_dict['acl_entry_dict'][id_nbr]['nat'] = nat
            result_dict['acl_entry_dict'][id_nbr]['src_object_list'].append(src_object)
            result_dict['acl_entry_dict'][id_nbr]['dst_object_list'].append(dst_object)
            result_dict['acl_entry_dict'][id_nbr]['dst_svc_list'].append(dst_svc)
            result_dict['acl_entry_dict'][id_nbr]['action'] = action
        if 'set src-address' in line:
            s,src,src_object = shlex.split(line)
            result_dict['acl_entry_dict'][id_nbr]['src_object_list'].append(src_object)
        if 'set dst-address' in line:
            d,dst,dst_object = shlex.split(line)
            result_dict['acl_entry_dict'][id_nbr]['dst_object_list'].append(dst_object)
        if 'set service' in orig_line and len(shlex.split(orig_line)) == 3:
            s,sv,dst_svc = shlex.split(orig_line)
            result_dict['acl_entry_dict'][id_nbr]['dst_svc_list'].append(dst_svc)

    return result_dict

def BuildServiceObjects(svc_dict):
    output_list = []
    for service_name in sorted(svc_dict.keys()):
        output_list.append('object service {0}'.format(service_name))
        if svc_dict[service_name]['proto'] == 'icmp' or svc_dict[service_name]['proto'] == 'gre':
            output_list.append(' service {0}\n'.format(svc_dict[service_name]['proto']))
        else:
            if int(svc_dict[service_name]['begin_dst_port']) == int(svc_dict[service_name]['end_dst_port']):
                output_list.append(' service {0} destination eq {1} \n'.format(svc_dict[service_name]['proto'],svc_dict[service_name]['end_dst_port']))
            if int(svc_dict[service_name]['end_dst_port']) > int(svc_dict[service_name]['begin_dst_port']):
                output_list.append(' service {0} destination range {1} {2} \n'.format(svc_dict[service_name]['proto'],
                                                                                      svc_dict[service_name]['begin_dst_port'],
                                                                                      svc_dict[service_name]['end_dst_port']))
    return output_list

def BuildServiceObjectGroups(svc_group_dict):
    output_list = []
    for object_name in sorted(svc_group_dict.keys()):
        output_list.append('object-group service {0}'.format(object_name))
        if 'comment' in svc_group_dict[object_name]:
            output_list.append(' description {0}'.format(svc_group_dict[object_name]['comment']))
        for service in svc_group_dict[object_name]['service']:
            output_list.append(' service-object object {0}'.format(service))
        output_list.append('\n')
    return output_list

def BuildNetworkObjects(net_obj_dict):
    output_list = []
    for object_name in sorted(net_obj_dict.keys()):
        output_list.append('object network {0}'.format(object_name))
        if 'desc' in net_obj_dict[object_name]:
            output_list.append(' description {0}'.format(net_obj_dict[object_name]['desc']))
        if 'mask' in net_obj_dict[object_name]:
            if net_obj_dict[object_name]['mask'] == '255.255.255.255':
                output_list.append(' host {0}\n'.format(net_obj_dict[object_name]['ip_addr']))
            else:
                output_list.append(' subnet {0} {1}\n'.format(net_obj_dict[object_name]['ip_addr'],net_obj_dict[object_name]['mask']))
        else:
            output_list.append(' host {0}\n'.format(net_obj_dict[object_name]['ip_addr']))
    return output_list

def BuildNetworkObjectGroups(net_obj_group_dict):
    output_list = []
    for object_name in sorted(net_obj_group_dict.keys()):
        output_list.append('object-group network {0}'.format(object_name))
        for added_object in net_obj_group_dict[object_name]['added_list']:
            output_list.append(' network-object object {0}'.format(added_object))
        output_list.append('\n')
    return output_list

def BuildACLEntries(acl_entry_dict):
    output_list = []
    for id in [str(y) for y in sorted([int(x) for x in acl_entry_dict.keys()])]:
        output_list.append('-' * 100)
        output_list.append('Policy ID:      {0}'.format(id))
        output_list.append('From Zone:      {0}   To Zone: {1}'.format(acl_entry_dict[id]['from_if'],acl_entry_dict[id]['to_if']))
        output_list.append('Source(s):      {0}'.format(', '.join(acl_entry_dict[id]['src_object_list'])))
        output_list.append('Destination(s): {0}'.format(', '.join(acl_entry_dict[id]['dst_object_list'])))
        output_list.append('Service(s)    : {0}'.format(', '.join(acl_entry_dict[id]['dst_svc_list'])))
        output_list.append('Action:         {0}\n'.format(acl_entry_dict[id]['action']))
        if acl_entry_dict[id]['nat']:
            output_list.append('SKIPPING THIS LINE DUE TO NAT SRC IN ORIGINAL CONFIG LINE!')
            output_list.append('-' * 100)
            continue
        output_list.append('access-list {0}-IN remark from {1} to {2} policy id {3}'.format(
            acl_entry_dict[id]['from_if'],
            acl_entry_dict[id]['from_if'],
            acl_entry_dict[id]['to_if'],
            id))
        for src_obj in acl_entry_dict[id]['src_object_list']:
            for svc_obj in acl_entry_dict[id]['dst_svc_list']:
                for dst_obj in acl_entry_dict[id]['dst_object_list']:
                    output_list.append('access-list {0}-IN extended {1} object-group {2} object-group {3} object-group {4}'.format(
                        acl_entry_dict[id]['from_if'],
                        acl_entry_dict[id]['action'],
                        svc_obj,
                        src_obj,
                        dst_obj))
    return output_list

def PrintOutput(fn,d):
    for line in fn(d):
        print line

if __name__ == '__main__':
    fn = raw_input("Please enter the source ScreenOS configuration file name: ")
    srcconfig = FileToList(fn)
    result_dict = LineParser(srcconfig)
    PrintOutput(BuildServiceObjects,result_dict['svc_dict'])
    PrintOutput(BuildServiceObjectGroups,result_dict['svc_group_dict'])
    PrintOutput(BuildNetworkObjects,result_dict['net_obj_dict'])
    PrintOutput(BuildNetworkObjectGroups,result_dict['net_obj_group_dict'])
    PrintOutput(BuildACLEntries,result_dict['acl_entry_dict'])











