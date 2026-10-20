# Example data

Examples in this repository are synthetic. No personal contact exports are included.

For a quick test, create a local `demo.vcf` file from the following **fictional** record:

```text
BEGIN:VCARD
VERSION:2.1
N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:;=E6=B5=8B=E8=AF=95;;;
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=E6=B5=8B=E8=AF=95
TEL;CELL:00000000000
END:VCARD
```

Run `python fix_vcard.py demo.vcf`, then inspect `demo_icloud.vcf`.
