"""Build and validate a NuGet release locally on Windows; never publishes."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NUGET_VERSION = '7.9.0'
REPOSITORY = 'https://github.com/Lou32Verbose/fatcow-icons'


def run(args, **kwargs):
    result = subprocess.run([str(arg) for arg in args], cwd=ROOT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    print(result.stdout, flush=True)
    result.check_returncode()
    if re.search(r'\bwarning\s+[A-Z]+\d+\b|^\s*warning\s*:', result.stdout, re.I | re.M):
        raise RuntimeError('Unexpected warning; review before releasing')
    return result.stdout.strip()


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify_package(package, version, commit):
    expected = {}
    assets = {p.relative_to(ROOT / 'dist').as_posix(): p
              for p in (ROOT / 'dist').rglob('*') if p.is_file()}
    check(sum(name.endswith('.png') and '/png/' in name for name in assets) == 15704,
          'Unexpected PNG count')
    for prefix in ('content/fatcow/', 'contentFiles/any/any/fatcow/'):
        expected.update({prefix + name: path for name, path in assets.items()})
    expected.update({name: ROOT / name for name in ('LICENSE.md', 'NOTICE.md', 'README.md')})
    expected.update({p.relative_to(ROOT).as_posix(): p
                     for p in (ROOT / 'docs').rglob('*') if p.is_file()})
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        check(len(names) == len(set(names)), 'Duplicate archive entries')
        payload = {name for name in names if not name.endswith('/')}
        generated = {'fatcow.nuspec', '[Content_Types].xml', '_rels/.rels'}
        generated.update(name for name in payload if re.fullmatch(
            r'package/services/metadata/core-properties/[a-zA-Z0-9]+\.psmdcp', name))
        check(payload == set(expected) | generated, 'Missing or unexpected package files')
        for name, path in expected.items():
            check(archive.read(name) == path.read_bytes(), f'Package bytes differ: {name}')
        metadata = ET.fromstring(archive.read('fatcow.nuspec'))
        ns = {'n': metadata.tag.split('}')[0][1:]}
        node = metadata.find('n:metadata', ns)
        for key, value in {'id': 'fatcow', 'version': version, 'license': 'LICENSE.md',
                           'readme': 'README.md', 'projectUrl': REPOSITORY}.items():
            check(node.findtext(f'n:{key}', namespaces=ns) == value, f'Invalid {key}')
        check(node.find('n:license', ns).get('type') == 'file', 'Invalid license type')
        repo = node.find('n:repository', ns)
        check(repo.attrib == {'type': 'git', 'url': REPOSITORY + '.git', 'commit': commit},
              'Invalid repository metadata')
        check(not node.findall('.//n:dependency', ns), 'Unexpected runtime dependencies')
        content = node.find('n:contentFiles/n:files', ns)
        check(content is not None and content.attrib == {
            'include': 'any/any/**/*', 'buildAction': 'Content',
            'copyToOutput': 'true', 'flatten': 'false'}, 'Invalid contentFiles settings')
        readme = archive.read('README.md').decode()
        check(all(re.match(r'https?://|#', link) for link in
                  re.findall(r'\]\(([^)]+)\)', readme)), 'Relative package README link')
    return assets


def verify_consumer(package, version, assets):
    # A fresh package cache prevents an older local package masking failures.
    with tempfile.TemporaryDirectory(prefix='nuget-test-', dir=ROOT / 'artifacts') as temp:
        folder = Path(temp)
        config = folder / 'NuGet.Config'
        configuration = ET.Element('configuration')
        sources = ET.SubElement(configuration, 'packageSources')
        ET.SubElement(sources, 'clear')
        ET.SubElement(sources, 'add', key='local', value=str(package.parent))
        ET.ElementTree(configuration).write(config, encoding='utf-8')
        project = folder / 'Consumer.csproj'
        project.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                           '<TargetFramework>net10.0</TargetFramework><NuGetAudit>false</NuGetAudit>'
                           '<TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup>'
                           '<ItemGroup><PackageReference Include="fatcow" Version="' + version +
                           '" /></ItemGroup></Project>', encoding='utf-8')
        env = dict(os.environ, NUGET_PACKAGES=str(folder / 'packages'))
        run(['dotnet', 'restore', project, '--configfile', config], env=env)
        run(['dotnet', 'build', project, '--no-restore', '-c', 'Release'], env=env)
        output = folder / 'bin/Release/net10.0/fatcow'
        check({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
              == set(assets), 'Consumer output paths differ')
        for name, path in assets.items():
            check((output / name).read_bytes() == path.read_bytes(), f'Consumer bytes differ: {name}')
        for css in output.glob('*/sprite/*.css'):
            for url in re.findall(r'url\(["\']?([^"\')]+)', css.read_text()):
                check((css.parent / url).is_file(), f'Broken sprite URL in {css}')


def main():
    check(sys.platform == 'win32', 'NuGet packing requires Windows')
    run([sys.executable, ROOT / 'scripts/verify.py'])
    commit = run(['git', 'rev-parse', 'HEAD'])
    version = json.loads((ROOT / 'package.json').read_text())['version']
    spec = ET.parse(ROOT / 'packaging/nuget/fatcow.nuspec')
    check(spec.findtext('.//{*}version') == version, 'npm/NuGet versions differ')
    artifacts = ROOT / 'artifacts'
    tools = artifacts / 'tools'
    tools.mkdir(parents=True, exist_ok=True)
    cli = tools / f'nuget-{NUGET_VERSION}.exe'
    if not cli.exists():
        download = cli.with_suffix('.download')
        urllib.request.urlretrieve(
            f'https://dist.nuget.org/win-x86-commandline/v{NUGET_VERSION}/nuget.exe', download)
        download.replace(cli)
    package = artifacts / f'fatcow.{version}.nupkg'
    checksum = package.with_suffix('.nupkg.sha256')
    checksum.unlink(missing_ok=True)
    package.unlink(missing_ok=True)
    run([cli, 'pack', ROOT / 'packaging/nuget/fatcow.nuspec', '-OutputDirectory', artifacts,
         '-Properties', f'RepositoryCommit={commit}', '-NonInteractive'])
    assets = verify_package(package, version, commit)
    print('Package bytes and metadata verified; restoring isolated consumer...', flush=True)
    verify_consumer(package, version, assets)
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    checksum.write_text(f'{digest}  {package.name}\n', encoding='utf-8')
    print(f'Validated release: {package}\nSHA-256: {digest}', flush=True)


if __name__ == '__main__':
    main()
