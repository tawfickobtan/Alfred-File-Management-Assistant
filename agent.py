import os
from llm import complete
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.theme import Theme
import tools
import json

# Load config file
config = {}
with open("config.json", "r") as f:
    config = json.load(f)

systemPrompt = ""
with open("system_prompt.txt", "r") as f:
    systemPrompt = f.read()

custom_theme = Theme({
    "markdown.h1": "bold white",
    "markdown.h2": "bold green",
    "markdown.h3": "bold yellow",
})

console = Console(theme=custom_theme)


# Define function registry
functionRegistry = {
    "getItemsInPath": tools.getItemsInPath,
    "writeIntoFile": tools.writeIntoFile,
    "readFile": tools.readFile,
    "createFile": tools.createFile,
    "delete": tools.delete,
    "createDirectory": tools.createDirectory,
    "deleteDirectory": tools.deleteDirectory,
    "moveFile": tools.moveFile,
    "copyFile": tools.copyFile,
    "getCurrentDirectory": tools.getCurrentDirectory,
    "runCommand": tools.runCommand,
    "fileExists": tools.fileExists,
    "getFileSize": tools.getFileSize,
}

# Create welcome message
big_text = Text("""     ██╗ █████╗ ███╗   ███╗███████╗███████╗
     ██║██╔══██╗████╗ ████║██╔════╝██╔════╝
     ██║███████║██╔████╔██║█████╗  ███████╗
██   ██║██╔══██║██║╚██╔╝██║██╔══╝  ╚════██║
╚█████╔╝██║  ██║██║ ╚═╝ ██║███████╗███████║
╚════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝
""", style="bold cyan")
welcome_text = Text("Your AI Coding Agent", style="bold cyan")
version_text = Text(f"(Version: {config.get('version', '1.0.0')})", style="dim white")
welcome_panel = Panel(
    big_text + welcome_text + "\n" + version_text,
    title="🚀 Agent Started",
    border_style="green",
    padding=(0, 10),
    expand=False
)
console.print(welcome_panel)
console.print(Text("Model: ", style="bold yellow") + Text(config.get("model", "openai/gpt-oss-120b"), style="white"))
console.print(Text("Current Directory: ", style="bold yellow") + Text(os.getcwd(), style="white"))

console.print()  # Blank line for spacing

# Initialise messages with system prompt
messages = [
    {"role": "system",
     "content": systemPrompt}
]

agentPanel = Panel("🤖 James:",
                     border_style="green",
                     expand=False,
                     style="bold blue")

UserPanel = Panel("💭 User:",
                     border_style="green",
                     expand=False,
                     style="bold blue")

toolPanel = Text("🛠️ Executing: ",
                     style="bold red")

response = complete(messages)
messages.append(response)
console.print(agentPanel)
console.print(Markdown(response.content))
print("_________________")
print()

while True:
    console.print(UserPanel)
    userInput = input()
    print("_________________")
    print()
    messages.append({
        "role": "user",
        "content": userInput
    })

    while True:
        response = complete(messages)
        messages.append(response)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                id = tool_call.id
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                console.print(toolPanel)
                print(name)
                for arg in args:
                    print(arg)
                    print(args[arg] if len(args[arg]) < 50 else args[arg][:50] + "...")
                print()
                result = functionRegistry[name](**args)
                print("result:")
                print(result if len(str(result)) < 50 else str(result)[:50] + "...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": id,
                    "content": str(result)
                })
        else:
            console.print(agentPanel)
            console.print(Markdown(response.content))
            print("_________________")
            print() 
            break