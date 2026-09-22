"""Command-line interface for Playwright Page Object Generator."""

import sys
import click
from pathlib import Path
from typing import Optional

from src.generator import PageObjectGenerator


def _interactive_mode() -> tuple:
    """Interactive mode: ask user for parameters.

    Returns:
        Tuple of (input_path, class_name, output_path)
    """
    click.echo("\n=== Playwright Page Object Generator (Interactive Mode) ===\n")

    # Ask for input
    while True:
        try:
            input_path = input("[1/3] Enter HTML file path (or - for stdin): ").strip()
            if input_path:
                break
            print("Path cannot be empty\n")
        except EOFError:
            click.echo("Error: No input provided", err=True)
            sys.exit(1)

    # Ask for class name
    while True:
        try:
            class_name = input("[2/3] Enter class name (PascalCase, e.g., LoginPage): ").strip()
            if class_name:
                break
            print("Class name cannot be empty\n")
        except EOFError:
            click.echo("Error: No input provided", err=True)
            sys.exit(1)

    # Ask for output
    try:
        output_path = input("[3/3] Output file path (press Enter for stdout): ").strip()
    except EOFError:
        output_path = ""

    if not output_path:
        output_path = None

    click.echo("")
    return input_path, class_name, output_path


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option(
    "-i",
    "--input",
    "input_path",
    required=False,
    type=str,
    default=None,
    help="Input HTML file or - for stdin",
)
@click.option(
    "-c",
    "--class-name",
    "class_name",
    required=False,
    type=str,
    default=None,
    help="Generated class name (PascalCase)",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    required=False,
    type=str,
    default=None,
    help="Output file (default: stdout)",
)
@click.option(
    "-I",
    "--interactive",
    "interactive",
    is_flag=True,
    help="Interactive mode - answer prompts",
)
def main(
    input_path: Optional[str] = None,
    class_name: Optional[str] = None,
    output_path: Optional[str] = None,
    interactive: bool = False
) -> None:
    """Generate Playwright Page Object class from HTML.

    Example usage:
        python main.py -i login.html -c LoginPage -o login_page.py
        cat login.html | python main.py -i - -c LoginPage
        python main.py -I  # Interactive mode
    """
    try:
        generator = PageObjectGenerator()

        # Interactive mode
        if interactive:
            input_path, class_name, output_path = _interactive_mode()

        # Validate required parameters
        if not input_path or not class_name:
            click.echo(
                "Error: --input and --class-name are required (or use --interactive)",
                err=True
            )
            sys.exit(2)

        # Validate class name
        if not generator.validate_class_name(class_name):
            click.echo(
                f"Error: class_name must be in PascalCase (got: {class_name})",
                err=True
            )
            sys.exit(1)

        # Read input
        if input_path == "-":
            # Read from stdin
            html = sys.stdin.read()
        else:
            # Read from file
            try:
                with open(input_path, "r", encoding="utf-8") as f:
                    html = f.read()
            except FileNotFoundError:
                click.echo(f"Error: File not found: {input_path}", err=True)
                sys.exit(1)
            except Exception as e:
                click.echo(f"Error reading file: {str(e)}", err=True)
                sys.exit(1)

        # Generate code
        try:
            code = generator.generate(html, class_name)
        except ValueError as e:
            click.echo(f"Error: {str(e)}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error generating code: {str(e)}", err=True)
            sys.exit(1)

        # Output code
        if output_path:
            # Write to file
            try:
                generator.save_to_file(code, output_path)
                click.echo(f"Generated: {output_path}")
                return
            except Exception as e:
                click.echo(f"Error writing output file: {str(e)}", err=True)
                sys.exit(1)
        else:
            # Write to stdout
            click.echo(code)
            return

    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
