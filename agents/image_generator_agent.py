"""
Image Generator Agent

Reads text input and generates images using the OpenAI DALL-E API.
Generated images are saved to agents/generated_images/.

Usage:
    python agents/image_generator_agent.py --text "A sunset over the mountains"
    python agents/image_generator_agent.py --file path/to/prompt.txt
    python agents/image_generator_agent.py  # reads from stdin

Environment variables:
    OPENAI_API_KEY  – required; your OpenAI API key
    IMAGE_SIZE      – optional; one of 256x256, 512x512, 1024x1024 (default: 1024x1024)
    IMAGE_COUNT     – optional; number of images to generate per prompt (default: 1)
"""

import argparse
import datetime
import os
import ssl
import sys
import urllib.request

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_images")

# Request timeout in seconds for downloading generated images from OpenAI.
_DOWNLOAD_TIMEOUT = 60


def _log(message: str) -> None:
    """Append a timestamped entry to logs/activity.log."""
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "activity.log")
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{timestamp}] {message}\n"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(entry)
    print(entry, end="")


def _download_image(url: str, filepath: str) -> None:
    """Download *url* to *filepath* with a timeout and SSL verification."""
    ssl_ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "image-generator-agent/1.0"})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=_DOWNLOAD_TIMEOUT) as resp:  # noqa: S310
        with open(filepath, "wb") as fh:
            fh.write(resp.read())


def generate_images(prompt: str, count: int = 1, size: str = "1024x1024") -> list[str]:
    """
    Generate images for *prompt* using the OpenAI DALL-E API and save them to
    OUTPUT_DIR.  Returns the list of saved file paths.
    """
    try:
        import openai  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "The 'openai' package is required.  Install it with:\n"
            "    pip install openai"
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY environment variable is not set.  "
            "Please export your OpenAI API key before running this agent."
        )

    # DALL-E 3 only supports n=1; fall back to DALL-E 2 when multiple images are requested.
    model = "dall-e-3" if count == 1 else "dall-e-2"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = openai.OpenAI(api_key=api_key)

    _log(f"Image generator agent: requesting {count} image(s) for prompt: {prompt!r}")

    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=count,
        size=size,
        response_format="url",
    )

    saved_paths: list[str] = []
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    for idx, image_data in enumerate(response.data):
        url = image_data.url
        # Build a short, filesystem-safe name derived from the prompt
        safe_name = "".join(
            c if c.isalnum() or c in " _-" else "_" for c in prompt[:40]
        ).strip().replace(" ", "_")
        filename = f"{timestamp}_{safe_name}_{idx + 1}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        _download_image(url, filepath)
        saved_paths.append(filepath)
        _log(f"Image generator agent: saved image to {filepath}")

    return saved_paths


def read_prompt(args: argparse.Namespace) -> str:
    """Return the prompt text from the appropriate source."""
    if args.text is not None:
        return args.text.strip()
    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    # Fall back to stdin
    print("Enter the prompt text (press Ctrl-D / Ctrl-Z when done):")
    return sys.stdin.read().strip()


def _parse_image_count(value: str) -> int:
    """Parse IMAGE_COUNT env-var to int with a helpful error message."""
    try:
        return int(value)
    except ValueError:
        raise SystemExit(
            f"IMAGE_COUNT environment variable must be a valid integer, got: {value!r}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate images from a text prompt using the OpenAI DALL-E API.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--text", "-t", help="Prompt text supplied directly on the command line.")
    group.add_argument("--file", "-f", help="Path to a plain-text file containing the prompt.")
    parser.add_argument(
        "--size",
        "-s",
        default=os.environ.get("IMAGE_SIZE", "1024x1024"),
        choices=["256x256", "512x512", "1024x1024"],
        help="Size of the generated image (default: 1024x1024).",
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=_parse_image_count(os.environ.get("IMAGE_COUNT", "1")),
        help="Number of images to generate (default: 1).  "
             "Note: DALL-E 3 only supports n=1; multiple images will use DALL-E 2.",
    )

    args = parser.parse_args()
    prompt = read_prompt(args)

    if not prompt:
        parser.error("Prompt text is empty.  Please provide a non-empty prompt.")

    saved = generate_images(prompt, count=args.count, size=args.size)

    print(f"\nDone! {len(saved)} image(s) saved to: {OUTPUT_DIR}")
    for path in saved:
        print(f"  • {path}")


if __name__ == "__main__":
    main()
