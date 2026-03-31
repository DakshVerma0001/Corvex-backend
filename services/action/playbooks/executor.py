import asyncio
from typing import List

from services.action.playbooks.loader import Playbook, PlaybookStep
from services.action.audit import log_action_audit


class ExecutionResult:
    def __init__(self, success: bool, steps: List[dict]):
        self.success = success
        self.steps = steps


class PlaybookExecutor:

    async def execute(self, playbook: Playbook, incident) -> ExecutionResult:

        executed_steps = []

        for step in playbook.steps:

            try:
                # Render params (basic template replace)
                params = self._render_params(step.params, incident)

                result = await self._run_action(step.action, params)

                await log_action_audit(
                    incident_id=incident.id,
                    playbook_name=playbook.name,
                    action_name=step.action,
                    params=params,
                    result=result,
                    success=result.get("success", False),
                    logs=str(result)
                )

                executed_steps.append({
                    "action": step.action,
                    "success": result.get("success", False)
                })

                if not result.get("success", False):
                    if step.on_failure == "rollback":
                        await self._rollback(playbook, incident)
                        return ExecutionResult(False, executed_steps)

                    elif step.on_failure == "abort":
                        return ExecutionResult(False, executed_steps)

            except Exception as e:
                await self._rollback(playbook, incident)
                return ExecutionResult(False, executed_steps)

        return ExecutionResult(True, executed_steps)

    def _render_params(self, params, incident):
        rendered = {}

        for k, v in params.items():
            if isinstance(v, str) and "{{ entity_id }}" in v:
                rendered[k] = v.replace("{{ entity_id }}", incident.entity_id)
            else:
                rendered[k] = v

        return rendered

    async def _run_action(self, action, params):
        # TEMP: reuse your current logic
        import subprocess
        import json

        if action == "linux.firewall.block_ip":
            cmd = [
                "python",
                "services/action/runners/linux_runner/runner.py",
                "--action",
                action,
                "--params-json",
                json.dumps(params)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }

        return {"success": True, "output": "noop"}

    async def _rollback(self, playbook: Playbook, incident):
        for step in reversed(playbook.rollback):
            params = self._render_params(step.params, incident)
            await self._run_action(step.action, params)