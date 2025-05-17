-- Telefones pode ser usado por clientes ou colaboradores
CREATE TABLE Telefones (
    id_telefone INT AUTO_INCREMENT PRIMARY KEY,
    telefone VARCHAR(20)
);

CREATE TABLE Enderecos (
    id_endereco INT AUTO_INCREMENT PRIMARY KEY,
    endereco VARCHAR(255)
);

CREATE TABLE Colaboradores (
    cpf BIGINT PRIMARY KEY UNIQUE, -- CPF geralmente é um número grande
    nome VARCHAR(100),
    dataAd DATE,
    nivelSistem INT,
    funcao VARCHAR(100),
    fk_telefone INT,
    fk_endereco INT,
    FOREIGN KEY (fk_telefone) REFERENCES Telefones(id_telefone),
    FOREIGN KEY (fk_endereco) REFERENCES Enderecos(id_endereco)
);

CREATE TABLE Clientes (
    cpf BIGINT PRIMARY KEY UNIQUE,
    nome VARCHAR(100),
    fk_telefone INT,
    FOREIGN KEY (fk_telefone) REFERENCES Telefones(id_telefone)
);

-- Pratos possuem um preço e vários ingredientes
CREATE TABLE Precos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    preco DOUBLE
);

CREATE TABLE Ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE Pratos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    fk_preco INT,
    FOREIGN KEY (fk_preco) REFERENCES Precos(id)
);

-- Relação muitos-para-muitos: Pratos e Ingredientes
CREATE TABLE Prato_Ingredientes (
    prato_id INT,
    ingrediente_id INT,
    PRIMARY KEY (prato_id, ingrediente_id),
    FOREIGN KEY (prato_id) REFERENCES Pratos(id),
    FOREIGN KEY (ingrediente_id) REFERENCES Ingredientes(id)
);

-- Pedidos podem ter vários pratos
CREATE TABLE Pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    numMesa INT,
    fk_colaborador BIGINT,
    FOREIGN KEY (fk_colaborador) REFERENCES Colaboradores(cpf)
);

-- Relação muitos-para-muitos: Pedidos e Pratos
CREATE TABLE Pedido_Pratos (
    pedido_id INT,
    prato_id INT,
    PRIMARY KEY (pedido_id, prato_id),
    FOREIGN KEY (pedido_id) REFERENCES Pedidos(id_pedido),
    FOREIGN KEY (prato_id) REFERENCES Pratos(id)
);

-- Cardápio tem vários pratos
CREATE TABLE Cardapio (
    id INT AUTO_INCREMENT PRIMARY KEY
);

-- Relação muitos-para-muitos: Cardápio e Pratos
CREATE TABLE Cardapio_Pratos (
    cardapio_id INT,
    prato_id INT,
    PRIMARY KEY (cardapio_id, prato_id),
    FOREIGN KEY (cardapio_id) REFERENCES Cardapio(id),
    FOREIGN KEY (prato_id) REFERENCES Pratos(id)
);

-- login do colaborador no sistema
create table Login(
id_usuario INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
cpf BIGINT NOT NULL,
senha INT NOT NULL,
FOREIGN KEY (cpf) REFERENCES colaboradores(cpf)
);
