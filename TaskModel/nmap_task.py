import nmap


def main(target_port, port_type='TCP'):
    target = target_port.split(':')[0]
    port = int(target_port.split(':')[1])

    white_list = ['java-rmi', 'ftp', 'ssh', 'sftp', 'telnet', 'tftp', 'rpc', 'netbios', 'xmanager', 'xwin', 'ldap',
                  'rlogin', 'sql', 'oracle', 'rdp', 'remoteadmin', 'x11', 'tcp_napster_directory_8888_primary', 'db2',
                  'gaussdb', 'essbase', 'oracle-tns', 'mysql', 'sybase', 'sybasedbsynch', 'sybasesrvmon', 'postgresql',
                  'redis', 'mongodb', 'sap hana', 'hbase', 'hbase-managed', 'hive']

    port_type = 'TCP' if port_type.upper() not in ['TCP', 'UDP'] else port_type

    result_data = {'ip': target, 'port': port, 'port_type': port_type}

    nmap_scan = nmap.PortScanner()
    nmap_args = '-sS -sV -sU -Pn --max-retries 3 --min-rtt-timeout 500ms --max-rtt-timeout 3000ms'
    nmap_args += ' --initial-rtt-timeout 500ms --defeat-rst-ratelimit --min-rate 10000 --max-rate 15000'

    try:
        target = target.replace('"', '')
        scan_result = nmap_scan.scan(hosts='"{}"'.format(target),
                                     ports='{}:{}'.format('U' if port_type.upper() == 'UDP' else 'T', port),
                                     arguments=nmap_args)
        try:
            port_info = scan_result['scan'][target]
        except Exception as e:
            print(e)
            domain_ip = list(scan_result['scan'].keys())[0]
            port_info = scan_result['scan'].get(domain_ip, {})

        result_data['hostname'] = str(port_info.get('hostnames', {}))
        result_data['vendor'] = str(port_info.get('vendor', {}))
        port_type_info = port_info.get(port_type.lower(), {}).get(port, {})
        result_data['state'] = port_type_info.get('state', '')

        if 'open' not in result_data['state']:
            return None

        result_data['version'] = port_type_info.get('version', '')
        result_data['service_name'] = port_type_info.get('name', '')
        result_data['application'] = port_type_info.get('product', '')
        result_data['extra_info'] = port_type_info.get('extrainfo', '')
        result_data['cpe'] = port_type_info.get('cpe', 'cpe:/n:unknown:unknown')
        result_data['vendor'] = (result_data['cpe'] + '::::').split(':')[2]

        application_temp = result_data['application'].lower()
        if any(item in application_temp for item in white_list):
            result_data['remarks'] = 'risk port'
        else:
            result_data['remarks'] = ''

        return result_data
    except Exception as e:
        print(e,
              e.__traceback__.tb_lineno,
              e.__traceback__.tb_frame.f_globals["__file__"])
        pass
    return None


if __name__ == '__main__':
    print(main('1.112.2.229:443', port_type='TCP'))
