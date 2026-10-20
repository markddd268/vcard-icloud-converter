#!/usr/bin/env python3
"""Convert old vCard 2.1 exports to iCloud-friendly vCard 3.0, omitting photos.
Usage: python fix_vcard.py input.vcf [output.vcf]
"""
import argparse
import quopri
import re
from pathlib import Path


def unfold(lines):
    """Unfold vCard folding and quoted-printable soft line breaks."""
    result = []
    for line in lines:
        line = line.rstrip('\r\n')
        if result and (line.startswith((' ', '\t')) or result[-1].endswith('=')):
            # For QP soft break, strip the trailing =. For standard vCard folds,
            # remove only the one whitespace character used for folding.
            if result[-1].endswith('='):
                result[-1] = result[-1][:-1] + line.lstrip(' \t')
            else:
                result[-1] += line[1:]
        else:
            result.append(line)
    return result


def decode_value(params, value):
    charset = re.search(r'(?:^|;)CHARSET=([^;:]+)', params, flags=re.I)
    encoding = re.search(r'(?:^|;)ENCODING=([^;:]+)', params, flags=re.I)
    if encoding and encoding.group(1).upper() in ('QUOTED-PRINTABLE', 'QP'):
        raw = quopri.decodestring(value.encode('ascii', errors='replace'))
        return raw.decode(charset.group(1) if charset else 'utf-8', errors='replace')
    return value


def escape_value(value):
    # Already-escaped backslashes may exist, so unescape first to avoid double escaping.
    value = re.sub(r'\\([nN,;\\])', lambda m: '\n' if m.group(1).lower() == 'n' else m.group(1), value)
    return value.replace('\\', '\\\\').replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;')


def convert(text):
    lines = unfold(text.splitlines())
    contacts = []
    current = None
    for line in lines:
        if line.upper() == 'BEGIN:VCARD':
            current = []
        elif line.upper() == 'END:VCARD':
            if current is not None:
                contacts.append(current)
            current = None
        elif current is not None:
            current.append(line)

    output = []
    for card in contacts:
        name = ''
        structured_name = ''
        fields = []
        for line in card:
            if ':' not in line:
                continue
            left, value = line.split(':', 1)
            parts = left.split(';')
            key = parts[0].upper().split('.')[-1]
            params = ';'.join(parts[1:])
            if key in ('BEGIN', 'END', 'VERSION', 'PHOTO', 'LOGO', 'SOUND', 'REV', 'PRODID'):
                continue
            value = decode_value(params, value)
            if key == 'FN':
                name = value
            elif key == 'N':
                structured_name = value
            elif key in ('TEL', 'EMAIL', 'ORG', 'TITLE', 'URL', 'NOTE', 'BDAY'):
                # Rewrite old TYPE syntax (e.g. TEL;CELL and TEL;TYPE=CELL).
                types = []
                for p in parts[1:]:
                    if p.upper().startswith(('CHARSET=', 'ENCODING=')):
                        continue
                    if p.upper().startswith('TYPE='):
                        types.extend(p[5:].split(','))
                    elif '=' not in p:
                        types.append(p)
                suffix = ';TYPE=' + ','.join(t.upper() for t in types if t) if types else ''
                fields.append((key + suffix, value))
        if not name and structured_name:
            name = ' '.join(p for p in structured_name.split(';')[:2] if p).strip()
        if not name:
            phone = next((v for k, v in fields if k.startswith('TEL')), '')
            name = phone or '未命名联系人'
        # Use the display name as the family-name component. Apple Contacts accepts it.
        record = ['BEGIN:VCARD', 'VERSION:3.0', 'N:' + escape_value(name) + ';;;;', 'FN:' + escape_value(name)]
        for key, value in fields:
            if value.strip():
                record.append(key + ':' + escape_value(value))
        record.append('END:VCARD')
        output.extend(record)
    return '\r\n'.join(output) + ('\r\n' if output else ''), len(contacts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('output', nargs='?', type=Path)
    args = ap.parse_args()
    dest = args.output or args.input.with_name(args.input.stem + '_icloud.vcf')
    raw = args.input.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('gb18030')
    converted, count = convert(text)
    if not count:
        raise SystemExit('未找到 BEGIN:VCARD / END:VCARD 联系人块')
    dest.write_bytes(converted.encode('utf-8'))
    print(f'已转换 {count} 个联系人，未保留头像。输出文件：{dest}')


if __name__ == '__main__':
    main()
