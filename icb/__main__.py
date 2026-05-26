import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import typer

app = typer.Typer()

@app.command()
def init(
    output_dir: str = typer.Option(".", "--dir", "-d", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """Generate main.py, config.py and .env starter files."""
    from icb.extra.initiator import run
    run(output_dir, force)

@app.command()
def migrate():
    """Run database migration and generate modules."""
    from icb.extra.migrations import run
    typer.echo("Running migration...")
    run()
    typer.echo("Migration complete!")

@app.command()
def create_model():
    """Create or alter table in database"""
    import icb.sample.main as main
    from icb.extra.create_model import TableMigration
    from icb.core.model import Base
    from icb.core.db import engine
    Base.metadata.create_all(bind=engine)
    TableMigration().execute()

@app.command()
def drop_table_fields():
    """Drop columns not in model from database tables"""
    from icb.extra.drop_table_fields import DropTableMigration
    typer.echo("Dropping table fields...")
    DropTableMigration().execute()
    typer.echo("Drop table field complete!")

@app.command()
def drop_table_unused():
    """Drop unused tables in database"""
    from icb.extra.drop_table_unused import DropTableUnusedMigration
    typer.echo("Dropping unused table...")
    DropTableUnusedMigration().execute()
    typer.echo("Dropping unused table complete!")

@app.command()
def bootstrap(
    requirements: str = typer.Option("requirements.txt", "--req", "-r", help="Path to requirements file"),
    host: str = typer.Option("127.0.0.1", "--host", help="Uvicorn host"),
    port: int = typer.Option(8000, "--port", "-p", help="Uvicorn port"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload"),
    skip_install: bool = typer.Option(False, "--skip-install", help="Skip pip install step"),
    skip_model: bool = typer.Option(False, "--skip-model", help="Skip icb create-model step"),
):
    """Install requirements, run create-model, then start uvicorn."""
    # command to run :
    # python -m icb bootstrap
    # python -m icb bootstrap --skip-install --port 8080 --no-reload
    from icb.extra.bootstrap import run
    run(
        requirements=requirements,
        host=host,
        port=port,
        reload=reload,
        skip_install=skip_install,
        skip_model=skip_model,
    )

if __name__ == "__main__":
    app()