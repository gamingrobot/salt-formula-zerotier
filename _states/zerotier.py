# -*- coding: utf-8 -*-
'''
Zerotier state

For managing zero tier things

Config Options:

hidden:bool - Hidden in UI
name:string - Short name describing member
description:string - Long form description
offlineNotifyDelay:number - Notify of offline after this many milliseconds

authorized:bool - True if authorized (only matters on private networks)
capabilities:array - Array of IDs of capabilities assigned to this member
tags:array - Array of tuples of tag ID, tag value
ipAssignments:array - Array of IP assignments published to member
noAutoAssignIps:bool - If true do not auto-assign IPv4 or IPv6 addresses, overriding 

.. code-block:: yaml

    zerotier-membership:
      zerotier.joined:
        - network_id: abc
      zerotier.central_member:
        - network_id: abc
        - api_key: xyz
        - config:
            name: testing
            description: "hello world"
            authorized: True
'''

from __future__ import absolute_import, generators, print_function, with_statement, unicode_literals
import logging

# Import python libs
import os.path

# Import Salt libs
import salt.utils

log = logging.getLogger(__name__)

def joined(name, network_id):
    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}

    if network_id == None:
        raise SaltInvocationError('network_id is required')

    network_state = __salt__['zerotier.network_info'](network_id)

    if network_state != None and network_state['status'] != "ACCESS_DENIED":
        ret['result'] = True
        ret['comment'] = 'Already joined network'
        return ret
    elif __opts__['test']:
        ret['comment'] = 'Will join network'
        ret['result'] = None
        return ret

    joined_state = __salt__['zerotier.network_join'](network_id)
    if joined_state != None:
        ret['changes'] = {
            'old': network_state,
            'new': joined_state
        }
        ret['result'] = True
        ret['comment'] = 'Successfully joined network'
    else:
        ret['result'] = False
        ret['comment'] = 'Failed to join network'

    return ret


def central_member(name, network_id, api_key, config):
    ret = {'name': name,
           'changes': {},
           'result': None,
           'comment': ''}


    if network_id == None:
        raise SaltInvocationError('network_id is required')
    
    if api_key == None:
        raise SaltInvocationError('api_key is required')

    if __opts__['test']:
        ret['comment'] = 'Will update central member'
        ret['changes'].update({'member': {'old': '', 'new': config}})
        ret['result'] = None
        return ret

    original_member_info = __salt__['zerotier.central_get_member'](network_id, api_key)

    #TODO: check values and see if we even need to update

    member_info = __salt__['zerotier.central_update_member'](network_id, api_key, **config)

    #Do a diff, prob a better way to do this
    diff = {'old': {}, 'new': {}}

    root_keys = ['hidden', 'name', 'description', 'offlineNotifyDelay']
    config_keys = ['authorized', 'capabilities', 'tags', 'ipAssignments', 'noAutoAssignIps']

    for key in root_keys:
        old = None
        new = None
        if key in original_member_info:
            old = original_member_info[key]
        if key in member_info:
            new = member_info[key]
        if old != new:
            diff['old'][key] = old
            diff['new'][key] = new

    for key in config_keys:
        old = None
        new = None
        if key in original_member_info.get('config', {}):
            old = original_member_info['config'][key]            
        if key in member_info.get('config', {}):
            new = member_info['config'][key]
        if old != new:
            diff['old'][key] = old
            diff['new'][key] = new

    if not diff['old'] and not diff['new']:
        ret['result'] = True
        ret['comment'] = 'Central Member is up to date'
    else:
        #just some visual cleanup if empty dict
        if not diff['old']:
            diff['old'] = None
        if not diff['new']:
            diff['new'] = None
        ret['changes'] = diff
        ret['result'] = True
        ret['comment'] = 'Updated central member'

    return ret