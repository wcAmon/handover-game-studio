import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/create_workspace.py'

class WorkspaceTests(unittest.TestCase):
    def run_tool(self, dest, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(dest), *args], cwd=ROOT, capture_output=True, text=True)

    def test_blank_is_independent_and_valid(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t) / 'blank'
            result = self.run_tool(dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((dest/'design/north-star.md').exists())
            self.assertFalse((dest/'examples').exists())
            self.assertFalse((dest/'.git').exists())
            self.assertFalse((dest/'.studio').exists())
            self.assertFalse((dest/'harness/config.local.sh').exists())
            text = (dest/'handover.md').read_text()
            self.assertIn('STATUS: BLOCKED', text)
            self.assertNotIn('Swarm', text)
            result = subprocess.run([sys.executable, str(dest/'harness/bin/check-handover')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('harness/bin/time-left', (dest/'AGENTS.md').read_text())

    def test_example_preserves_approval_assets_and_board(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t) / 'swarm'
            result = self.run_tool(dest, '--example', 'swarm-agent')
            self.assertEqual(result.returncode, 0, result.stderr)
            approval = json.loads((dest/'design/approval.json').read_text())
            self.assertEqual(approval['status'], 'approved')
            self.assertEqual(approval['sha256'], hashlib.sha256((dest/'design/north-star.md').read_bytes()).hexdigest())
            for src in (ROOT/'examples/swarm-agent/design/concept').glob('*.png'):
                self.assertEqual(src.read_bytes(), (dest/'design/concept'/src.name).read_bytes())
            for command in [[sys.executable, str(dest/'tools/concept_board.py')], [sys.executable, str(dest/'harness/bin/check-handover')]]:
                result = subprocess.run(command,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)

    def test_existing_destination_untouched(self):
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t); sentinel=dest/'keep'; sentinel.write_text('keep')
            result=self.run_tool(dest)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('already exists', result.stderr)
            self.assertEqual(list(dest.iterdir()),[sentinel])

    def test_framework_destination_rejected(self):
        result=self.run_tool(ROOT/'should-not-create-workspace')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('outside the framework', result.stderr)
        self.assertFalse((ROOT/'should-not-create-workspace').exists())

    def test_unknown_example_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'new'
            self.assertNotEqual(self.run_tool(dest,'--example','missing').returncode,0)
            self.assertFalse(dest.exists())

    def test_image_tools_target_selected_workspace(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'selected'
            source=ROOT/'examples/swarm-agent/design/concept/004-desert-treehouse.png'
            cmd=[sys.executable,str(ROOT/'tools/imagegen.py'),'--workspace',str(dest),
                 '--source',str(source),'--prompt','test routing','--slug','routing','--round','1']
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            image=dest/'design/concept/001-routing.png'
            self.assertEqual(image.read_bytes(),source.read_bytes())
            result=subprocess.run([sys.executable,str(ROOT/'tools/concept_board.py'),
                                   '--workspace',str(dest)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('001-routing.png',(dest/'design/concept/board.html').read_text())

if __name__ == '__main__':
    unittest.main()
