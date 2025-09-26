import os
import time
from xonsh.main import setup
from xonsh.built_ins import XSH
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import print_formatted_text
from langchain_core.messages import SystemMessage, HumanMessage

class XonshInteractiveMode:
    def __init__(self, aish):
        self.aish = aish
        self.mode = "terminal"
        self.session = PromptSession()

        setup(shell_type="prompt_toolkit")
        
    def _get_prompt_text(self):
        blocks = [('ansired', time.strftime("%H:%M:%S") + ' ')]
        blocks += [('ansiblue', os.getenv("USER", "user"))]
        blocks += [('ansipurple', '@')]
        blocks += [('ansiyellow', self.mode)]
        blocks += [('ansiwhite', ' ' + os.getcwd())]
        blocks += [('ansipurple', ' ? ')]

        return FormattedText(blocks)

    def _setup_bindings(self):
        bindings = KeyBindings()
        
        @bindings.add('c-space')
        def _(event):
            self._switch_mode()
            event.app.invalidate()
        
        return bindings
    
    def _switch_mode(self):
        self.mode = "terminal" if self.mode == "prompt" else "prompt"
        if self.aish.history and self.aish.history[-1].content.startswith("Mode switched to "):
            self.aish.history.pop()
        self.aish.history.append(SystemMessage(content=f"Mode switched to {self.mode}"))
    
    def _run_command(self, command):
        self.aish.history.append(HumanMessage(content=command))
        
        try:
            XSH.execer.eval(f'$[{command}]')
            # TODO: Capture output and add to history
        except Exception as e:
            error_msg = str(e).split('\n')[0]
            print(f"Error: {error_msg}")
            self.aish.history.append(SystemMessage(content=error_msg))
    
    def _handle_input(self, user_input):
        if self.mode == "prompt":
            self.aish.process_user_message(user_input)
        elif self.mode == "terminal":
            self._run_command(user_input)
    
    def run(self, message=None):
        print("Use Ctrl+Space to switch between Terminal and AI mode")
        
        if message:
            self._handle_input(message)
            return
        
        # Start with custom prompt that can handle mode switching
        self._run_interactive_session()
    
    def _run_interactive_session(self):
        while True:
            try:
                # Übergebe Prompt als callable für Live-Updates
                user_input = self.session.prompt(self._get_prompt_text, key_bindings=self._setup_bindings())
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                    
                self._handle_input(user_input)
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

InteractiveMode = XonshInteractiveMode