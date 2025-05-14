from enum import Enum


class NivelSistema(Enum):
    """Níveis de acesso no sistema da cafeteria"""

    ADMINISTRADOR = 1  # Acesso total ao sistema
    GERENTE = 2  # Gerencia a cafeteria como um todo
    BARISTA_MASTER = 3  # Barista experiente com funções de supervisão
    BARISTA = 4  # Funcionário prepara bebidas e atende clientes
    ATENDENTE = 5  # Atendimento no balcão/caixa
    AUXILIAR = 6  # Auxiliar de limpeza e apoio geral

    @classmethod
    def get_choices(cls):
        """Retorna opções para formulários/combobox"""
        return [(member.value, member.name.replace("_", " ").title()) for member in cls]


class Cargos(Enum):
    """Cargos funcionais da cafeteria"""

    DONO = "Dono/Proprietário"
    GERENTE = "Gerente Geral"
    SUPERVISOR_TURNO = "Supervisor de Turno"
    BARISTA_CHEFE = "Barista Chefe"
    BARISTA = "Barista"
    CAIXA = "Atendente de Caixa"
    GARCOM = "Garçom/Mesas"
    AUXILIAR_COZINHA = "Auxiliar de Cozinha"
    AUXILIAR_LIMPEZA = "Auxiliar de Limpeza"
    ESTAGIARIO = "Estagiário"
    ENTREGADOR = "Entregador/Delivery"

    @classmethod
    def get_choices(cls):
        """Retorna opções para formulários/combobox"""
        return [(member.name, member.value) for member in cls]
