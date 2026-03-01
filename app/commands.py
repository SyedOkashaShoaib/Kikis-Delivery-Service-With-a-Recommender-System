import click
from app import app
from app.vectorizer import compute_all_item_vectors, compute_item_similarity_matrix

@app.cli.command("recompute-vectors")
def recompute_vectors():
    with app.app_context():
        compute_all_item_vectors()
        compute_item_similarity_matrix()
        click.echo("Recomputed vectors")