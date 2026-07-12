resource "docker_network" "lab11_net" {
  name = "lab11_net"
}

resource "docker_image" "postgres" {
  name = "postgres:16-alpine"
}

resource "docker_image" "flask_app" {
  name = "lab11_flask_app:latest"

  build {
    context    = "${path.module}/backend"
    dockerfile = "Dockerfile"
  }
}

resource "docker_image" "nginx_lb" {
  name = "lab11_nginx_lb:latest"

  build {
    context    = "${path.module}/nginx"
    dockerfile = "Dockerfile"
  }
}

resource "docker_container" "postgres" {
  name  = "postgres"
  image = docker_image.postgres.image_id

  env = [
    "POSTGRES_DB=lab11_db",
    "POSTGRES_USER=lab11_user",
    "POSTGRES_PASSWORD=lab11_pass"
  ]

  networks_advanced {
    name = docker_network.lab11_net.name
  }
}

resource "docker_container" "flask1" {
  name       = "flask1"
  image      = docker_image.flask_app.image_id
  depends_on = [docker_container.postgres]

  env = [
    "DB_HOST=postgres",
    "DB_NAME=lab11_db",
    "DB_USER=lab11_user",
    "DB_PASSWORD=lab11_pass",
    "APP_NAME=Flask1"
  ]

  networks_advanced {
    name = docker_network.lab11_net.name
  }
}

resource "docker_container" "flask2" {
  name       = "flask2"
  image      = docker_image.flask_app.image_id
  depends_on = [docker_container.postgres]

  env = [
    "DB_HOST=postgres",
    "DB_NAME=lab11_db",
    "DB_USER=lab11_user",
    "DB_PASSWORD=lab11_pass",
    "APP_NAME=Flask2"
  ]

  networks_advanced {
    name = docker_network.lab11_net.name
  }
}

resource "docker_container" "nginx" {
  name       = "nginx_lb"
  image      = docker_image.nginx_lb.image_id
  depends_on = [docker_container.flask1, docker_container.flask2]

  ports {
    internal = 80
    external = 3000
  }

  networks_advanced {
    name = docker_network.lab11_net.name
  }
}
