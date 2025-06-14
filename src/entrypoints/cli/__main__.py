import click
from src.entrypoints.cli.calculate_irr import calculate_irr
import warnings
from dotenv import load_dotenv


warnings.filterwarnings("ignore", category=UserWarning)


@click.group()
def cli():
    pass


cli.add_command(calculate_irr)

if __name__ == "__main__":
    load_dotenv(dotenv_path=".env", override=True)
    cli()
