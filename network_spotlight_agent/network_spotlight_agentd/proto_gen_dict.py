#/usr/bin/env python
import re 
import json

def main():
    mpa = {}
    protocols = {}
    protoname_from_id = {}
    current_proto = ''
    for l in open('protodef.proto').read().split('\n'):
        m_mpa = re.search('^  \(mpa ([a-zA-Z]*) ([\-0-9]*)\)$', l)
        m_proto = re.search('^  \(proto ([a-zA-Z]*) ([\-0-9]*)$', l)
        m_proto_attr = re.search('^    \(([a-zA-Z]*) ([\-0-9]*)\)$', l)
        m_proto_attr_mpa = re.search('^    \(([a-zA-Z]*) mpa\)$', l)
        if m_mpa:
            mpa[m_mpa.group(1)] = int(m_mpa.group(2))
        if m_proto:
            current_proto = m_proto.group(1)
            protoname_from_id[int(m_proto.group(2))] = m_proto.group(1)
            protocols[current_proto] = {'id': int(m_proto.group(2)), 'attr': {}}
        if m_proto_attr:
            protocols[current_proto]['attr'][m_proto_attr.group(1)] = int(m_proto_attr.group(2))
        if m_proto_attr_mpa:
            protocols[current_proto]['attr'][m_proto_attr_mpa.group(1)] = mpa[m_proto_attr_mpa.group(1)]

    print  json.dumps(protocols, sort_keys=True, indent=4)
    print  json.dumps(protoname_from_id, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
