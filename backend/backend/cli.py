import click

@click.group()
def cli():
    """Backend CLI for Neuroscience Website"""
    pass

@cli.command()
def hello():
    click.echo("Hello from the backend CLI!")

if __name__ == "__main__":
    cli() 