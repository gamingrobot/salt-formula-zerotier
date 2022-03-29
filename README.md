# Salt Formula ZeroTier

Salt Formula for ZeroTier https://www.zerotier.com/

This is an unofficial salt formula for ZeroTier, its not perfect but does function.

## Notes

* Only works on Ubuntu
* Requires two runs of highstate to fully initialize a new server

## Sample pillar

```yaml
zerotier:
  network_id: <network_id>
  api_key: <api_key>
```