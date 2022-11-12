import argparse
import gzip
import json
import socket
import sys
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

import pdftotext  # type: ignore

READ_BYTES = 1024 * 16


def find_ip() -> Optional[str]:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0)
        try:
            sock.connect(("10.255.255.255", 1))
            return sock.getsockname()[0]
        except OSError:
            return None


def pdf2json(pdf: BytesIO) -> str:
    return json.dumps(list(pdftotext.PDF(pdf)))


def parse_local(pdf: Path, out: Optional[Path]):
    json = pdf2json(BytesIO(pdf.read_bytes()))
    if out is None:
        print(json)
    else:
        out.write_text(json)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["directory"] = "web"
        super().__init__(*args, **kwargs)

    def do_POST(self) -> None:
        self.log_message(self.requestline)
        headers: Dict[str, str] = dict(
            tuple(head.split(":", 1))  # type: ignore
            for head in str(self.headers).splitlines()
            if head.strip() != ""
        )

        msg_len = int(headers["Content-Length"])
        boundary = headers["Content-Type"].split("=")[1].strip()
        self.log_message(f"Content-Length: {msg_len}")
        self.log_message(f"Boundary: {boundary}")

        buf = []
        while True:
            msg = self.rfile.read(msg_len)
            if msg == b"":
                self.log_message("EOF")
                break
            buf.append(msg)
            msg_len -= len(msg)
        msg = Handler.parse_file(b"".join(buf), boundary.encode("utf-8"))
        try:
            now = time.time()
            json = pdf2json(BytesIO(msg)).encode("utf-8")
            delta = time.time() - now
            self.log_message(f"Converted PDF in {delta:.6f} seconds")
        except pdftotext.Error as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Invalid PDF", str(e))
            return

        json_zip = gzip.compress(json)
        cmp_ratio = 1 - (len(json_zip) / len(json))
        # NOTE: Need to escape '%' since `log_message` treats it as a format
        # string.
        self.log_message(f"Compressed JSON by {cmp_ratio:.2%}".replace("%", "%%"))

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(json_zip)))
        self.end_headers()
        self.wfile.write(json_zip)

    @staticmethod
    def parse_file(msg: bytes, boundary: bytes) -> bytes:
        start = msg.find(b"\r\n\r\n")
        assert start != -1
        start += 4
        end = msg.find(boundary, start)
        assert end != -1
        msg = msg[start:end].rstrip(b"\n\r\n--")
        return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to JSON.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=80,
        help="port number",
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="file to convert locally (optional)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="where to write output (defaults to stdout)",
    )
    args = parser.parse_args()

    pdf = args.file
    if pdf is not None:
        parse_local(pdf, args.output)
        sys.exit()

    host = find_ip()
    port = args.port

    if host is None:
        host = "0.0.0.0"

    with HTTPServer(("0.0.0.0", port), Handler) as serv:
        print(f"Pdf2Json (http://{host}:{port})")
        try:
            serv.serve_forever()
        except KeyboardInterrupt:
            pass
