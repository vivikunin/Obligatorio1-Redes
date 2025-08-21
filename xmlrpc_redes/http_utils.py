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

#construir respuesta http desde el server

	import datetime
	
	def build_http_response(body_content: str, status_code: int = 200, status_message: str = "OK") -> bytes:
	    """
	    Crea una respuesta HTTP/1.1 completa con los encabezados especificados y un cuerpo.
	
	    Args:
	        body_content (str): El contenido del cuerpo de la respuesta (ej. el XML-RPC).
	        status_code (int): El código de estado HTTP (ej. 200, 404).
	        status_message (str): El mensaje de estado asociado al código (ej. "OK", "Not Found").
	
	    Returns:
	        bytes: La respuesta HTTP completa lista para ser enviada a través de un socket.
	    """
	    body_bytes = body_content.encode('utf-8')
	    content_length = len(body_bytes)
	
	    current_gmt_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
	
	    status_line = f"HTTP/1.1 {status_code} {status_message}\r\n"
	
	    # Construir los encabezados
	    headers = [
	        "Connection: close",
	        f"Content-Length: {content_length}",
	        "Content-Type: text/xml", # Tu requisito específico
	        f"Date: {current_gmt_date}",
	        "Server: no sabe no contesta" ############## Tu requisito específico
	    ]
	
	    # Unir los encabezados con CRLF (salto de línea de Windows)
	    headers_block = "\r\n".join(headers) + "\r\n\r\n" # Doble CRLF al final para separar encabezados del cuerpo
	
	    # Unir todo
	    full_response = status_line + headers_block
	    full_response_bytes = full_response.encode('utf-8') + body_bytes
	
	    return full_response_bytes