import click
from src.entrypoints.cli.calculate_irr import calculate_irr
import warnings
from src.utils.env_var_loader import env_var_loader


warnings.filterwarnings("ignore", category=UserWarning)


@click.group()
def cli():
    pass


cli.add_command(calculate_irr)

if __name__ == "__main__":
    env_var_loader(".env")
    cli()
