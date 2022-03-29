zerotier-pkgrepo:
  pkgrepo.managed:
    - humanname: ZeroTier Ubuntu Repo
    - name: {{ 'deb https://download.zerotier.com/debian/' + salt['grains.get']('oscodename') + ' ' + salt['grains.get']('oscodename') + ' main'}}
    - file: /etc/apt/sources.list.d/zerotier.list
    - key_url: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x1657198823E52A61
    - clean_file: True
    - require_in:
      - pkg: zerotier

zerotier:
  pkg.installed:
    - name: zerotier-one
  service.running:
    - name: zerotier-one
    - enable: True
    - require:
      - pkg: zerotier

zerotier-joined:
  zerotier.joined:
    - network_id: {{ salt['pillar.get']('zerotier:network_id') }}

zerotier-member:
  zerotier.central_member:
    - network_id: {{ salt['pillar.get']('zerotier:network_id') }}
    - api_key: {{ salt['pillar.get']('zerotier:api_key') }}
    - config:
        name: {{ salt['grains.get']('host') }}
        authorized: True
    - onchanges:
      - zerotier: zerotier-joined