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
    print("body", body)
    header_lines = header.split("\r\n")
    status_line = header_lines[0]
    match = re.match(r"HTTP/\d\.\d (\d+)", status_line)
    status_code = int(match.group(1)) if match else None
    headers = {}
    for line in header_lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v
    return status_code, headers, body

#construir respuesta http desde el server

import datetime
"""
	    Crea una respuesta HTTP/1.1 completa con los encabezados especificados y un cuerpo.
	
	    Args:
	        body_content (str): El contenido del cuerpo de la respuesta.
	        status_code (int): El código de estado HTTP.
	        status_message (str): El mensaje de estado asociado al código.
	
	    Returns:
	        bytes: La respuesta HTTP completa lista para ser enviada a través de un socket.
	    """
def build_http_response(body, status_code: int = 200, status_message: str = "OK") -> bytes:
    status_line = f"HTTP/1.1 {status_code} {status_message}\r\n"
    # Construir los encabezados
    print("body en build", body) 
    headers = [
        "Connection: close",
        f"Content-Length: {len(body)}",
        "Content-Type: text/xml", # Tu requisito específico
        f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Server: no sabe no contesta" ############## Tu requisito específico
    ]
    headers_block = "\r\n".join(headers) + "\r\n\r\n" # Doble \r\n al final para separar encabezados del cuerpo

    # Unir respuesta completa
    full_response = status_line + headers_block
    full_response_bytes = full_response.encode('utf-8') + body

    return full_response_bytes