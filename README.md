# Agents

A repository for storing and managing agents.

## Structure

- **agents/** – Store agent files here.
  - `image_generator_agent.py` – Reads a text prompt and generates images via the OpenAI DALL-E API.
  - **generated_images/** – Output directory where all generated images are saved.
- **logs/** – Activity log files are written here.
  - `activity.log` – Timestamped record of all actions taken in this repository.

## Image Generator Agent

Generates images from a text prompt and saves them to `agents/generated_images/`.

### Prerequisites

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

### Usage

```bash
# Pass the prompt directly
python agents/image_generator_agent.py --text "A sunset over the mountains"

# Read the prompt from a file
python agents/image_generator_agent.py --file prompt.txt

# Read the prompt from stdin (Ctrl-D to submit)
python agents/image_generator_agent.py
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--text` | `-t` | – | Prompt text on the command line |
| `--file` | `-f` | – | Path to a plain-text prompt file |
| `--size` | `-s` | `1024x1024` | Image size: `256x256`, `512x512`, or `1024x1024` |
| `--count` | `-n` | `1` | Number of images to generate |

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |
| `IMAGE_SIZE` | ❌ | Default image size (overridden by `--size`) |
| `IMAGE_COUNT` | ❌ | Default image count (overridden by `--count`) |
