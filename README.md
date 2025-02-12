# SWEKit AutoGen

An autonomous software engineering assistant powered by AutoGen and Composio, designed to analyze and fix code issues automatically.

## Features

- Automated code analysis and bug fixing
- GitHub integration for issue tracking and PR creation
- Composio toolset integration for advanced code manipulation
- Support for multiple expert agents (SWE Expert and Test Expert)
- Workspace management for isolated development environments

## Prerequisites

- Python 3.11+
- Git
- GitHub access token
- Composio API key
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/memamun/swekit_autogen.git
cd swekit_autogen
```


2. Install dependencies:

```bash
pip install ag2[captainagent]
```

using uv:
```bash
uv pip install -r requirements.txt
```

using pip:
```bash
pip install -r requirements.txt
```

using conda:
```bash
conda env create -n swe -f environment.yml
```

3. Create or copy `.env.example` to `.env` and add your API keys:

```bash
COMPOSIO_API_KEY=your_composio_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_ACCESS_TOKEN=your_github_access_token
```

## Usage

```bash
python main.py
```

# With Docker and Without Docker:
- Change Workspace WorkspaceType.Host for Local Workspace(preferred)
- Change Workspace WorkspaceType.Docker for Docker Workspace

# TODO:
- Add integration with AutogenStudio
- Add integration with Ollama
- Add integration with Gemini
- API integration with N8N
- Add a web UI

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
