import sys
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from langchain_core.messages import SystemMessage, HumanMessage

from .aish import AIsh

class InteractiveMode:
    def __init__(self, aish: AIsh):
        self.aish = aish
        self.mode = "terminal"
        self.bindings = self._setup_bindings()
    
    def _get_mode_prompt(self):
        if self.mode == "message":
            color = "bold ansiblack bg:ansigreen"
        elif self.mode == "terminal":
            color = "bold ansiblack bg:ansiblue"

        prompt_text = FormattedText([
            ('bold ansiblack bg:ansiyellow', ' USER '),
            (f'{color}', f' {self.mode.capitalize()} '),
            ('', ' ')
        ])
        
        style = Style.from_dict({})
        
        return prompt_text, style

    def _switch_mode(self):
        self.mode = "terminal" if self.mode == "message" else "message"
        if self.aish.history and self.aish.history[-1].content.startswith("Mode switched to "):
            self.aish.history.pop()
        self.aish.history.append(SystemMessage(content=f"Mode switched to {self.mode}"))

    def _run_command(self, command: str):
        self.aish.history.append(HumanMessage(content=command))
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
            self.aish.history.append(SystemMessage(content=result.stdout))
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            self.aish.history.append(SystemMessage(content=result.stderr))
    
    def _handle_input(self, user_input: str):
        if self.mode == "message":
            self.aish.user_message(user_input)
        elif self.mode == "terminal":
            self._run_command(user_input)
    
    def _setup_bindings(self):
        bindings = KeyBindings()
        
        @bindings.add('c-space')
        def _(event):
            self._switch_mode()
            event.app.invalidate()
        
        return bindings

    def run(self):
        print("Welcome to AIsh Interactive (Use Ctrl+Space to switch mode)")
        
        def get_prompt():
            prompt_text, _ = self._get_mode_prompt()
            return prompt_text
        
        while True:
            try:
                user_input = prompt(get_prompt, key_bindings=self.bindings)
                
                if user_input.lower() == "exit":
                    break
                    
                self._handle_input(user_input)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break