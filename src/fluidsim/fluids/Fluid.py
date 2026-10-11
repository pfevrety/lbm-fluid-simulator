from abc import ABC

class Fluid(ABC):
    def __init__(self):
        self.type = None
        self.rho = None
        self.viscosity = None
    
    
    def get_fluid_info(self):
        print(f'Nom du fluide : {self.type}')
        print(f'Masse volumique du fluide : {self.rho}')
        print(f'Viscosité du fluide : {self.viscosity}')


class Air(Fluid):
    def __init__(self):
        super().__init__()
        self.type = "Air"
        self.rho = 1.2
        self.viscosity = 0.000018

class Water(Fluid):
    def __init__(self):
        super().__init__()
        self.type = "Water"
        self.rho = 1000
        self.viscosity = 1e-3
        
class Olive_oil(Fluid):
    def __init__(self):
        super().__init__()
        self.type = "Huile d'olive"
        self.rho = 920
        self.viscosity = 0.084	

class Honey(Fluid):
    def __init__(self):
        super().__init__()
        self.type = "Water"
        self.rho = 1420
        self.viscosity = 10

class CustomFluid(Fluid):
    def __init__(self, name, rho, viscosity):
        super().__init__()
        self.name=name
        self.rho=rho
        self.viscosity=viscosity