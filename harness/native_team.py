"""Use Codex's native subagents inside a shift; no second scheduling runtime."""
import json
from pathlib import Path
import subprocess

ORCHESTRATOR = 'gpt-6-astra'
WORKERS = ('gpt-6-sol', 'gpt-5.6-terra', 'gpt-6-luna')
ROLES = ('planner', 'coder', 'artist', 'reviewer', 'finisher')


def options(effort='high'):
    result = ['-m', ORCHESTRATOR]
    settings = {
        'model_reasoning_effort': effort,
        'agents.enabled': True,
        'agents.max_concurrent_threads_per_session': 2,
        'agents.default_subagent_model': WORKERS[0],
        'agents.default_subagent_reasoning_effort': 'medium',
    }
    for key, value in settings.items():
        result += ['-c', key + '=' + json.dumps(value)]
    return result


def preflight(binary, workspace):
    """Read-only local feature check; does not establish account/model/tool access."""
    version = subprocess.check_output([binary, '--version'], text=True, timeout=10).strip()
    features = subprocess.check_output([binary, 'features', 'list'], text=True, timeout=10)
    enabled = any(line.split()[0:1] == ['multi_agent'] and line.split()[-1:] == ['true']
                  for line in features.splitlines())
    if not enabled:
        raise RuntimeError('Native multi_agent is unavailable or disabled; inspect this CLI configuration. No fallback.')
    role_dir = Path(workspace) / 'harness/native-agents'
    for role in ROLES:
        if not (role_dir / f'{role}.md').is_file():
            raise RuntimeError('Missing native agent guidance in target workspace: ' + role)
    return {'version': version, 'orchestrator': ORCHESTRATOR,
            'default_worker': WORKERS[0], 'max_workers': 2,
            'note': 'Feature check only; model access and artist tools require live evidence.'}


PROMPT = '''
本班啟用原生多模型團隊；你是 Astra orchestrator，只負責讀摘要、排優先序、派工、
追蹤班次生命週期與處理 worker 的阻礙。你不實作產品、不做詳細 code review、
不親自跑驗證或看圖驗收、不寫交班／報告、不 commit、不執行 knowledge accept/rollback。
這段授權「班內 subagents」，不是讓子 agent 啟動下一班或另外的 CLI/tmux/cron。
只處理當前一個 NOW；讀 handover 與索引後，把必要的詳細檔案閱讀交給對應 worker。
使用 Codex 原生 spawn / send / wait / completion，不自行實作喚醒服務。
每次派工選 planner / coder / artist / reviewer / finisher，讀 harness/native-agents/<role>.md，
把其職責規則連同任務傳給子 agent，並明確指定 model 與 effort。角色是任務分工，
不假定當前 CLI 的 spawn 工具有 agent_type 或自訂角色參數。
允許 worker 模型：gpt-6-sol、gpt-5.6-terra、gpt-6-luna。
reviewer 與 finisher 固定選 gpt-6-sol；reviewer 必須獨立於被審查的 coder。
一般規劃、跨檔實作、美術整合優先 Sol；狹窄盤點、摘要可選 Luna；
Terra 用於界線清楚、有可靠驗證的小修改或整理。以上是起始策略，不宣稱固定價格/速度。
首要指標是可靠交付速度、一次驗收成功率與返工；不是最少token或最便宜模型。
有明確範圍的一般實作優先派 Sol；反覆失敗時重估方法或升級，不為省用量硬撐。
worker 不預設繼承 Astra。選其他模型須用 fresh/精簡 context（若有 fork_turns，設 none），
明確提供目的、輸入、知識索引、可寫路徑、驗證與截止時間。不要複製全部歷史。
模型/工具不可用時保留原始錯誤與實際選擇；最多一次有理由的替代/升級，不能默默換模型。
最多兩個子 agent 同時工作，禁止子 agent 再派生。共用工作區時同時最多一個 writer，
其他 agent 只讀且避開正在變更的檔案；reviewer 在 coder/artist 停止寫入後審查穩定 diff。
不要把 subagents 當成自動隔離的 worktree；若必須多人同時寫，先隔離並安排序列整合。
流程為 coder/artist 完成產物 → 獨立 Sol reviewer 回報具體問題 → coder 修復並按需複審
→ Sol finisher 執行最終測試與看圖、核對審查和驗證證據、寫派工報告／交班、
依證據決定知識候選是否 accept/rollback、執行 check-handover 並 commit。
若 reviewer 或 finisher 發現需修復的問題，由你重新派 coder；不要自己接手修改或驗收。
finisher 不再 spawn 子 agent，也不改產品功能；不把 worker 完成訊息當成驗收證據。
finisher 必須獲得足夠收班時間。軟截止後停止新產品任務，但必要的 reviewer／finisher
收尾派工與修復調度仍可進行到硬截止；不能因軟截止禁止 finisher。
artist 必須先確認當前 session 實際有生圖/建模工具。模型名字不代表生圖能力；
工具缺失就回報具體限制，不能以腳本佔位冒充正式素材。
worker 完成會由原生機制回報；尚有任務就 wait 或調整派工，不要提早 final 等使用者喚醒。
finisher 收班前確認其他 worker 停止寫入；若無法停妥或驗證失敗，記錄真實狀態，
不得冒稱乾淨收班。Astra 等 finisher 回報並結束本班，不代做剩餘工作。
將每次派工 role、task、model、effort、選擇理由、agent id、驗證指令/結果、fallback 與坑，
交給 finisher 寫入 docs/runs/team-<班次號>.md；handover 僅留摘要與該檔索引。
這是可稽核的行為政策，不是模型/路徑權限的硬隔離。遵循既有 sandbox 與核准邊界。
'''
