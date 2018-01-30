import json

print("Start writing FNCS_VOLTTRON_Bridge.config based on fncs_configure.cfg")

# dp = open('FNCS_VOLTTRON_Bridge.config', 'w')
ip = open ("fncs_configure.txt", "r")

# Start writing config file
config = {}
fncs_zpl = {}
values = {}
remote_platform_params = {}
config['simulation_run_time'] = '24h'
config['heartbeat_period'] = 1
config['heartbeat_multiplier'] = 1 # 60
# Start defining fncs_zpl based on glm config file
fncs_zpl['name'] = 'FNCS_Volttron_Bridge'
fncs_zpl['time_delta'] = '1s' # 60s
fncs_zpl['broker'] = 'tcp://localhost:5570'

# Loop through the file fncs_configure.cfg
index = 1
for line in ip:
    if ('->' in line):
        dict = {}
        lst = line.split('-> ')
        temp = lst[1].split(';')
        dict['topic'] = 'fncs_Test/' + temp[0]
        dict['default'] = '0'
        dict['type'] = 'double'
        dict['list'] = 'fasle'
        values[str(index)] = dict
        index += 1
ip.close()
  
fncs_zpl['values'] = values
config['fncs_zpl'] = fncs_zpl

# write remote_platform_params
remote_platform_params['vip_address'] = 'tcp://127.0.0.1'
remote_platform_params['port'] = 22916
remote_platform_params['agent_public'] = 'cDc4_Lli13dt-__ju-vpgAeOEbbRPaOVzQoeQ5KHjUk'
remote_platform_params['agent_secret'] = 'k19_VwSSfbFUzm4Op3DGBlOH6Vd7rMJWy4iQo_t-wuw'
remote_platform_params['server_key'] = 'XDMM3_KrXqSaaPXEM3vL7rumk4nd-A30dcksjfFWNyM'
config['remote_platform_params'] = remote_platform_params

# Write the dictionary into JSON file
with open('../FncsVolttronBridge/FNCS_VOLTTRON_Bridge.config', 'w') as outfile:
    json.dump(config, outfile)

print("Finish writing FNCS_VOLTTRON_Bridge.config based on fncs_configure.cfg")

