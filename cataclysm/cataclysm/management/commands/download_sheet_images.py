import ipaddress
import mimetypes
import os
import re
import socket
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.text import slugify

from people.models import Person
from species.models import Species

from cataclysm.utils.google_sheets import extract_spreadsheet_id, read_sheet_data


DEFAULT_SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "").strip()
DEFAULT_TABS = ("Main Crew", "Other Crew")
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}
DEFAULT_USER_AGENT = "CataclysmAppImageSync/1.0"


def _url_from_cell(value: str) -> str | None:
    if not value:
        return None
    match = URL_RE.search(value.strip())
    if not match:
        return None
    url = match.group(0)
    if url and url[-1] in {")", "]", ",", ";"}:
        return url[:-1]
    return url


def _url_from_column(row: list[str], index: int | None) -> str | None:
    if index is None or index < 0 or index >= len(row):
        return None
    return _url_from_cell(row[index])


def _extract_row_urls(row: list[str]) -> list[str]:
    urls: list[str] = []
    seen = set()
    for cell in row:
        found = _url_from_cell(cell)
        if found and found not in seen:
            seen.add(found)
            urls.append(found)
    return urls


def _row_url_pair(row: list[str], person_url_col: int | None, species_url_col: int | None) -> tuple[str | None, str | None]:
    person_url = _url_from_column(row, person_url_col)
    species_url = _url_from_column(row, species_url_col)
    if person_url_col is not None or species_url_col is not None:
        return person_url, species_url

    urls = _extract_row_urls(row)
    if not urls:
        return None, None
    person_url = urls[0]
    species_url = urls[1] if len(urls) > 1 else None
    return person_url, species_url


def _is_private_or_local_host(hostname: str) -> bool:
    if hostname.lower() == "localhost":
        return True

    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            resolved = socket.getaddrinfo(hostname, None)
        except socket.gaierror as exc:
            raise ValueError(f"Could not resolve download host: {hostname}") from exc
        addresses = {ipaddress.ip_address(entry[4][0]) for entry in resolved}

    return any(
        address.is_loopback
        or address.is_private
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
        for address in addresses
    )


def _validate_download_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"Unsupported URL scheme for download: {parsed.scheme!r}")
    if not parsed.hostname:
        raise ValueError("Download URL is missing a hostname.")
    if _is_private_or_local_host(parsed.hostname):
        raise ValueError(f"Refusing to download from private/local host: {parsed.hostname}")


def _guess_extension(url: str, content_type: str | None) -> str | None:
    parsed_path = urlparse(url).path
    ext = os.path.splitext(parsed_path)[1].lower()
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return ext
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed:
            # Python can return ".jpe" for JPEG content types; normalize to ".jpg".
            normalized = ".jpg" if guessed == ".jpe" else guessed
            if normalized in SUPPORTED_IMAGE_EXTENSIONS:
                return normalized
    return None


def _download_image(url: str, timeout: int = 10, max_bytes: int = 10 * 1024 * 1024) -> tuple[bytes, str]:
    _validate_download_url(url)
    response = requests.get(
        url,
        timeout=timeout,
        allow_redirects=False,
        stream=True,
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )
    try:
        response.raise_for_status()
        content_type = response.headers.get("Content-Type")
        if content_type and not content_type.split(";")[0].strip().lower().startswith("image/"):
            raise ValueError(f"Refusing non-image content type for {url}: {content_type}")

        content_length = response.headers.get("Content-Length")
        if content_length and content_length.isdigit() and int(content_length) > max_bytes:
            raise ValueError(f"Refusing download larger than {max_bytes} bytes for URL: {url}")

        extension = _guess_extension(url, content_type)
        if not extension:
            raise ValueError(f"Could not determine a safe image extension for URL: {url}")

        data = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            data.extend(chunk)
            if len(data) > max_bytes:
                raise ValueError(f"Refusing download larger than {max_bytes} bytes for URL: {url}")

        return bytes(data), extension
    finally:
        response.close()


class Command(BaseCommand):
    help = "Download person/species images from Google Sheet Main Crew and Other Crew tabs."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--spreadsheet-id",
            default=DEFAULT_SPREADSHEET_ID,
            help="Google spreadsheet URL or ID (defaults to SPREADSHEET_ID env var).",
        )
        parser.add_argument(
            "--tabs",
            nargs="+",
            default=list(DEFAULT_TABS),
            help="Sheet tab names to process (default: Main Crew Other Crew).",
        )
        parser.add_argument("--start-row", type=int, default=5, help="First row number to read in each tab (default: 5).")
        parser.add_argument("--end-column", default="ZZ", help="Last column letter to read (default: ZZ).")
        parser.add_argument("--person-name-col", type=int, default=0, help="Zero-based person name column index (default: 0).")
        parser.add_argument("--species-name-col", type=int, default=1, help="Zero-based species name column index (default: 1).")
        parser.add_argument(
            "--person-url-col",
            type=int,
            default=None,
            help="Zero-based person image URL column index. If omitted, first URL in row is used.",
        )
        parser.add_argument(
            "--species-url-col",
            type=int,
            default=None,
            help="Zero-based species image URL column index. If omitted, second URL in row is used.",
        )
        parser.add_argument("--overwrite", action="store_true", help="Overwrite existing image fields.")
        parser.add_argument("--dry-run", action="store_true", help="Report what would be downloaded without writing files.")
        parser.add_argument("--timeout", type=int, default=10, help="Download timeout in seconds (default: 10).")
        parser.add_argument(
            "--max-bytes",
            type=int,
            default=10 * 1024 * 1024,
            help="Maximum bytes allowed per image download (default: 10485760).",
        )

    def _save_image(
        self,
        obj,
        url: str,
        base_name: str,
        dry_run: bool,
        overwrite: bool,
        download_cache: dict[str, tuple[bytes, str]],
        timeout: int,
        max_bytes: int,
    ) -> str:
        image_field = obj.image
        if image_field and not overwrite:
            return "skipped_existing"
        if dry_run:
            return "would_update"

        if url in download_cache:
            data, ext = download_cache[url]
        else:
            data, ext = _download_image(url, timeout=timeout, max_bytes=max_bytes)
            download_cache[url] = (data, ext)

        filename = f"{slugify(base_name) or 'image'}{ext}"
        image_field.save(filename, ContentFile(data), save=False)
        obj.save(update_fields=["image"])
        return "updated"

    def handle(self, *args, **options):
        spreadsheet_id = extract_spreadsheet_id(options["spreadsheet_id"])
        tabs = options["tabs"]
        start_row = options["start_row"]
        end_column = options["end_column"]
        person_name_col = options["person_name_col"]
        species_name_col = options["species_name_col"]
        person_url_col = options["person_url_col"]
        species_url_col = options["species_url_col"]
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]
        timeout = options["timeout"]
        max_bytes = options["max_bytes"]

        if not spreadsheet_id:
            raise CommandError("Provide --spreadsheet-id or set the SPREADSHEET_ID environment variable.")
        if timeout <= 0:
            raise CommandError("--timeout must be a positive integer.")
        if max_bytes <= 0:
            raise CommandError("--max-bytes must be a positive integer.")

        stats = {
            "rows": 0,
            "people_updated": 0,
            "species_updated": 0,
            "people_skipped_existing": 0,
            "species_skipped_existing": 0,
            "people_missing": 0,
            "species_missing": 0,
            "people_errors": 0,
            "species_errors": 0,
            "people_would_update": 0,
            "species_would_update": 0,
        }
        download_cache: dict[str, tuple[bytes, str]] = {}

        for tab_name in tabs:
            range_name = f"{tab_name}!A{start_row}:{end_column}"
            rows = read_sheet_data(spreadsheet_id, range_name)
            if rows is None:
                self.stderr.write(self.style.WARNING(f"Failed to read tab '{tab_name}' ({range_name})."))
                continue

            for row_index, row in enumerate(rows, start=start_row):
                person_name = (row[person_name_col] if len(row) > person_name_col else "").strip()
                species_name = (row[species_name_col] if len(row) > species_name_col else "").strip()
                person_url, species_url = _row_url_pair(row, person_url_col, species_url_col)

                if not person_name and not species_name:
                    continue
                stats["rows"] += 1

                if person_name and person_url:
                    person = Person.objects.filter(name__iexact=person_name).first()
                    if not person:
                        stats["people_missing"] += 1
                    else:
                        try:
                            result = self._save_image(
                                person,
                                person_url,
                                person.name,
                                dry_run,
                                overwrite,
                                download_cache,
                                timeout=timeout,
                                max_bytes=max_bytes,
                            )
                            stats[f"people_{result}"] += 1
                        except (requests.RequestException, OSError, ValueError) as exc:
                            stats["people_errors"] += 1
                            self.stderr.write(
                                self.style.ERROR(f"[{tab_name} row {row_index}] Person '{person_name}' failed: {exc}")
                            )

                if species_name and species_url:
                    species = Species.objects.filter(species_name__iexact=species_name).first()
                    if not species:
                        stats["species_missing"] += 1
                    else:
                        try:
                            result = self._save_image(
                                species,
                                species_url,
                                species.species_name,
                                dry_run,
                                overwrite,
                                download_cache,
                                timeout=timeout,
                                max_bytes=max_bytes,
                            )
                            stats[f"species_{result}"] += 1
                        except (requests.RequestException, OSError, ValueError) as exc:
                            stats["species_errors"] += 1
                            self.stderr.write(
                                self.style.ERROR(f"[{tab_name} row {row_index}] Species '{species_name}' failed: {exc}")
                            )

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                prefix
                + (
                    f"Processed rows={stats['rows']} "
                    f"people(updated={stats['people_updated']}, would_update={stats['people_would_update']}, "
                    f"skipped_existing={stats['people_skipped_existing']}, missing={stats['people_missing']}, errors={stats['people_errors']}) "
                    f"species(updated={stats['species_updated']}, would_update={stats['species_would_update']}, "
                    f"skipped_existing={stats['species_skipped_existing']}, missing={stats['species_missing']}, errors={stats['species_errors']})"
                )
            )
        )
