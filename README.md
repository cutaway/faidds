# faidds
Forensic Acquisition Information and Drive Data Script (faidds).

```
faidds.py [-h] [-D] [-dcfldd] [-m hash0,hash1] [-c size in G (1024*1024*1024)] [-s \"serial number\"] -d \"drive location\"'
    -h: help'
    -D: debug information'
    -s: user specified serial number. Default is to find serial number in drive info.'
    -d: device file to acquire'
    -c: size to split file in G (1024*1024*1024)'
    -dcfldd: use dcfldd (default: dc3dd)'
    -m: list of hash algorithms to use. Comma separated with no spaces. (default: md5)'
```
