import argparse
from .agencli import AgenCLI

def cli():
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

    agencli.request_loop(args.message)