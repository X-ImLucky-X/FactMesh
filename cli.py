import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import glob
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from backend.knowledge_layer import FactKnowledgeLayer
from backend.showcase_cases import get_showcase_cases
from backend.models import RelationshipType

console = Console(highlight=False)

def get_layer() -> FactKnowledgeLayer:
    layer = FactKnowledgeLayer()
    layer.load_state()
    return layer

def cmd_load(args):
    """Loads a starter dataset."""
    layer = get_layer()
    dataset_name = args.dataset.lower()
    from backend import config
    target_dir = config.DATASET_DIR / dataset_name
    if not target_dir.exists():
        if "delhi" in dataset_name:
            target_dir = config.DATASET_DIR / "delhivery"
        elif "macro" in dataset_name or "india" in dataset_name:
            target_dir = config.DATASET_DIR / "india-macroeconomy"
        else:
            console.print(f"[bold red]Error: Dataset '{dataset_name}' not found.[/bold red]")
            return

    pdf_files = list(target_dir.glob("*.pdf"))
    console.print(f"[bold cyan]Ingesting {len(pdf_files)} PDFs from {target_dir.name}...[/bold cyan]")
    res = layer.ingest_multiple([str(p) for p in pdf_files])
    console.print(f"[bold green]✓ Ingestion Complete![/bold green] Ingested {res['documents_ingested']} documents.")
    console.print(f"Total Facts: [bold yellow]{res['total_facts']}[/bold yellow] | Relationships: [bold yellow]{res['total_relationships']}[/bold yellow]")

def cmd_ingest(args):
    """Ingests custom PDF files."""
    layer = get_layer()
    files = []
    for pattern in args.files:
        matched = glob.glob(pattern)
        if matched:
            files.extend(matched)
        else:
            files.append(pattern)

    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
    if not pdf_files:
        console.print("[bold red]No valid PDF files provided.[/bold red]")
        return

    console.print(f"[bold cyan]Ingesting {len(pdf_files)} PDF(s)...[/bold cyan]")
    res = layer.ingest_multiple(pdf_files)
    console.print(f"[bold green]✓ Ingestion Complete![/bold green] Total Facts: {res['total_facts']}")

def cmd_facts(args):
    """Lists extracted facts."""
    layer = get_layer()
    facts = layer.get_facts(document_filter=args.doc, entity_filter=args.entity, query=args.query)

    if not facts:
        console.print("[yellow]No facts found matching criteria. Use 'python cli.py load --dataset delhivery' first.[/yellow]")
        return

    table = Table(title=f"Extracted Facts ({len(facts)} items)", show_header=True, header_style="bold magenta")
    table.add_column("Entity", style="bold cyan")
    table.add_column("Attribute", style="white")
    table.add_column("Value", style="bold green")
    table.add_column("Period", style="yellow")
    table.add_column("Document & Page", style="dim")

    for f in facts[:args.limit]:
        table.add_row(
            f.entity,
            f.attribute,
            f"{f.raw_value or f.value} {f'({f.unit})' if f.unit else ''}",
            f.temporal_context or "—",
            f"{Path(f.document_name).name} (p.{f.page_number})"
        )

    console.print(table)
    if len(facts) > args.limit:
        console.print(f"[dim]... and {len(facts) - args.limit} more facts (use --limit to see more).[/dim]")

def cmd_relationships(args):
    """Lists cross-document relationships."""
    layer = get_layer()
    rels = layer.get_relationships()

    if not rels:
        console.print("[yellow]No relationships found. Run 'python cli.py load' or 'python cli.py reconcile' first.[/yellow]")
        return

    table = Table(title=f"Cross-Document Relationships ({len(rels)} items)", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="bold")
    table.add_column("Attribute", style="cyan")
    table.add_column("Doc 1 Evidence", style="white")
    table.add_column("Doc 2 Evidence", style="white")
    table.add_column("Key Takeaway", style="yellow")

    for r in rels[:args.limit]:
        type_color = "green" if r.relationship_type == RelationshipType.CORROBORATED else ("red" if r.relationship_type == RelationshipType.CONTRADICTION else "yellow")
        table.add_row(
            f"[{type_color}]{r.relationship_type.value}[/{type_color}]",
            r.source_fact.attribute if r.source_fact else "—",
            f"{r.source_fact.raw_value or r.source_fact.value} (p.{r.source_fact.page_number})" if r.source_fact else "—",
            f"{r.target_fact.raw_value or r.target_fact.value} (p.{r.target_fact.page_number})" if r.target_fact else "—",
            r.key_takeaway
        )

    console.print(table)

def cmd_cases(args):
    """Displays the four required showcase cases with citations and reasoning."""
    dataset = args.dataset or "delhivery"
    cases = get_showcase_cases(dataset)

    console.print(Panel(f"[bold yellow]SHOWCASE: FOUR REQUIRED CASES[/bold yellow]\n[cyan]Dataset: {cases.dataset_name}[/cyan]", style="bold blue"))

    # Case 1
    c1 = cases.case_1_corroboration
    console.print(Panel(
        f"[bold green]🤝 {c1['title']}[/bold green]\n"
        f"Entity: [cyan]{c1['entity']}[/cyan] | Attribute: [cyan]{c1['attribute']}[/cyan] | Value: [bold]{c1['value']}[/bold]\n\n"
        f"[bold]Evidence Sources:[/bold]\n" +
        "\n".join([f"  • [yellow]{s['document']}[/yellow] (p.{s['page']}): \"{s['quote']}\"" for s in c1['evidence_sources']]) +
        f"\n\n[bold]System Reasoning:[/bold]\n{c1['system_reasoning']}",
        title="Case 1: Corroboration",
        border_style="green"
    ))

    # Case 2
    c2 = cases.case_2_contradiction
    console.print(Panel(
        f"[bold red]⚡ {c2['title']}[/bold red]\n"
        f"Entity: [cyan]{c2['entity']}[/cyan] | Attribute: [cyan]{c2['attribute']}[/cyan]\n\n"
        f"[bold]Evidence Sources:[/bold]\n" +
        "\n".join([f"  • [yellow]{s['document']}[/yellow] (p.{s['page']}): \"{s['quote']}\"" for s in c2['evidence_sources']]) +
        f"\n\n[bold]System Reasoning:[/bold]\n{c2['system_reasoning']}",
        title="Case 2: Genuine Contradiction",
        border_style="red"
    ))

    # Case 3
    c3 = cases.case_3_apparent_contradiction_explained
    console.print(Panel(
        f"[bold yellow]🔍 {c3['title']}[/bold yellow]\n"
        f"Entity: [cyan]{c3['entity']}[/cyan] | Attribute: [cyan]{c3['attribute']}[/cyan]\n\n"
        f"[bold]Evidence Sources:[/bold]\n" +
        "\n".join([f"  • [yellow]{s['document']}[/yellow] (p.{s['page']} - {s.get('temporal_context','')}): \"{s['quote']}\"" for s in c3['evidence_sources']]) +
        f"\n\n[bold]Contextual Breakdown:[/bold]\n" +
        "\n".join([f"  • [bold]{k.upper()}:[/bold] {v}" for k, v in (c3.get('context_resolution') or {}).items()]) +
        f"\n\n[bold]System Reasoning:[/bold]\n{c3['system_reasoning']}",
        title="Case 3: Apparent Contradiction Explained by Context",
        border_style="yellow"
    ))

    # Case 4
    c4 = cases.case_4_failure_and_remediation
    console.print(Panel(
        f"[bold magenta]🛡️ {c4.failure_title}[/bold magenta]\n"
        f"Document: [yellow]{c4.document_name}[/yellow] (p.{c4.page_number}) | Failure Type: [red]{c4.failure_type}[/red]\n\n"
        f"[bold]Problematic Extraction:[/bold]\n\"{c4.problematic_extraction}\"\n\n"
        f"[bold]Root Cause:[/bold]\n{c4.root_cause}\n\n"
        f"[bold]Handling & Remediation:[/bold]\n{c4.handling_and_remediation}\n\n"
        f"[bold green]Fixed Output:[/bold green]\n{c4.fixed_or_mitigated_output}",
        title="Case 4: Extraction/Reasoning Failure & Remediation",
        border_style="magenta"
    ))

def cmd_query(args):
    """Semantic question answering."""
    layer = get_layer()
    q = args.question
    console.print(f"[bold cyan]Query:[/bold cyan] {q}\n")
    res = layer.answer_query(q)
    console.print(Panel(res.answer, title="Fact Knowledge Layer Response", border_style="cyan"))

def main():
    parser = argparse.ArgumentParser(description="Fact Knowledge Layer CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # load
    p_load = subparsers.add_parser("load", help="Load starter dataset")
    p_load.add_argument("--dataset", default="delhivery", help="Dataset name: 'delhivery' or 'india-macroeconomy'")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Ingest custom PDF documents")
    p_ingest.add_argument("files", nargs="+", help="Path(s) to PDF files or glob pattern")

    # facts
    p_facts = subparsers.add_parser("facts", help="List extracted facts")
    p_facts.add_argument("--doc", help="Filter by document name")
    p_facts.add_argument("--entity", help="Filter by entity name")
    p_facts.add_argument("--query", help="Filter by search query")
    p_facts.add_argument("--limit", type=int, default=25, help="Max facts to show")

    # relationships
    p_rels = subparsers.add_parser("relationships", help="List cross-document relationships")
    p_rels.add_argument("--limit", type=int, default=25, help="Max relationships to show")

    # cases
    p_cases = subparsers.add_parser("cases", help="Showcase the four required cases")
    p_cases.add_argument("--dataset", default="delhivery", help="Dataset name: 'delhivery' or 'india-macroeconomy'")

    # query
    p_query = subparsers.add_parser("query", help="Ask a question across the fact knowledge layer")
    p_query.add_argument("question", help="Natural language question")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "load":
        cmd_load(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "facts":
        cmd_facts(args)
    elif args.command == "relationships":
        cmd_relationships(args)
    elif args.command == "cases":
        cmd_cases(args)
    elif args.command == "query":
        cmd_query(args)

if __name__ == "__main__":
    main()
