import re

"Construye un mensaje HTTP POST con cuerpo XML."
def build_http_post_request(path: str, host: str, body: str) -> str:
    headers = [
        f"POST {path} HTTP/1.1",
        f"Host: {host}",
        "Content-Type: text/xml",
        f"Content-Length: {len(body.encode('utf-8'))}",
        "",
        ""
    ]
    request = "\r\n".join(headers) + body
    return request

"Parsea una respuesta HTTP y retorna (status_code, headers_dict, body)."
def parse_http_response(response: str) -> tuple:
    header, _, body = response.partition("\r\n\r\n")
    header_lines = header.split("\r\n")
    status_line = header_lines[0]
    match = re.match(r"HTTP/\d\.\d (\d+)", status_line)
    status_code = int(match.group(1)) if match else None
    headers = {}
    for line in header_lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v