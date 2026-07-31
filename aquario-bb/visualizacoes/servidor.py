#!/usr/bin/env python3
"""Servidor minimo para o painel Aquario BB."""
import http.server
import socketserver
import threading
import webbrowser
import sys

PORT = 8000
DIRETORIO = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRETORIO, **kwargs)

    def log_message(self, formato, *args):
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), formato % args))

def abrir_navegador(url):
    webbrowser.open(url)

if __name__ == "__main__":
    url = "http://localhost:%d/index.html" % PORT
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print("Painel Aquario BB disponivel em: %s" % url)
        print("Pressione Ctrl+C para encerrar.")
        threading.Timer(0.8, abrir_navegador, args=(url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrando servidor.")
