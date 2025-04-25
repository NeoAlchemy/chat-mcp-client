
class AssistantFactory:
    def __init__(self, openai_client):
        self.client = openai_client

    def create_family_activity_assistant(self, tools, file_contents: str):
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read()
        return self.client.beta.assistants.create(
            name="Family Activities Assistant",
            instructions=f"{system_prompt} Here is the CSV contents:\n{file_contents}",
            tools=tools,
            model="gpt-4o",
            
        ).id
