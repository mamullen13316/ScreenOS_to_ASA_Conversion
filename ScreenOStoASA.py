'''This script will convert a Juniper ScreenOS access rules to the equivalent access-list commands
on the Cisco ASA platform'''

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


def LineParser(srcconfig):
    acl_entry_dict = {}
    for line in srcconfig:
        if ('source-address' in line) or ('destination-address' in line) or ('destination-port' in line):
            s,f,fi,filter_name,t,term_nbr,fr,src,addr = line.split()
            if not filter_name in acl_entry_dict:
                acl_entry_dict[filter_name] = {}
            if not term_nbr in acl_entry_dict[filter_name]:
                acl_entry_dict[filter_name][term_nbr] = {}
            if 'source-address' in line:
                src_ip = addr[:addr.find('/')]
                src_mask = MaskConvert(addr[addr.find('/'):])
                acl_entry_dict[filter_name][term_nbr]['src_ip'] = src_ip
                acl_entry_dict[filter_name][term_nbr]['src_mask'] = src_mask
            if 'destination-address' in line:
                dst_ip = addr[:addr.find('/')]
                dst_mask = MaskConvert(addr[addr.find('/'):])
                acl_entry_dict[filter_name][term_nbr]['dst_ip'] = dst_ip
                acl_entry_dict[filter_name][term_nbr]['dst_mask'] = dst_mask
            if 'destination-port' in line:
                if 'dst_port' not in acl_entry_dict[filter_name][term_nbr]:
                    acl_entry_dict[filter_name][term_nbr]['dst_port'] = []
                acl_entry_dict[filter_name][term_nbr]['dst_port'].append(addr)
        if ('reject' in line) or ('accept' in line):
            s,f,fi,filter_name,t,term_nbr,th,action = line.split()
            if not filter_name in acl_entry_dict:
                acl_entry_dict[filter_name] = {}
            if not term_nbr in acl_entry_dict[filter_name]:
                acl_entry_dict[filter_name][term_nbr] = {}
            if 'reject' in line:
                acl_entry_dict[filter_name][term_nbr]['action'] = 'deny'
            if 'accept' in line:
                acl_entry_dict[filter_name][term_nbr]['action'] = 'permit'
    return acl_entry_dict

def ASASyntaxConversion(src_dict):
    outputlist = []
    for filter_name in src_dict.keys():
        srt_term_nbr = sorted(src_dict[filter_name].keys())
        for term_nbr in srt_term_nbr:
            for dst_port in src_dict[filter_name][term_nbr]['dst_port']:
                src_ip = src_dict[filter_name][term_nbr]['src_ip']
                src_mask = src_dict[filter_name][term_nbr]['src_mask']
                dst_ip = src_dict[filter_name][term_nbr]['dst_ip']
                dst_mask = src_dict[filter_name][term_nbr]['dst_mask']
                action = src_dict[filter_name][term_nbr]['action']
                for udp_port in ['161','snmp','53','dns','123','ntp']:
                    if udp_port in dst_port:
                        proto = 'udp'
                        break
                    else:
                        proto = 'tcp'
                outputlist.append('access-list {0} extended {1} {2} {3} {4} {5} {6} eq {7} '.format(
                    filter_name,action,proto,src_ip,src_mask,dst_ip,dst_mask,dst_port))
    return outputlist

if __name__ == '__main__':
    fn = raw_input("Please enter the source ScreenOS configuration file name: ")
    srcconfig = FileToList(fn)
    config_dict = LineParser(srcconfig)
    output_list = ASASyntaxConversion(config_dict)
    for line in output_list:
        print (line)









