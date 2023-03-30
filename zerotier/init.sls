zerotier-pkgrepo:
  pkgrepo.managed:
    - humanname: ZeroTier Ubuntu Repo
    - name: deb [signed-by=/etc/apt/keyrings/zerotier.gpg] https://download.zerotier.com/debian/{{ salt.cmd.run('lsb_release -cs') }} {{ salt.cmd.run('lsb_release -cs') }} main
    - file: /etc/apt/sources.list.d/zerotier.list
    - key_url: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x1657198823E52A61
    - aptkey: False
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