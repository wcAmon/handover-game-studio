import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'harness/continuous.py'

class ContinuousTests(unittest.TestCase):
    def fixture(self,t,behavior='advance'):
        root=Path(t)
        (root/'harness/bin').mkdir(parents=True)
        shutil.copy2(ROOT/'harness/bin/check-handover',root/'harness/bin/check-handover')
        shutil.copytree(ROOT/'harness/native-agents',root/'harness/native-agents')
        (root/'handover.md').write_text('''# HANDOVER
STATUS: ACTIVE
## NORTH_STAR
fixture
## STATE
step 0
## TASKS
### NOW
- [T-001] fixture
## PITFALLS
none
## PLAYBOOK
none
## HUMAN
- none
## LOG
- #0 fixture
''')
        subprocess.run(['git','init','-q',str(root)],check=True)
        subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
        subprocess.run(['git','-C',str(root),'config','user.email','test@localhost'],check=True)
        subprocess.run(['git','-C',str(root),'add','.'],check=True)
        subprocess.run(['git','-C',str(root),'commit','-qm','initial'],check=True)
        agent=root/'fake-codex'
        agent.write_text('''#!/usr/bin/env python3
import os,sys,time
from pathlib import Path
root=Path.cwd()
if '--version' in sys.argv:
 print('codex-cli fixture');sys.exit(0)
if sys.argv[1:3]==['features','list']:
 print('multi_agent stable true');sys.exit(0)
with (root/'pids').open('a') as f:f.write(str(os.getpid())+'\\n')
with (root/'args').open('a') as f:f.write(repr(sys.argv)+'\\n')
(root/'prompt.txt').write_text(sys.stdin.read())
mode='''+repr(behavior)+'''
if mode=='hang':time.sleep(10)
if mode=='fail':sys.exit(7)
if mode=='unchanged':sys.exit(0)
p=root/'handover.md'; s=p.read_text()
step=int(s.split('step ')[1].split()[0])+1
s=s.replace('step '+str(step-1),'step '+str(step))
if mode=='drain':(root/'.studio/continuous.drain').touch()
if step>=2 and mode!='forever':s=s.replace('STATUS: ACTIVE','STATUS: DONE')
p.write_text(s)
''')
        agent.chmod(0o755)
        return root,agent

    def run_supervisor(self,root,agent,*extra):
        return subprocess.run([sys.executable,str(RUNNER),'run','--workspace',str(root),'--codex',str(agent),'--session-seconds','3','--retry-delay','0',*extra],capture_output=True,text=True,timeout=15)

    def test_two_fresh_contexts_until_done(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            pids=(root/'pids').read_text().splitlines()
            self.assertEqual(len(pids),2);self.assertEqual(len(set(pids)),2)
            args=(root/'args').read_text();self.assertNotIn('resume',args);self.assertNotIn('--full-auto',args)
            state=json.loads((root/'.studio/continuous.json').read_text())
            self.assertEqual(state['state'],'done')
            self.assertEqual(state['sandbox'],'workspace-write')
            self.assertFalse((root/'.studio/session.env').exists())

    def test_explicit_full_access_survives_detached_start(self):
        import time
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            result=subprocess.run([sys.executable,str(RUNNER),'start','--workspace',str(root),'--codex',str(agent),'--sandbox','danger-full-access'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                state=json.loads((root/'.studio/continuous.json').read_text())
                if state['state']=='done':break
                time.sleep(.05)
            self.assertEqual(state['state'],'done')
            self.assertEqual(state['sandbox'],'danger-full-access')
            self.assertIn("'--sandbox', 'danger-full-access'",(root/'args').read_text())

    def test_repeated_failure_stops(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'fail')
            result=self.run_supervisor(root,agent,'--max-failures','2')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(len((root/'pids').read_text().splitlines()),2)
            self.assertEqual(json.loads((root/'.studio/continuous.json').read_text())['state'],'error')

    def test_no_progress_stops(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'unchanged')
            result=self.run_supervisor(root,agent,'--max-failures','2')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(len((root/'pids').read_text().splitlines()),2)

    def test_timeout_cleans_session(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'hang')
            result=self.run_supervisor(root,agent,'--session-seconds','0.3','--max-failures','1')
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((root/'.studio/session.env').exists())

    def test_stop_and_duplicate_start(self):
        with tempfile.TemporaryDirectory() as t:
            import time
            root,agent=self.fixture(t,'hang')
            cmd=[sys.executable,str(RUNNER),'run','--workspace',str(root),'--codex',str(agent)]
            first=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                deadline=time.monotonic()+5
                while not (root/'pids').exists() and time.monotonic()<deadline:time.sleep(.05)
                self.assertTrue((root/'pids').exists())
                second=subprocess.run(cmd,capture_output=True,text=True,timeout=3)
                self.assertNotEqual(second.returncode,0)
                self.assertIn('already running',second.stderr)
                subprocess.run([sys.executable,str(RUNNER),'stop','--workspace',str(root)],check=True,capture_output=True)
                first.communicate(timeout=5)
                self.assertEqual(first.returncode,0)
                state=json.loads((root/'.studio/continuous.json').read_text())
                self.assertEqual(state['state'],'stopped')
                self.assertFalse((root/'.studio/session.env').exists())
            finally:
                if first.poll() is None:first.kill();first.communicate()

    def test_blocked_never_launches_agent(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            p=root/'handover.md';p.write_text(p.read_text().replace('STATUS: ACTIVE','STATUS: BLOCKED'))
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse((root/'pids').exists())

    def test_native_team_survives_detached_start_and_fresh_shifts(self):
        import time
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            result=subprocess.run([sys.executable,str(RUNNER),'start','--workspace',str(root),
                '--codex',str(agent),'--team','native','--orchestrator-effort','medium'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                state=json.loads((root/'.studio/continuous.json').read_text())
                if state['state']=='done':break
                time.sleep(.05)
            self.assertEqual(state['state'],'done')
            self.assertEqual(state['team'],'native')
            self.assertEqual(state['orchestrator_effort'],'medium')
            self.assertEqual(state['native_team']['orchestrator'],'gpt-6-astra')
            argv=(root/'args').read_text().splitlines()
            self.assertEqual(len(argv),2)
            for line in argv:
                self.assertIn("'-m', 'gpt-6-astra'",line)
                self.assertIn('agents.default_subagent_model="gpt-6-sol"',line)
                self.assertIn('model_reasoning_effort="medium"',line)
                self.assertIn('agents.max_concurrent_threads_per_session=2',line)
                self.assertNotIn('resume',line)
            self.assertIn('最多一個 writer',(root/'prompt.txt').read_text())
            self.assertIn('gpt-5.6-terra',(root/'prompt.txt').read_text())

    def test_disabled_native_feature_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            agent.write_text(agent.read_text().replace('multi_agent stable true','multi_agent stable false'))
            result=self.run_supervisor(root,agent,'--team','native')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('No fallback',result.stderr)
            self.assertFalse((root/'pids').exists())
            self.assertFalse((root/'.studio/session.env').exists())

    def test_doctor_is_readonly_and_does_not_launch_agent(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            result=subprocess.run([sys.executable,str(RUNNER),'doctor','--workspace',str(root),
                '--codex',str(agent)],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['default_worker'],'gpt-6-sol')
            self.assertFalse((root/'.studio').exists())
            self.assertFalse((root/'pids').exists())

    def test_native_requires_role_guidance_in_target_workspace(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            (root/'harness/native-agents/coder.md').unlink()
            result=self.run_supervisor(root,agent,'--team','native')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('target workspace: coder',result.stderr)
            self.assertFalse((root/'pids').exists())

    def test_drain_finishes_current_shift_without_starting_next(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'drain')
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len((root/'pids').read_text().splitlines()),1)
            state=json.loads((root/'.studio/continuous.json').read_text())
            self.assertEqual(state['state'],'paused')
            self.assertIn('step 1',(root/'handover.md').read_text())
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len((root/'pids').read_text().splitlines()),1)

    def test_delivery_stagnation_replans_then_stops(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'forever')
            (root/'product.txt').write_text('unchanged')
            (root/'delivery.json').write_text(json.dumps({'version':1,'watch':['product.txt'],'stagnation_shifts':2,'replan_shifts':1}))
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len((root/'pids').read_text().splitlines()),3)
            state=json.loads((root/'.studio/continuous.json').read_text())
            self.assertEqual(state['state'],'stalled')
            self.assertIn('交付停滯',(root/'prompt.txt').read_text())
            self.assertEqual(state['delivery']['stagnant_shifts'],3)

    def test_done_takes_precedence_over_stagnation(self):
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            (root/'product.txt').write_text('unchanged')
            (root/'delivery.json').write_text(json.dumps({'version':1,'watch':['product.txt'],'stagnation_shifts':1,'replan_shifts':1}))
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((root/'.studio/continuous.json').read_text())['state'],'done')
            receipts=list((root/'docs/runs/shifts').glob('*.json'))
            self.assertEqual(len(receipts),2)
            self.assertGreaterEqual(json.loads(receipts[0].read_text())['elapsed_seconds'],0)

    def test_resume_clears_drain_and_starts_fresh_contexts(self):
        import time
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t)
            (root/'.studio').mkdir()
            for name in ['continuous.drain','continuous.stop','PAUSE']:
                (root/'.studio'/name).touch()
            result=subprocess.run([sys.executable,str(RUNNER),'resume','--workspace',str(root),
                '--codex',str(agent),'--team','native'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                state=json.loads((root/'.studio/continuous.json').read_text())
                if state['state']=='done':break
                time.sleep(.05)
            self.assertEqual(state['state'],'done')
            self.assertEqual(len((root/'pids').read_text().splitlines()),2)
            self.assertFalse((root/'.studio/continuous.drain').exists())

    def test_external_delivery_change_resets_previous_stagnation(self):
        import hashlib
        with tempfile.TemporaryDirectory() as t:
            root,agent=self.fixture(t,'drain')
            (root/'product.txt').write_text('new external change')
            policy=root/'delivery.json'
            policy.write_text(json.dumps({'version':1,'watch':['product.txt'],'stagnation_shifts':2,'replan_shifts':1}))
            (root/'.studio').mkdir()
            (root/'.studio/delivery.json').write_text(json.dumps({'policy_hash':hashlib.sha256(policy.read_bytes()).hexdigest(),
                'fingerprint':'previous product fingerprint','stagnant_shifts':2,'action':'replan'}))
            result=self.run_supervisor(root,agent)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((root/'.studio/continuous.json').read_text())['delivery']['stagnant_shifts'],1)

if __name__=='__main__':unittest.main()
