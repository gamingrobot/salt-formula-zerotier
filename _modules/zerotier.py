# -*- coding: utf-8 -*-
'''
Zerotier
'''

# Import python libs
from __future__ import absolute_import, generators, print_function, with_statement, unicode_literals
import logging
import json

# Import 3rd-party libs
# pylint: disable=import-error,no-name-in-module,redefined-builtin
from salt.ext.six.moves.urllib.parse import urljoin as _urljoin
import salt.ext.six.moves.http_client
# pylint: enable=import-error,no-name-in-module

# Import salt libs
import salt.utils
import salt.utils.http
import salt.utils.path
import salt.utils.stringutils

log = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load the module if zerotier is installed
    '''
    if salt.utils.path.which("zerotier-cli"):
        return 'zerotier'
    return (False, 'The zerotier execution module cannot be loaded: zerotier is not installed.')

def version():
    '''
    Return version (``zerotier-cli -v``)

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.version
    '''
    cmd = 'zerotier-cli -v'
    ret = __salt__['cmd.run'](cmd)
    return ret

def node_id():
    '''
    Return node id

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.node_id
    '''
    cmd = 'zerotier-cli -j info'
    out = __salt__['cmd.run'](cmd)
    info = json.loads(salt.utils.stringutils.to_str(out))
    node_address = info["address"]
    return node_address


def info(network_id):
    '''
    Info (``zerotier-cli info``)

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.info
    '''
    cmd = 'zerotier-cli -j info'
    out = __salt__['cmd.run'](cmd)

    ret = json.loads(salt.utils.stringutils.to_str(out))
    return ret

def network_info(network_id):
    '''
    Network Info

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.network_info <network_id>
    '''
    cmd = 'zerotier-cli -j listnetworks'
    out = __salt__['cmd.run'](cmd)
    decoded = json.loads(salt.utils.stringutils.to_str(out))
    ret = next((n for n in decoded if n['id'] == network_id), None)
    return ret

def network_join(network_id):
    '''
    Join network (``zerotier-cli join <network_id>``)

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.network_join <network_id>
    '''
    cmd = 'zerotier-cli -j join {0}'.format(network_id)
    out = __salt__['cmd.run'](cmd)
    ret = json.loads(salt.utils.stringutils.to_str(out))
    return ret

def network_leave(network_id):
    '''
    Leave network (``zerotier-cli leave <network_id>``)

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.network_leave <network_id>
    '''
    cmd = 'zerotier-cli -j leave {0}'.format(network_id)
    out = __salt__['cmd.run'](cmd)
    ret = json.loads(salt.utils.stringutils.to_str(out))
    return ret


def central_get_member(network_id, api_key=None):
    '''
    Get information about network memeber

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.central_get_member <network_id> <api_key>
    '''

    nodeId = node_id()

    base_url = 'https://my.zerotier.com'
    url = _urljoin(base_url, '/api/network/{networkId}/member/{nodeId}'.format(networkId=network_id, nodeId=nodeId))
    headers = {'Authorization': "Bearer {0}".format(api_key), 'Content-type': 'application/json'}
    member_info_raw = salt.utils.http.query(
        url,
        'GET',
        text=True,
        status=True,
        header_dict=headers,
        opts=__opts__
    )
    if member_info_raw['status'] != 200:
        raise Exception(member_info_raw['error'])

    #Handle the fact that the result from this GET may be empty
    if member_info_raw['text']:
        member_info_raw['dict'] = json.loads(salt.utils.stringutils.to_str(member_info_raw['text']))

    return member_info_raw.get('dict', {})
    

def central_update_member(network_id, api_key=None, **config_args):
    '''
    Update information about network memeber

    CLI Example:

    .. code-block:: bash

        salt '*' zerotier.central_update_member <network_id> <api_key> <config_args>


    config_args: 
        hidden:bool - Hidden in UI
        name:string - Short name describing member
        description:string - Long form description
        offlineNotifyDelay:number - Notify of offline after this many milliseconds

        authorized:bool - True if authorized (only matters on private networks)
        capabilities:array - Array of IDs of capabilities assigned to this member
        tags:array - Array of tuples of tag ID, tag value
        ipAssignments:array - Array of IP assignments published to member
        noAutoAssignIps:bool - If true do not auto-assign IPv4 or IPv6 addresses, overriding 
    '''

    nodeId = node_id()

    member_info = central_get_member(network_id, api_key)

    #set properties
    root_keys = ['hidden', 'name', 'description', 'offlineNotifyDelay']
    config_keys = ['authorized', 'capabilities', 'tags', 'ipAssignments', 'noAutoAssignIps']

    for key in root_keys:
        if key in config_args and key in member_info:
            log.debug("Setting root key {0} to {1}".format(key, config_args[key]))
            member_info[key] = config_args[key]
    
    for key in config_keys:
        if key in config_args and key in member_info.get('config', {}):
            log.debug("Setting config key {0} to {1}".format(key, config_args[key]))
            member_info['config'][key] = config_args[key]

    # TODO: check we have network_id and node_id
    base_url = 'https://my.zerotier.com'
    url = _urljoin(base_url, '/api/network/{networkId}/member/{nodeId}'.format(networkId=network_id, nodeId=nodeId))
    headers = {'Authorization': "Bearer {0}".format(api_key), 'Content-type': 'application/json'}

    update_result = salt.utils.http.query(
        url,
        'POST',
        params={},
        data=json.dumps(member_info),
        decode=True,
        status=True,
        header_dict=headers,
        opts=__opts__
    )
    
    if update_result['status'] != 200:
        raise Exception(update_result['error'])
    
    return update_result.get('dict', {})