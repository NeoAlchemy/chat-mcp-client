
from core.state import app_state
from openai import OpenAI
import asyncio
import time
import logging

openai_client = OpenAI()
class OpenAIAgentService:
    def __init__(self, client, state):
        self.client = client
        self.state = state

    async def handle_message(self, message: str) -> str:
        run_id = self._run_threads(message)
        await self._wait_for_completion(run_id)
        return self._get_reply(run_id)

    def _run_threads(self, message):
        if not self.state.thread_id:
            thread = self.client.beta.threads.create()
            self.state.thread_id = thread.id

        self.client.beta.threads.messages.create(
            thread_id=self.state.thread_id,
            role="user",
            content=f"{self.state.context} {message}"
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.state.thread_id,
            assistant_id=self.state.assistant_id
        )
        return run.id

    async def _wait_for_completion(self, run_id):
        start_time = time.time()
        timeout = 55

        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.state.thread_id,
                run_id=run_id
            )
            if run_status.status in ["completed", "failed", "cancelled"]:
                break

            if time.time() - start_time > timeout:
                self.client.beta.threads.runs.cancel(
                    thread_id=self.state.thread_id,
                    run_id=run_id
                )
                raise TimeoutError("Run cancelled due to timeout.")

            await asyncio.sleep(1)

    def _get_reply(self, run_id):
        messages = list(self.client.beta.threads.messages.list(
            thread_id=self.state.thread_id, run_id=run_id))
        return messages[0].content[0].text.value

openai_agent_service = OpenAIAgentService(openai_client, app_state)
