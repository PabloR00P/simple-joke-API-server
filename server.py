import http.server
import socketserver
import requests
import json
import asyncio

PORT = 8000

# Aquí defino una subclase de SimpleHTTPRequestHandler para manejar las solicitudes
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/jokes':
            # Se obtiene una lista de chistes únicos
            jokes = self.get_unique_jokes(25)
            
            # Se validan los chistes obtenidos *primera validación*
            validated_jokes = self.validate_jokes(jokes)
            
            # Se vaidan los chistes nuevamente * segunda validación *
            double_validated_jokes = self.validate_jokes(validated_jokes)
            
            # Se envia la respuesta con los chistes validados dos veces
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(double_validated_jokes).encode())
        else:
            super().do_GET()

    # get_unique_jokes obtiene una lista de chistes únicos
    def get_unique_jokes(self, num_jokes):
        loop = asyncio.get_event_loop()
        tasks = [self.get_random_joke() for _ in range(num_jokes)]  # Crear tareas para obtener chistes aleatorios
        jokes = loop.run_until_complete(asyncio.gather(*tasks))  # Ejecutar las tareas y obtener los resultados
        return jokes
    
    # get_random_joke es el metodo asíncrono para obtener un chiste aleatorio
    async def get_random_joke(self):
        response = await asyncio.to_thread(requests.get, 'https://api.chucknorris.io/jokes/random')  # Hacemos una solicitud asíncrona a la API
        joke = response.json()  # obtenemos el chiste de la respuesta en formato JSON
        return joke['value']  # devolvemos el valor del chiste
    
    # validate_jokes es el metodo para validar los chistes
    def validate_jokes(self, jokes):
        validated_jokes = []
        for joke in jokes:
            while joke in validated_jokes:
                joke = self.get_random_joke()
            validated_jokes.append(joke)
        return validated_jokes

# Creamos de un servidor TCP que escucha en el puerto especificado
with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
    print("Servidor en el puerto:", PORT)
    httpd.serve_forever()  # Iniciar el servidor y mantenerlo en ejecución