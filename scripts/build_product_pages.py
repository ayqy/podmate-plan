#!/usr/bin/env python3
"""Publish only non-sensitive product policy and LGPL material."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
STORE_NAME = 'MeowPodcaster'
INSTALLED_ENGLISH_NAME = 'MeowPodcast'

def document(title, body, digest, locale='zh-Hans', page='privacy'):
    english = locale == 'en'
    suffix = '-en' if english else ''
    other_suffix = '' if english else '-en'
    navigation = (f'<a href="privacy{suffix}.html">' + ('Privacy' if english else '隐私说明') + '</a>'
        + f'<a href="support{suffix}.html">' + ('Support' if english else '产品支持') + '</a>'
        + f'<a href="{page}{other_suffix}.html" hreflang="' + ('zh-Hans' if english else 'en')
        + '" lang="' + ('zh-Hans' if english else 'en') + '">' + ('简体中文' if english else 'English') + '</a>')
    return f'''<!doctype html>
<html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="podmate-policy-sha256" content="{digest}"><title>{html.escape(title)}</title>
<style>body{{font:1rem/1.75 system-ui,sans-serif;margin:0;background:#f6f7fb;color:#20243b}}main{{max-width:46rem;margin:auto;padding:2rem 1.25rem}}h1{{line-height:1.3}}h2{{margin-top:2rem;font-size:1.3rem}}a{{color:#343bac;overflow-wrap:anywhere}}nav{{display:flex;gap:1.5rem;flex-wrap:wrap}}p{{overflow-wrap:anywhere}}@media(prefers-color-scheme:dark){{body{{background:#191c2b;color:#e9ebf6}}a{{color:#b3baff}}}}</style></head>
<body><main><nav>{navigation}</nav>{body}</main></body></html>
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
    support = '''<h1>妙啊播客 产品支持</h1>
<p>妙啊播客（MeowPodcast，项目名 Podmate）用于访谈、文章播客与口才练习。此页面提供使用、隐私和第三方许可支持；应用上架状态以 App Store 为准。</p>
<h2>语言与本机配音</h2><p>界面提供 System、English、简体中文选择，并保存手动选择。本机文章配音目前使用中文音色；切换界面语言不会翻译用户原文。播客成品支持 MP3 与 WAV 分享。</p>
<h2>提交问题</h2><p>通过 <a href="https://github.com/ayqy/podmate-plan/issues">公开问题页面</a>联系维护者 ayqy。请提供应用版本、设备与系统版本、操作步骤和不含隐私的错误说明。</p>
<p>请勿提交 API Key、密码、私人原声、整份工程或未经授权内容。公开问题任何人可见；截图请先移除个人信息。</p>
<h2>隐私与原件</h2><p>项目默认保存在本机；可选上传和远端副本边界见<a href="privacy.html">隐私说明</a>。不要为了排查问题删除唯一原件或备份。</p>
<h2>第三方许可与源码</h2><p>MP3 编码使用 LAME。<a href="third-party-notices.txt">许可与上游授权全文</a>、<a href="lame-source.zip">当前集成的 LAME 库源码</a>及<a href="lame-source-manifest.json">源码摘要清单</a>可直接下载。</p>
<p>若需要替换所用 LAME 库或获取重链接资料，请通过支持渠道联系维护者。</p>'''
    contact = json.loads((DOCS / 'support-contact.json').read_text())
    assert set(contact) == {'email'} and re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+', contact['email'])
    address = html.escape(contact['email'], quote=True)
    support = support.replace('<h2>提交问题</h2>',
        f'<h2>联系支持</h2><p>产品使用与隐私问题请发送至 <a href="mailto:{address}">{address}</a>。请勿发送密码、API Key或私人原声。</p>\n<h2>提交问题</h2>')
    support = support.replace(
        '<p>若需要替换所用 LAME 库或获取重链接资料，请通过支持渠道联系维护者。</p>',
        '<p><a href="relinking.html">下载对应版本的 LAME 替换重链接材料</a>，包括库源码、许可、应用对象、资源和构建说明。</p>')
    relinking = json.loads((DOCS / 'relinking-manifest.json').read_text())
    assert relinking['bundle_id'] == 'com.ayqy.podmate'
    assert relinking['version'] == '1.0.0' and re.fullmatch('[1-9][0-9]*', relinking['build'])
    assert re.fullmatch('[a-f0-9]{40}', relinking['source_commit'])
    material = [f'<h1>LAME 源码与替换材料</h1><p>Podmate {relinking["version"]}（{relinking["build"]}）</p>',
        '<p>你可以依据 LGPL 复制、修改和重新链接 LAME。Podmate 允许个人使用的库修改，以及为调试这些库修改而对应用进行逆向工程。</p>',
        '<p>下面的材料包括此版本的 LAME 源码及许可、实际交付的非库对象、必要资源、编译链接脚本和逐文件摘要；不含应用私有源码、用户项目或 Apple 签名凭据。</p>']
    platforms = set()
    for package in relinking['packages']:
        assert package['platform'] in {'iphoneos', 'iphonesimulator'}
        assert package['architecture'] in {'arm64', 'x86_64'}
        assert package['url'].startswith(f'https://github.com/ayqy/podmate-plan/releases/download/lame-relink-{relinking["version"]}-{relinking["build"]}/')
        assert re.fullmatch('[a-f0-9]{64}', package['sha256'])
        platforms.add(package['platform'])
        label = 'iOS 设备' if package['platform'] == 'iphoneos' else 'iOS 模拟器'
        material.append(f'<h2>{label} · {html.escape(package["architecture"])}</h2>'
            f'<p><a href="{html.escape(package["url"], quote=True)}">下载重新链接包</a> · {package["size"] / 1048576:.1f} MB</p>'
            f'<p>SHA-256：<code>{package["sha256"]}</code></p>')
    assert platforms == {'iphoneos', 'iphonesimulator'}
    material.extend([
        '<h2>使用材料</h2><p>需要与包内架构匹配的 Mac、Xcode 26.5、对应 Apple SDK 与 Python 3。先按包内 README 核验，再修改 LAME 并运行编译链接脚本。</p>',
        '<p>重新链接会使原 App Store 签名失效。模拟器包使用临时本地签名；设备包需要你自己的开发签名与描述文件。平台安装和 StoreKit 条件仍适用。</p>',
        '<p>非库对象与资源用于重新链接本应用，不授权其他应用源码。LAME 的授权范围按包内 COPYING 与 LICENSE 原文执行。</p>',
        f'<p>对应应用源码提交：<code>{relinking["source_commit"]}</code></p>',
        '<p><a href="relinking-manifest.json">下载摘要清单</a> · <a href="third-party-notices.txt">许可全文</a></p>'])
    result = {'privacy.html': document(policy['title'], ''.join(parts), digest),
              'support.html': document('妙啊播客 产品支持', support, digest, page='support'),
              'relinking.html': document('妙啊播客 LAME 替换材料', ''.join(material), digest, page='relinking')}
    translated_raw = (DOCS / 'privacy-policy-en.json').read_bytes()
    translated = json.loads(translated_raw)
    assert translated['schemaVersion'] == policy['schemaVersion']
    assert translated['revision'] == policy['revision']
    assert [x['id'] for x in translated['sections']] == [x['id'] for x in policy['sections']]
    assert [x['url'] for x in translated['references']] == [x['url'] for x in policy['references']]
    en_privacy_title = f'{STORE_NAME} Privacy Statement'
    en_parts = [f'<h1>{html.escape(en_privacy_title)}</h1>',
                f'<p>{STORE_NAME} is the App Store name of {INSTALLED_ENGLISH_NAME} (project name: Podmate). This statement covers the same app and its data practices.</p>',
                f'<p>{html.escape(translated["summary"])}</p>',
                f'<p>Updated: {html.escape(translated["revision"])}</p>']
    for section in translated['sections']:
        en_parts.append(f'<h2 id="{html.escape(section["id"], quote=True)}">{html.escape(section["title"])}</h2>')
        en_parts.extend(f'<p>{html.escape(paragraph)}</p>' for paragraph in section['paragraphs'])
    en_parts.append('<h2>Related information</h2><p><a href="third-party-notices.txt">Third-party licenses</a></p>')
    en_parts.extend(f'<p><a href="{html.escape(x["url"], quote=True)}">{html.escape(x["title"])}</a></p>'
                    for x in translated['references'])
    en_support = f'''<h1>{STORE_NAME} Support</h1>
<p>{STORE_NAME} (on-device name: {INSTALLED_ENGLISH_NAME}; project name: Podmate) helps you create interviews and article podcasts, and practise speaking. App availability is determined by its App Store listing.</p>
<h2>Language and on-device narration</h2><p>Choose System, English or 简体中文 in Settings. Your explicit choice is saved. On-device article narration currently uses Chinese voices; changing the interface language does not translate your original text. Finished podcasts can be shared as MP3 or WAV.</p>
<h2>Contact support</h2><p>For product or privacy questions, email <a href="mailto:{address}">{address}</a>. Do not send passwords, API keys or private recordings.</p>
<p>You can also use the <a href="https://github.com/ayqy/podmate-plan/issues">public issue tracker</a> to contact maintainer ayqy. Include the app version, device, OS version, steps and a description without personal information. Public issues are visible to everyone; remove personal information from screenshots.</p>
<h2>Privacy and originals</h2><p>Projects are stored on your device by default. Optional uploads and remote copies are explained in the <a href="privacy-en.html">privacy policy</a>. Keep your only originals and backups when troubleshooting.</p>
<h2>Third-party licenses and source</h2><p>MP3 encoding uses LAME. Download the <a href="third-party-notices.txt">license notices</a>, <a href="lame-source.zip">integrated LAME source</a> and <a href="relinking-en.html">version-matched relinking materials</a>. These materials include library source, licenses, application objects, resources and build instructions.</p>'''
    en_material = [f'<h1>LAME source and relinking materials</h1><p>{STORE_NAME} {relinking["version"]} (build {relinking["build"]}), shown as {INSTALLED_ENGLISH_NAME} on your device</p>',
        '<p>You may copy, modify and relink LAME under the LGPL. Podmate permits library modifications for your own use and reverse engineering to debug those modifications.</p>',
        '<p>The packages contain corresponding LAME source and licenses, actual non-library application objects, required resources, build scripts and file digests. They do not contain private application source, user projects or Apple signing credentials.</p>']
    for package in relinking['packages']:
        label = 'iOS device' if package['platform'] == 'iphoneos' else 'iOS Simulator'
        en_material.append(f'<h2>{label} · {package["architecture"]}</h2><p><a href="{html.escape(package["url"], quote=True)}">Download relinking package</a> · {package["size"] / 1048576:.1f} MB</p><p>SHA-256: <code>{package["sha256"]}</code></p>')
    en_material.extend([
        '<h2>Using these materials</h2><p>Use a Mac matching the package architecture, Xcode 26.5, the corresponding Apple SDK and Python 3. Verify the package using its README before modifying LAME and running the build scripts.</p>',
        '<p>Relinking invalidates the original App Store signature. Simulator packages use a temporary local signature. Device packages require your own development signing identity and provisioning profile. Platform installation and StoreKit requirements still apply.</p>',
        '<p>Non-library objects and resources are supplied for relinking this application; they do not license other application source. LAME licensing is governed by the included COPYING and LICENSE files.</p>',
        f'<p>Application archive source revision: <code>{relinking["source_commit"]}</code>. Individual package manifests record their packaging revisions.</p>',
        '<p><a href="relinking-manifest.json">Download digest manifest</a> · <a href="third-party-notices.txt">License notices</a></p>'])
    en_digest = hashlib.sha256(translated_raw).hexdigest()
    result.update({'privacy-en.html': document(en_privacy_title, ''.join(en_parts), en_digest, 'en'),
                   'support-en.html': document(f'{STORE_NAME} Support', en_support, digest, 'en', 'support'),
                   'relinking-en.html': document(f'{STORE_NAME} LAME relinking materials', ''.join(en_material), digest, 'en', 'relinking')})
    return result

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
