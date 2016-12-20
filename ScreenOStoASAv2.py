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

def SpaceReplacer(s):
    if ' ' in s:
        s = s.replace(' ','_')
    return s


def LineParser(src_config):
    svc_dict = {}
    svc_group_dict = {}
    net_obj_dict = {}
    net_obj_group_dict = {}
    acl_entry_dict = {}
    for line in src_config:
        if 'set service' in line:
            s,sv,svc_object,p,proto,sp,src_port,d,dst_port = shlex.split(line)
            svc_object = SpaceReplacer(svc_object)
            if '-' in dst_port:
                dst_port = dst_port[0:dst_port.find('-')]
            svc_dict[svc_object] = {}
            svc_dict[svc_object]['proto'] = proto
            svc_dict[svc_object]['srcport'] = src_port
            svc_dict[svc_object]['dst_port'] = dst_port
        if 'set group service' in line:
            if 'comment' in line:
                s,g,sv,svc_name,c,comment = shlex.split(line)
                svc_name = SpaceReplacer(svc_name)
                if not svc_name in svc_group_dict:
                    svc_group_dict[svc_name] = {}
                svc_group_dict[svc_name]['comment'] = comment
            if 'add' in line:
                s,g,s,svc_name,a,service = shlex.split(line)
                svc_name = SpaceReplacer(svc_name)
                if not svc_name in svc_group_dict:
                    svc_group_dict[svc_name] = {}
                if not 'service' in svc_group_dict[svc_name]:
                    svc_group_dict[svc_name]['service'] = []
                svc_group_dict[svc_name]['service'].append(service)
        if 'set address' in line:
            s,a,intf,object_name,ip_addr,mask,desc = shlex.split(line)
            object_name = SpaceReplacer(object_name)
            if not object_name in net_obj_dict:
                net_obj_dict[object_name] = {}
            net_obj_dict[object_name]['intf'] = intf
            net_obj_dict[object_name]['ip_addr'] = ip_addr
            net_obj_dict[object_name]['mask'] = mask
            net_obj_dict[object_name]['desc'] = desc
        if 'set group address' in line:
            s,g,a,intf,object_name,a,added_obj = shlex.split(line)
            object_name = SpaceReplacer(object_name)
            if not object_name in net_obj_group_dict:
                net_obj_group_dict[object_name] = {}
            net_obj_group_dict[object_name]['intf'] = intf
            if not 'added_list' in net_obj_group_dict[object_name]:
                net_obj_group_dict[object_name]['added_list'] = []
            net_obj_group_dict[object_name]['added_list'].append(added_obj)
        if 'set policy id' in line:
            s,p,i,id_nbr,n,bs,f,from_if,t,to_if,src_object,dst_object,dst_port,action = shlex.split(line)
            src_object = SpaceReplacer(src_object)
            dst_object = SpaceReplacer(dst_object)
            dst_port = SpaceReplacer(dst_port)
            acl_entry_dict[id_nbr] = {}
            acl_entry_dict[id_nbr]['from_if'] = from_if
            acl_entry_dict[id_nbr]['to_if'] = to_if
            acl_entry_dict[id_nbr]['src_object'] = src_object
            acl_entry_dict[id_nbr]['dst_object'] = dst_object
            acl_entry_dict[id_nbr]['dst_port'] = dst_port
            acl_entry_dict[id_nbr]['action'] = action

    return svc_dict,svc_group_dict,net_obj_dict,net_obj_group_dict,acl_entry_dict

def BuildServiceObjects(svc_dict):
    output_list = []
    for service_name in svc_dict.keys():
        output_list.append('object service {0}'.format(service_name))
        output_list.append(' service {0} destination eq {1} \n'.format(svc_dict[service_name]['proto'],svc_dict[service_name]['dst_port']))
    return output_list

def BuildServiceObjectGroups(svc_group_dict):
    output_list = []
    for object_name in svc_group_dict.keys():
        output_list.append('object-group service {0}'.format(object_name))
        output_list.append(' description {0}'.format(svc_group_dict[object_name]['comment']))
        for service in svc_group_dict[object_name]['service']:
            output_list.append(' service-object object {0}'.format(service))
        output_list.append('\n')
    return output_list

def BuildNetworkObjects(net_obj_dict):
    output_list = []
    for object_name in net_obj_dict.keys():
        output_list.append('object network {0}'.format(object_name))
        output_list.append(' description {0}'.format(net_obj_dict[object_name]['desc']))
        output_list.append(' host {0}\n'.format(net_obj_dict[object_name]['ip_addr']))
    return output_list

def BuildNetworkObjectGroups(net_obj_group_dict):
    output_list = []
    for object_name in net_obj_group_dict.keys():
        output_list.append('object-group network {0}'.format(object_name))
        for added_object in net_obj_group_dict[object_name]['added_list']:
            output_list.append(' network-object object {0}\n'.format(added_object))
    return output_list

def BuildACLEntries(acl_entry_dict):
    output_list = []
    for id in acl_entry_dict.keys():
        output_list.append('access-list {0}-IN remark from {1} to {2} policy id {3}'.format(
            acl_entry_dict[id]['from_if'],
            acl_entry_dict[id]['from_if'],
            acl_entry_dict[id]['to_if'],
            id))
        output_list.append('access-list {0}-IN extended {1} object-group {2} object-group {3} object {4}\n'.format(
            acl_entry_dict[id]['from_if'],
            acl_entry_dict[id]['action'],
            acl_entry_dict[id]['dst_port'],
            acl_entry_dict[id]['src_object'],
            acl_entry_dict[id]['dst_object']))
    return output_list

def PrettyOutput(acl_entry_dict):
    for id in acl_entry_dict.keys():
        print('Policy ID:      {0}'.format(id))
        print('From Zone:      {0}'.format(acl_entry_dict[id]['from_if']))
        print('Source(s):      {0}'.format(acl_entry_dict[id]['src_object']))
        print('Destination(s): {0}'.format(acl_entry_dict[id]['dst_object']))
        print('Service(s)    : {0}'.format(acl_entry_dict[id]['dst_port']))
        print('Action:         {0}\n'.format(acl_entry_dict[id]['action']))


def PrintOutput(fn,d):
    for line in fn(d):
        print line

if __name__ == '__main__':
    fn = raw_input("Please enter the source ScreenOS configuration file name: ")
    srcconfig = FileToList(fn)
    svc_dict,svc_group_dict,net_obj_dict,net_obj_group_dict,acl_entry_dict = LineParser(srcconfig)
    PrintOutput(BuildServiceObjects,svc_dict)
    PrintOutput(BuildServiceObjectGroups,svc_group_dict)
    PrintOutput(BuildNetworkObjects,net_obj_dict)
    PrintOutput(BuildNetworkObjectGroups,net_obj_group_dict)
    PrintOutput(BuildACLEntries,acl_entry_dict)
    PrettyOutput(acl_entry_dict)










