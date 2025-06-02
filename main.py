import json
import time
import ovirtsdk4 as sdk 
import ovirtsdk4.types as types
import psycopg2
import fastapi
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from scripts import *
from typing import Optional

app = FastAPI()

class Cluster(BaseModel): 
    name: str
class Template(BaseModel):
    name: str
class Criacao(BaseModel):
    name: str
    memory: int
    cpu: int
    cluster: Cluster
    template: Template
class Start(BaseModel):
    name: str 
class NetWork(BaseModel):
    vnic_profile : str
class NIC(BaseModel):
    name: str
    network: NetWork 
class IP(BaseModel):
    name: str 
class Info(BaseModel):
    name: str 
class ID(BaseModel):
    name: str 
class Deletar(BaseModel):
    name: str
class Editar_VM(BaseModel):
    name: str 
    ram: Optional[int] = None
    cpu_cores: Optional[int] = None
    new_name: Optional[str] = None
    nic: Optional[str] = None
class Listar(BaseModel):
    tipo: str
    criterio: str
    
@app.post("/criar_vm/")
async def criar(vm_data: Criacao):
    return criar_vm(
            name=vm_data.name,
            memory=vm_data.memory,
            cpu=vm_data.cpu,
            cluster=vm_data.cluster.name,
            template=vm_data.template.name
        ) 

@app.post("/start/")
async def iniciar(name: Start):
    return start(name.name) 

@app.post("/nic/")
async def add_nic(rede: NIC):
    return nic(rede.name, rede.network.vnic_profile) 

@app.post("/ip/")
async def identificar_ip(name: IP):
    return ip(name.name) 

@app.post("/info/")
async def informacoes(name: Info):
    return info(name.name) 

@app.post("/id/")
async def id_vm(name: ID):
    return id(name.name) 

@app.post("/deletar_vm/")
async def excluir(name: Deletar):
    return deletar_vm(name.name)

@app.post("/editar_vm/")
async def editar(vm_data: Editar_VM):
    return editar_vm(
            name=vm_data.name,
            ram=vm_data.ram,
            cpu_cores=vm_data.cpu_cores,
            new_name=vm_data.new_name,
            nic=vm_data.nic,
        )

@app.post("/listar_vms/")
async def listar(vm_data: Listar):
    return listar_vms(
        tipo=vm_data.tipo,
        criterio=vm_data.criterio
    )
