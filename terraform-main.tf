provider "aws" {
  region = "eu-west-1" # You can change this to another region if needed (e.g., "us-east-1")
}

# Security group for the backend server
resource "aws_security_group" "backend_sg" {
  name        = "backend-sg"
  description = "Allow SSH, Flask API, and MongoDB access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # For better security, consider restricting to your own IP
  }

  ingress {
    from_port   = 5000 # Port used by the Flask API
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # You can lock this down to a specific IP or range
  }

  ingress {
    from_port        = 27017 # MongoDB port – allow only from the game server
    to_port          = 27017
    protocol         = "tcp"
    security_groups  = [aws_security_group.game_sg.id] # Allow traffic only from the game server SG
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Allow all outbound traffic
  }
}

# Security group for the game server
resource "aws_security_group" "game_sg" {
  name        = "game-sg"
  description = "Allow SSH and game traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # You may want to limit SSH access by IP
  }

  ingress {
    from_port   = 80 # Update if your game runs on a different port
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Full outbound access
  }
}

# Backend server instance
resource "aws_instance" "backend_server" {
  ami                    = "ami-053b0a9d18080214a" # Ubuntu 22.04 LTS (eu-west-1)
  instance_type          = "t2.micro"
  key_name               = "my-aws-key" # Replace with your actual key pair name
  vpc_security_group_ids = [aws_security_group.backend_sg.id]

  tags = {
    Name = "PokeAPI-Backend-Server"
  }
}

# Game server instance
resource "aws_instance" "game_server" {
  ami                    = "ami-053b0a9d18080214a" # Ubuntu 22.04 LTS (eu-west-1)
  instance_type          = "t2.micro"
  key_name               = "my-aws-key" # Replace with your real AWS key pair name
  vpc_security_group_ids = [aws_security_group.game_sg.id]

  tags = {
    Name = "PokeAPI-Game-Server"
  }
}

# Output the public IP addresses of both instances
output "backend_public_ip" {
  value = aws_instance.backend_server.public_ip
}

output "game_public_ip" {
  value = aws_instance.game_server.public_ip
}
