from curses import REPORT_MOUSE_POSITION
import re
import os
import json
import subprocess
from pathlib import Path
import frontmatter
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from providers import PROVIDERS

load_dotenv()

class AgenCLI:
    def __init__(self, model_name: str = None, provider_name: str = None, agent_name: str = None):
        self.config_path = Path(__file__).parent / "config" or Path.home() / ".config" / "agencli"
        self.system_overview = """
        You are a agencli. A Terminal Assitant that can help with a variety of Shell Tasks.

        Use short answers and concise responses.

        Using tags you can run shell commands in the terminal. For example: <shell>ls -la</shell> will run the ls -la command in the terminal.
        You can stack multiple shell commands in one response. All commands will be executed after the response.
        The user does not see the shell commands, so format your responses to be concise and to the point.
        """

        self.console = Console(force_terminal=True)

        self.config = self.load_config()
        self.agent_name = agent_name or os.getenv("AGENCLI_AGENT") or self.config["default_agent"]

        self.agent_prompt, self.agent_metadata = self.get_agent_prompt()

        self.default_connection = self.config["connections"][self.agent_metadata.get("connection")] or next(iter(self.config["connections"].values()))
        self.model_name = model_name or self.agent_metadata.get("model") or os.getenv("AGENCLI_MODEL") or self.default_connection['model']
        self.provider_name = provider_name or self.agent_metadata.get("provider") or os.getenv("AGENCLI_PROVIDER") or self.default_connection['provider']

        self.llm = PROVIDERS[self.provider_name](model=self.model_name)


    def load_config(self) -> dict:
        with open(self.config_path / "agencli.json", "r", encoding="utf-8") as config_file:
            return json.load(config_file)


    def get_agent_prompt(self) -> str:
        prompt_path = self.config_path / "agents" / f"{self.agent_name}.md"
        
        with open(prompt_path, "r", encoding="utf-8") as file:
            post = frontmatter.load(file)
            return post.content, post.metadata

    def run_context_module(self, module: str) -> str:
        module_path = self.config_path / "context_modules" / module

        result = subprocess.run([module_path], capture_output=True, text=True, check=True)
        return result.stdout


    def build_context(self) -> str:
        context = ""

        for module in self.agent_metadata["context_modules"].split(","):
            module = module.strip()
            context += f"\n\n------- Context Module: {module} -------\n"
            context += self.run_context_module(module)
            context += "\n\n-----------------------------------------\n"

        return context

    def request(self, message: str):
        conversation = [
            SystemMessage(content=self.system_overview),
            SystemMessage(content=self.agent_prompt),
            SystemMessage(content=self.build_context()),
            HumanMessage(content=message)
        ]
            
        response = self.llm.invoke(conversation)
        return response.content

    def parse_and_run_shell_commands(self, response: str):
        commands = re.findall(r"<shell>(.*?)</shell>", response)

        for command in commands:
            user_consent = Prompt.ask(f"[bold green]EXECUTING:[/bold green] [bold red]{command}[/bold red]", choices=["y", "n"], default="y")
            if user_consent == "n":
                continue
            if user_consent == "y":
                subprocess.run(command, shell=True)


    def print_response(self, response: str):
        response = re.sub(r"<shell>(.*?)</shell>", "", response)
        self.console.print(response.strip())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message", type=str, help="The message to send to the agent")
    parser.add_argument("-m", "--model", type=str, help="The model to use")
    parser.add_argument("-p", "--provider", type=str, help="The provider to use")
    parser.add_argument("-a", "--agent", type=str, help="The agent to use")
    parser.add_argument("--print-context", action="store_true", help="Print the context")
    parser.add_argument("--print-full-context", action="store_true", help="Print the full context")
    args = parser.parse_args()

    agencli = AgenCLI(model_name=args.model, provider_name=args.provider, agent_name=args.agent)

    if args.print_full_context:
        print(agencli.system_overview)
        print(agencli.agent_prompt)
        print(agencli.build_context())
        exit()
    elif args.print_context:
        print(agencli.build_context())
        exit()

    response = agencli.request(args.message)
    agencli.print_response(response)
    agencli.parse_and_run_shell_commands(response)