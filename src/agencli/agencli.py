import re
import os
import json
import subprocess
from pathlib import Path
import frontmatter
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from platformdirs import user_config_dir

from .providers import PROVIDERS

load_dotenv()

class AgenCLI:
    def __init__(self, model_name: str = None, provider_name: str = None, agent_name: str = None):
        self.console = Console(force_terminal=True)

        self.config_path = self._get_config_path()
        self.config = self._load_config()

        self.system_overview = self._get_system_overview()

        self.agent_name = agent_name or os.getenv("AGENCLI_AGENT") or self.config["default_agent"]
        self.agent_prompt, self.agent_metadata = self._get_agent_prompt()

        self.default_connection = self.config["connections"][self.agent_metadata.get("connection")] or next(iter(self.config["connections"].values()))
        self.model_name = model_name or self.agent_metadata.get("model") or os.getenv("AGENCLI_MODEL") or self.default_connection['model']
        self.provider_name = provider_name or self.agent_metadata.get("provider") or os.getenv("AGENCLI_PROVIDER") or self.default_connection['provider']

        self.llm = PROVIDERS[self.provider_name](model=self.model_name)

    def _get_system_overview(self) -> str:
        with open(self.config_path / "system_overview.md", "r", encoding="utf-8") as file:
            return file.read()

    def _get_config_path(self) -> Path:
        # Development: Check for local config directory
        local_config = Path.cwd() / "config"
        if local_config.is_dir() and (local_config / "agencli.json").exists():
            return local_config
        
        # Production: XDG-compliant user config directory
        user_config = Path(user_config_dir("agencli"))
        user_config.mkdir(parents=True, exist_ok=True)
        return user_config
       
    def _load_config(self) -> dict:
        with open(self.config_path / "agencli.json", "r", encoding="utf-8") as config_file:
            return json.load(config_file)


    def _get_agent_prompt(self) -> str:
        prompt_path = self.config_path / "agents" / f"{self.agent_name}.md"
        
        with open(prompt_path, "r", encoding="utf-8") as file:
            post = frontmatter.load(file)
            return post.content, post.metadata

    def _run_context_module(self, module: str) -> str:
        module_path = self.config_path / "context_modules" / module

        result = subprocess.run([module_path], capture_output=True, text=True, check=True)
        return result.stdout


    def _build_context(self) -> str:
        context = ""

        for module in self.agent_metadata["context_modules"].split(","):
            module = module.strip()
            context += f"\n\n------- Context Module: {module} -------\n"
            context += self._run_context_module(module)
            context += "\n\n-----------------------------------------\n"

        return context

    def _request(self, history: list):
        system_messages = [
            SystemMessage(content=self.system_overview),
            SystemMessage(content=self.agent_prompt),
            SystemMessage(content=self._build_context()),
        ]

        conversation = system_messages + history
            
        response = self.llm.invoke(conversation)
        return response.content

    def _execute_commands(self, response: str):
        commands = re.findall(r"<execute>(.*?)</execute>", response)

        if not commands:
            return None

        for command in commands:
            prompt = f"[bold on red] EXECUTE [/][bold on green] {command} [/]"
            user_consent = Prompt.ask(prompt, choices=["y", "n"], default="y")
            if user_consent == "n":
                continue
            if user_consent == "y":
                output = subprocess.run(command, shell=True, capture_output=True, text=True)
                print(output.stdout)
                return prompt + user_consent + "\n" + output.stdout


    def _print_response(self, response: str):
        response = re.sub(r"<execute>(.*?)</execute>", "", response)
        response = re.sub(r"<think>(.*?)</think>", "", response)
        response = re.sub(r"<user>", "", response)
        response = re.sub(r"<end>", "", response)
        self.console.print(response.strip())

    def request_loop(self, message: str):
        history = []
        history.append(HumanMessage(content=message))

        while True:
            response = self._request(history)
            history.append(AIMessage(content=response))

            if "<end>" in response:
                break
            
            try:
                self._print_response(response)
                command_output = self._execute_commands(response)
                if command_output != None:
                    history.append(SystemMessage(content=command_output))
                    continue
            except Exception as e:
                history.append(SystemMessage(content=f"System Error: {e}"))
                continue

            if "<user>" in response:
                message = Prompt.ask("[bold on blue] USER [/bold on blue][bold on green] MESSAGE [/bold on green]")
                history.append(HumanMessage(content=message))