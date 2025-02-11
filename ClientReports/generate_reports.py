import logging.handlers
import os
import sys
from typing import Dict, List
import tableauserverclient as TSC
import argparse
import logging
import json
from dataclasses import dataclass
from PyPDF2 import PdfMerger

pages_ids_en = [
    "4e8a17eb-0d30-4161-bcf7-46d3044cc88b",
    "54ba008c-546e-4c89-a7e5-104ccc4284ef",
    "a8d2b65d-47b3-432d-935d-590b79d2f1a1",
    "3a464694-bb10-4173-96fb-0371a8e2e173",
    "bf32ac95-f644-4355-98a6-6d2bef9cb62f",
]
pages_ids_fr = [
    "87208742-47ab-46b4-9c61-6641121c7b3c",
    "7163d8a5-e5c8-4173-a4c7-65678751d9f7",
    "b3edb664-5c59-4175-8b61-5e89ecbdd962",
    "8b6bab27-1670-4eb8-bbf0-3be8bab5e376",
    "bb2702de-f132-4eb1-a763-683aa3e0f9aa",
]

portfolios_en = ["BRLP", "CAP", "PSDI", "JUS", "IRRP", "TLS"]
portfolios_fr = ["PDADR", "POC", "SPDI", "JUS", "PDRA", "SDF"]

merged_folder = "merged"


@dataclass
class Client:
    cmr_number: str
    portfolio_short_en: str
    portfolio_short_fr: str
    client_name_short_en: str
    client_name_short_fr: str


@dataclass
class Clients:
    clients: List[Client]

    @classmethod
    def from_json(cls, json_path: str) -> "Clients":
        with open(json_path, "r") as f:
            data = json.load(f)
            return cls(
                clients=[
                    Client(
                        cmr_number=c["CmrNumber"],
                        portfolio_short_en=c["PortfolioShortEN"],
                        portfolio_short_fr=c["PortfolioShortFR"],
                        client_name_short_en=c["ClientNameShortEN"],
                        client_name_short_fr=c["ClientNameShortFR"],
                    )
                    for c in data["Clients"]
                ]
            )


def create_portfolio_directories(
    portfolios: List[str], root_dir: str = None, language: str = "EN"
) -> str:
    # Create output directory
    if not root_dir:
        logging.debug("No output directory specified. Using current directory")
        root_dir = os.path.join(os.getcwd())

    for portfolio in portfolios:
        output_dir = os.path.join(root_dir, language, portfolio)
        merged_output_dir = os.path.join(root_dir, merged_folder, language, portfolio)
        logging.info(f"Creating directory {output_dir}")
        try:
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(merged_output_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating output directory: {e}")


def initialize_tableau_server(
    username: str, password: str, server: str = "tableau", site: str = None
):
    tableau_auth = TSC.TableauAuth(username, password, site)
    server = TSC.Server(f"https://{server}.justice.gc.ca")
    server.version = "3.14"
    server.add_http_options({"verify": False})
    return server, tableau_auth


def generate_pdf_report(
    server: TSC.Server,
    auth,
    views: List[Dict[str, str]],
    clients: Clients,
    language: str,
    cut_off_date: str,
    file_path: str | None = None,
):
    with server.auth.sign_in(auth):
        for view in views:
            view_item = server.views.get_by_id(view[1])
            pdf_req_option = TSC.PDFRequestOptions(
                page_type=TSC.PDFRequestOptions.PageType.Letter,
                orientation=TSC.PDFRequestOptions.Orientation.Portrait,
            )
            for client in clients:
                pdf_req_option.vf(f"Client{view[0]}B", int(client.cmr_number))
                pdf_req_option.vf(f"Cut-Off Date{view[0]}", cut_off_date)

                server.views.populate_pdf(view_item, pdf_req_option)

                try:
                    _save_report(view_item, client, language, view[0], file_path)
                except Exception as e:
                    logging.error(f"Error saving report to file: {e}")


def _save_report(
    view: TSC.ViewItem, client: Client, language: str, page_number: int, file_path: str
):
    # Save report to file
    if language == "EN":
        portfolio_short_name = client.portfolio_short_en
        client_short_name = client.client_name_short_en
    else:
        portfolio_short_name = client.portfolio_short_fr
        client_short_name = client.client_name_short_fr

    if not file_path:
        file_path = os.path.join(os.getcwd(), language)

    client_dir = os.path.join(file_path, portfolio_short_name, client_short_name)

    path = os.path.join(client_dir, f"PAGE_{page_number}.pdf")

    try:
        os.makedirs(client_dir, exist_ok=True)
        logging.info("Creating directory: " + client_dir)
    except Exception as e:
        logging.error(f"Error creating directory: {e}")

    try:
        with open(path, "wb") as f:
            f.write(view.pdf)
        logging.info(f"Saved report to {path}")
    except Exception as e:
        logging.error(f"Error saving report to file: {e}")


def get_view_ids(page_numbers: List[str], language: str) -> List[Dict[str, str]]:
    view_ids = []
    for page in page_numbers:
        if language == "EN":
            view_ids.append((page, pages_ids_en[int(page) - 1]))
        else:
            view_ids.append((page, pages_ids_fr[int(page) - 1]))
    return view_ids


def merge_pdfs(root_dir: str | None, language: str):
    """Merge all PDFs for each client into a single file"""
    logging.info(f"Merging PDFs for {language} reports")

    if not root_dir:
        logging.debug("No output directory specified. Using current directory")
        root_dir = os.path.join(os.getcwd())

    path = os.path.join(root_dir, merged_folder, language)

    portfolios = portfolios_en if language == "EN" else portfolios_fr

    for portfolio in portfolios:
        # Create merged folder if it doesn't exist
        os.makedirs(os.path.join(path, portfolio), exist_ok=True)

        portfolio_path = os.path.join(root_dir, language, portfolio)
        clients = os.listdir(portfolio_path)

        for client in clients:
            client_path = os.path.join(portfolio_path, client)

            if not os.path.isdir(client_path):
                continue

            pdfs = sorted([f for f in os.listdir(client_path) if f.endswith(".pdf")])

            if not pdfs:
                continue

            merger = PdfMerger()

            try:
                for pdf in pdfs:
                    merger.append(os.path.join(client_path, pdf))

                output_path = os.path.join(path, portfolio, f"{client}.pdf")
                merger.write(output_path)
                merger.close()

                logging.info(f"Merged PDF for {client} into {output_path}")

            except Exception as e:
                logging.error(f"Error merging PDFs for {client}: {e}")
                continue


def main():
    # parse arguments
    parser = argparse.ArgumentParser(
        description="Export client reports pages from Tableau server and merge them into a single PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Export reports:
    python generate_reports.py export jdoe password123 tableau all 2024-03-31 --language EN
  
  Merge PDFs:
    python generate_reports.py merge --language EN --output ./reports
        """,
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Export command parser
    export_parser = subparsers.add_parser("export", help="Export reports from Tableau", description="Export client reports from Tableau")
    export_parser.add_argument("username", type=str, help="Tableau server username")
    export_parser.add_argument("password", type=str, help="Tableau server password")
    export_parser.add_argument("server", type=str, help="Tableau server address")
    export_parser.add_argument("client", type=str, help="Client cmr number or all")
    export_parser.add_argument(
        "cut_off_date", type=str, help="Cut-off date for reports"
    )
    export_parser.add_argument(
        "--page",
        "-p",
        choices=["1", "2", "3", "4", "5", "all"],
        default="1",
        help="Page number to generate",
    )
    export_parser.add_argument("--site", "-s", type=str, help="Tableau server site")

    # Merge command parser
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge PDF reports",
        description="Merge individual PDF reports into a single file by client.",
    )

    # Common arguments for both commands
    for p in [export_parser, merge_parser]:
        p.add_argument(
            "--language",
            "-lang",
            choices=["EN", "FR", "all"],
            default="EN",
            help="Language of reports",
        )
        p.add_argument("--output", "-o", type=str, help="Output directory")
        p.add_argument(
            "--log-level",
            "-l",
            choices=["debug", "info", "error"],
            default="info",
            help="Logging level",
        )

    args = parser.parse_args()    

    # Set logging configuration
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    try:
        logging.info("Creating English portfolio directories")
        create_portfolio_directories(portfolios_en, args.output, "EN")

        logging.info("Creating French portfolio directories")
        create_portfolio_directories(portfolios_fr, args.output, "FR")

        if args.language == "all":
            languages = ["EN", "FR"]
        else:
            languages = [args.language]

        if args.command == "export":
            if not all(
                [args.username, args.password, args.server, args.client, args.cut_off_date]
            ):
                parser.error(
                    "--export requires username, password, server, client and cut-off date arguments"
                )
            try:
                
                if args.page == "all":
                    page_numbers = ["1", "2", "3", "4", "5"]
                else:
                    page_numbers = [args.page]                

                server, tableau_auth = initialize_tableau_server(
                    args.username, args.password, args.server, args.site
                )

                clients = Clients.from_json("clients.json")

                if args.client != "all":
                    clients = [c for c in clients.clients if c.cmr_number == args.client]
                else:
                    clients = clients.clients

                for language in languages:
                    view_ids = get_view_ids(page_numbers, language)
                    generate_pdf_report(
                        server, tableau_auth, view_ids, clients, language, args.cut_off_date
                    )
            except Exception as e:
                logging.error(f"An error occured while exporting reports: {e}")
            finally:
                if "server" in locals() and hasattr(server, "auth"):
                    server.auth.sign_out()

        # merge all pdfs into one
        if args.command == "merge":
            for language in languages:
                merge_pdfs(args.output, language)

    except Exception as e:        
        logging.error(f"An error occured while running this script: {e}")



if __name__ == "__main__":
    main()
