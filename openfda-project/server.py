#INICIO
import http.server
import http.client
import json
import socketserver

IP = "localhost"
PORT = 8000

socketserver.TCPServer.allow_reuse_address = True

#HERENCIA
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    pagina_fda = "api.fda.gov"
    fda_json = "/drug/label.json"
    search_drug = '&search=active_ingredient:'
    search_company = '&search=openfda.manufacturer_name:'

    #FORMULARIO HTML
    def get_html(self):
        html = """
            <!DOCTYPE html>
            <html>
            <head>
              <title>OpenFDA</title>
            </head>
            <body style="background-color: #00FF80;">

            <h1>OpenFDA</h1>
            <a><i>En los campos en los que ponga limite debera introducir el limite de elementos que desee recibir.</a></i><br>
            <a><i>Debe rellenar uno de los siguientes formularios.</a></i><br>

            <form action = "searchDrug" method="get">
            	<a>Buscar medicamento:</a><br>
              <input type="text" name="active_ingredient" value=""><br>
              Limite: <input type="text" name="limit" value=""><br>
              <input type="submit" value="Buscar">
            </form>

            <form action = "listDrugs" method="get">
            	<a>Lista de medicamentos:</a><br>
              Limite: <input type="text" name="limit" value=""><br>
              <input type="submit" value="Buscar">
            </form>

            <form action = "searchCompany" method="get">
            	<a>Buscar empresa:</a><br>
              <input type="text" name="company" value=""><br>
              Limite: <input type="text" name="limit" value=""><br>
              <input type="submit" value="Buscar">
            </form>

            <form action = "listCompanies" method="get">
            	<a>Lista de empresas:</a><br>
              Limite: <input type="text" name="limit" value=""><br>
            	<input type="submit" value="Buscar">
            </form>
            <form method="get" action="listWarnings">
                <input type = "submit" value="Warnings">
                </input>
            </form>

            </body>
            </html>
                """
        return html

    def get_data(self, lista):
        data_html = """
            <html>
            <head>
                <title>OpenFDA</title>
            </head>
            <body style='background-color: #00FF80'>
            <h2> Estas son las listas de datos obtenidas: </h2>
                <ul>
                """
        for elem in lista:
            data_html += "<li>" + elem + "</li>"

        data_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return data_html

    def get_resultados(self, limit=10):
        conexion = http.client.HTTPSConnection(self.pagina_fda)
        conexion.request("GET", self.fda_json + "?limit=" + str(limit))
        print(self.fda_json + "?limit=" + str(limit))
        respuesta = conexion.getresponse()
        print(respuesta.status, respuesta.reason)
        data_raw = respuesta.read().decode("utf8")
        data = json.loads(data_raw)
        resultados = data['results']
        return resultados

    def do_GET(self):
        division = self.path.split("?")
        if len(division) > 1:
            elemento = division[1]
        else:
            elemento = ""
        limit = 1
        if elemento:
            info = elemento.split("=")
            if info[0] == "limit":
                limit = int(info[1])
                print("Limit: {}".format(limit))
        else:
            print("Error.")


        #CONDICIONALES
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.get_html()
            self.wfile.write(bytes(html, "utf8"))

        elif 'searchDrug' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            active_ingredient = self.path.split('=')[1]

            lista_medicamentos = []
            conexion = http.client.HTTPSConnection(self.pagina_fda)
            conexion.request("GET",self.fda_json + "?limit=" + str(limit) + self.search_drug + active_ingredient)
            respuesta = conexion.getresponse()
            datos_raw = respuesta.read().decode('utf8')

            info_medicamentos = json.loads(datos_raw)['results']

            for elem in info_medicamentos:
                if ('generic_name' in elem['openfda']):
                    lista_medicamentos.append(elem['openfda']['generic_name'][0])
                else:
                    lista_medicamentos.append('Unknown')

            medicamentos_html = self.get_data(lista_medicamentos)
            self.wfile.write(bytes(medicamentos_html, "utf8"))


        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_medicamentos = []
            info_medicamentos = self.get_resultados(limit)

            for elem in info_medicamentos:
                if ('generic_name' in elem['openfda']):
                    lista_medicamentos.append(elem['openfda']['generic_name'][0])
                else:
                    lista_medicamentos.append('Unknown')

            medicamentos_html = self.get_data(lista_medicamentos)
            self.wfile.write(bytes(medicamentos_html, "utf8"))

        elif 'searchCompany' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            company = self.path.split('=')[1]

            lista_empresas = []
            conexion = http.client.HTTPSConnection(self.pagina_fda)
            conexion.request("GET", self.fda_json + "?limit=" + str(limit) + self.search_company + company)
            respuesta = conexion.getresponse()
            datos_raw = respuesta.read().decode('utf8')

            info_empresas = json.loads(datos_raw)['results']

            for elem in info_empresas:
                lista_empresas.append(elem['openfda']['manufacturer_name'][0])

            empresas_html = self.get_data(lista_empresas)
            self.wfile.write(bytes(empresas_html, "utf8"))

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_empresas = []
            info_empresas = self.get_resultados(limit)

            for elem in info_empresas:
                if ('manufacturer_name' in elem['openfda']):
                    lista_empresas.append(elem['openfda']['manufacturer_name'][0])
                else:
                    lista_empresas.append('Unknown')

            empresas_html = self.get_data(lista_empresas)
            self.wfile.write(bytes(empresas_html, "utf8"))


        #EXTENSIONES
        elif 'listWarnings' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_warnings = []
            info_warnings = self.get_resultados(limit)
            for elem in info_warnings:
                if ('warnings' in elem):
                    lista_warnings.append(elem['warnings'][0])
                else:
                    lista_warnings.append('Unknown')

            warnings_html = self.get_data(lista_warnings)
            self.wfile.write(bytes(warnings_html, "utf8"))

        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        elif 'redirect' in self.path:
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("ERROR 404. Se desconoce el siguiente recurso solicitado: '{}'.".format(self.path).encode())

        return


#SERVIDOR
Handler = testHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("El servidor ha sido interrumpido por el usuario.")

httpd.server_close()
print("El servidor está parado.")
