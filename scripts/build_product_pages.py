#!/usr/bin/env python3
"""Publish only non-sensitive product policy and LGPL material."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

def document(title, body, digest):
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="podmate-policy-sha256" content="{digest}"><title>{html.escape(title)}</title>
<style>body{{font:1rem/1.75 system-ui,sans-serif;margin:0;background:#f6f7fb;color:#20243b}}main{{max-width:46rem;margin:auto;padding:2rem 1.25rem}}h1{{line-height:1.3}}h2{{margin-top:2rem;font-size:1.3rem}}a{{color:#343bac;overflow-wrap:anywhere}}nav{{display:flex;gap:1.5rem;flex-wrap:wrap}}p{{overflow-wrap:anywhere}}@media(prefers-color-scheme:dark){{body{{background:#191c2b;color:#e9ebf6}}a{{color:#b3baff}}}}</style></head>
<body><main><nav><a href="privacy.html">隐私说明</a><a href="support.html">产品支持</a></nav>{body}</main></body></html>
'''

def outputs():
    raw = (DOCS / 'privacy-policy.json').read_bytes()
    policy = json.loads(raw)
    assert policy['schemaVersion'] == 1
    assert {x['id'] for x in policy['sections']} == {'local', 'cloud', 'backup', 'permissions', 'network', 'retention', 'support'}
    digest = hashlib.sha256(raw).hexdigest()
    parts = [f"<h1>{html.escape(policy['title'])}</h1>", f"<p>{html.escape(policy['summary'])}</p>", f"<p>更新：{html.escape(policy['revision'])}</p>"]
    for section in policy['sections']:
        parts.append(f"<h2 id=\"{html.escape(section['id'], quote=True)}\">{html.escape(section['title'])}</h2>")
        parts.extend(f"<p>{html.escape(paragraph)}</p>" for paragraph in section['paragraphs'])
    parts.append('<h2>相关链接</h2><p><a href="third-party-notices.txt">第三方许可全文</a></p>')
    for reference in policy['references']:
        assert reference['url'].startswith('https://')
        parts.append(f"<p><a href=\"{html.escape(reference['url'], quote=True)}\">{html.escape(reference['title'])}</a></p>")
    source = json.loads((DOCS / 'lame-source-manifest.json').read_text())
    with zipfile.ZipFile(DOCS / 'lame-source.zip') as archive:
        assert set(archive.namelist()) == set(source['files'])
        for name, expected in source['files'].items():
            assert name.startswith('LAME/') and '..' not in Path(name).parts
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
    support = '''<h1>Podmate 产品支持</h1>
<p>Podmate 用于访谈、文章播客与口才练习。此页面提供使用、隐私和第三方许可支持；应用上架状态以 App Store 为准。</p>
<h2>提交问题</h2><p>通过 <a href="https://github.com/ayqy/podmate-plan/issues">公开问题页面</a>联系维护者 ayqy。请提供应用版本、设备与系统版本、操作步骤和不含隐私的错误说明。</p>
<p>请勿提交 API Key、密码、私人原声、整份工程或未经授权内容。公开问题任何人可见；截图请先移除个人信息。</p>
<h2>隐私与原件</h2><p>项目默认保存在本机；可选上传和远端副本边界见<a href="privacy.html">隐私说明</a>。不要为了排查问题删除唯一原件或备份。</p>
<h2>第三方许可与源码</h2><p>MP3 编码使用 LAME。<a href="third-party-notices.txt">许可与上游授权全文</a>、<a href="lame-source.zip">当前集成的 LAME 库源码</a>及<a href="lame-source-manifest.json">源码摘要清单</a>可直接下载。</p>
<p>若需要替换所用 LAME 库或获取重链接资料，请通过支持渠道联系维护者。</p>'''
    return {'privacy.html': document(policy['title'], ''.join(parts), digest), 'support.html': document('Podmate 产品支持', support, digest)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in outputs().items():
        path = DOCS / name
        if args.check:
            assert path.is_file() and path.read_text() == content, f'{name} is not current'
        else:
            path.write_text(content)
    print(json.dumps({'policy_pages_current': True, 'source_archive_verified': True, 'check_only': args.check}))

if __name__ == '__main__':
    main()
