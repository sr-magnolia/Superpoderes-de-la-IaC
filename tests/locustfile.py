from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Simula un tiempo de espera entre 1 y 5 segundos entre peticiones
    wait_time = between(1, 5)

    @task
    def access_alb(self):
        # El endpoint que procesa la carga de CPU
        self.client.get("/")