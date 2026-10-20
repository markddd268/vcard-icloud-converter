# vCard to iCloud Converter

将旧版 vCard 2.1 通讯录转换为 UTF-8 编码的 vCard 3.0，移除联系人头像，方便尝试导入 iCloud 通讯录。

## 特性

- 支持旧版 vCard 2.1 中的 `QUOTED-PRINTABLE` 中文姓名
- 清除 `PHOTO`、`LOGO` 和 `SOUND` 字段
- 转换常见字段：姓名、电话、邮箱、公司、职位、网址、备注、生日
- 没有姓名的联系人使用电话号码或“未命名联系人”补充
- 完全本地运行，不上传联系人信息
- 仅依赖 Python 标准库

> 注意：这是一个针对常见旧式导出文件的轻量转换器，并非完整的 vCard 标准解析器。部分扩展字段（如地址、群组、自定义属性）不会被保留。建议先备份原文件，并用少量联系人确认导入效果。此工具不保证所有 vCard 导出格式都兼容 iCloud。

## 使用

需要 Python 3.9+。

```bash
python fix_vcard.py contacts.vcf
```

默认输出 `contacts_icloud.vcf`，也可指定文件名：

```bash
python fix_vcard.py contacts.vcf cleaned.vcf
```

随后在 [iCloud 通讯录](https://www.icloud.com/contacts/) 中尝试导入转换后的 VCF。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 隐私与脱敏

本仓库**不包含任何真实通讯录、手机号、邮箱、联系人头像或用户上传的数据**。`examples/` 内只有人工编造的测试数据。`.gitignore` 默认忽略 `.vcf`、`.vcard`、常见通讯录导出格式和转换产物，避免误提交。

**提交前请再次检查 `git status` 和 `git diff --cached`，尤其是强制添加 (`git add -f`) 或修改 `.gitignore` 后。**

## 许可证

MIT
