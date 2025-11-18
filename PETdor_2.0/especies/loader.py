# PetDor/especies/loader.py
from .index import Especie

def listar_especies():
    return [e.value for e in Especie]
