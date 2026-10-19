"""Package report and reproducible sources in the handout's folder structure."""
from pathlib import Path
import shutil
import re
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
out=Path('/workspace/artifacts')
out.mkdir(exist_ok=True)
identity=(ROOT/'latex/identity.tex').read_text()
group=re.search(r'\\newcommand\{\\groupname\}\{([^}]+)\}',identity).group(1)
group=re.sub(r'[^A-Za-z0-9_-]','',group)
if not group: raise ValueError('Set a group name in latex/identity.tex')
filename=f'{group}-ProjectStep2.zip'
shutil.copy2(ROOT/'latex/report.pdf',out/'ProjectStep2-Report.pdf')
with ZipFile(out/filename,'w',ZIP_DEFLATED) as archive:
    archive.write(ROOT/'latex/report.pdf','ProjectStep2-Report.pdf')
    archive.write(ROOT/'README.md','README.md')
    for folder in ('Verilog','scripts','latex'):
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and (path.suffix in ('.v','.py','.sh','.tex') or path.parent.name=='figures'):
                archive.write(path,path.relative_to(ROOT))
    for path in sorted((ROOT/'build').iterdir()):
        if path.suffix=='.vcd' or (path.suffix=='.log' and not path.name.startswith('latex')):
            archive.write(path,'Verilog/simulation/'+path.name)
print(out/filename)
