import json
from fastapi import params
import ovirtsdk4 as sdk 
import ovirtsdk4.types as types
from ovirtsdk4 import types  
from pydantic import BaseModel
import time

with open('login.json') as config_file:
    config = json.load(config_file)

class OvirtConnectionManager:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __enter__(self):
        self.connection = sdk.Connection(
            url=self.config['url'],
            username=self.config['username'],
            password=self.config['password'],
            ca_file=self.config['ca_file']
        )
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

def criar_vm(name: str, memory: int, cpu: int, cluster: str, template: str):

    with OvirtConnectionManager(config) as conexao:
        servico_vms = conexao.system_service().vms_service()

        memoria_bytes = memory * 1024 * 1024

        vm = servico_vms.add(
            types.Vm(
                name = name,
                memory = memoria_bytes,
                cpu=types.Cpu(
                    topology=types.CpuTopology(
                        cores=cpu,  
                        sockets=1,  
                        threads=1  
                    )
                ),
                cluster = types.Cluster(
                    name = cluster
                ),
                template = types.Template(
                    name = template
                ),
                os=types.OperatingSystem(
                    boot=types.Boot(
                        devices=[types.BootDevice.HD]
                    )
                ),
            )
        )

        print(f'VM {vm.name} criada')
        return{"message":f"VM {vm.name} Criada", "status":"OK"}

def start(name: str):

    with OvirtConnectionManager(config) as conexao:
        servico_vms = conexao.system_service().vms_service()

        vm = servico_vms.list(search=name)[0]
        servico_vm = servico_vms.vm_service(vm.id)
        servico_vm.start()

        while True:
            time.sleep(5)
            vm = servico_vm.get()
            if vm.status == types.VmStatus.UP:
                break

        print(f'VM {vm.name} ligada')
        return {"message":f"VM {vm.name} Ligada", "status":"OK"}
        
def nic(name: str, vnic_profile: str):

    with OvirtConnectionManager(config) as conexao:
        servico_vms = conexao.system_service().vms_service()

        vm = servico_vms.list(search=name)[0]

        servico_vm = servico_vms.vm_service(vm.id)
        servico_nics = servico_vm.nics_service()

        vnic_profiles_service = conexao.system_service().vnic_profiles_service()
        vnic_profile = next(
            (profile for profile in vnic_profiles_service.list() if profile.name == vnic_profile),
            None
        )

        if vnic_profile:
            existing_nics = servico_nics.list()
            existing_vnic_ids = {nic.vnic_profile.id for nic in existing_nics}

            if vnic_profile.id in existing_vnic_ids:
                print(f"A interface de rede '{vnic_profile.name}' já foi adicionada à VM '{vm.name}'.")
                return {"message": f"A interface de rede '{vnic_profile.name}' já está configurada para a VM {vm.name}.", "status": "OK"}
            else:
                nic = servico_nics.add(
                    types.Nic(
                        name="nic1",
                        vnic_profile=types.VnicProfile(id=vnic_profile.id)
                    )
                )
                print(f'Interface de rede {nic.name} adicionada à VM {vm.name}.')
                return {"message": f"Interface de rede {nic.name} adicionada à VM {vm.name}.", "status": "OK"}
        else:
            print(f"Perfil de rede '{vnic_profile}' não encontrado.")
            return {"message": f"Perfil de rede '{name}' não encontrado.", "status": "Error"}
        
def ip(name: str):

    with OvirtConnectionManager(config) as conexao:
    
        servico_vms = conexao.system_service().vms_service()

        vm = servico_vms.list(search=name)[0]

        vm_service = servico_vms.vm_service(vm.id)

        devices_service = vm_service.reported_devices_service()
        devices = devices_service.list()

        for device in devices:
            if device.name == 'ens3':  
                if device.ips:
                    for ip in device.ips:
                        print(f"Interface: {device.name}, IP: {ip.address}")
                        return {"ip":f"{ip.address}", "status":"OK"}

                else:
                    print(f"Interface: {device.name} sem IP atribuído.")
                    return {"ip":f"Sem IP atribuído.", "status":"OK"}
            else:
                print(f"{vm.name} não é {device.name}.")
                return {"message":f"{vm.name} não é {device.name}.", "status":"ERRO"}

def info(name: str):

    with OvirtConnectionManager(config) as conexao:
    
        servico_vms = conexao.system_service().vms_service()
        vm = servico_vms.list(search = name)[0]
        vm_service = servico_vms.vm_service(vm.id)
        vms = servico_vms.list(search=name)

        ip = None

        if vm:
            print(f"\nInformações da VM: {vm.name}")
            print(f"Nome: {vm.name}")

            if vms:
                vm = vms[0]
                print(f"ID da VM: {vm.id}")
            else:
                print(f"VM '{vm.name}' não encontrada.")

            if vm.template:
                print(f'Template: {vm.template.name}')
            else:
                print(f'Não está usando um template.')

            print(f"Memória: {vm.memory / (1024 * 1024)} MB")  
            print(f"Estado: {vm.status}")

            cluster = conexao.system_service().clusters_service().cluster_service(vm.cluster.id).get()
            print(f"Cluster: {cluster.name}")

            if vm.host:
                host = conexao.system_service().hosts_service().host_service(vm.host.id).get()
                print(f"Host: {host.name}")
            else:
                print("Host não disponível para esta VM.")

            cpu_cores = vm.cpu.topology.cores
            cpu_sockets = vm.cpu.topology.sockets
            cpu_threads = vm.cpu.topology.threads
            total_cpus = cpu_cores * cpu_sockets * cpu_threads
            print(f'CPUs: {total_cpus}')

            creation_time = vm.creation_time
            print(f"A VM '{vm.name}' foi criada em: {creation_time}")

            devices_service = vm_service.reported_devices_service()
            devices = devices_service.list()

            for device in devices:
                if device.name == 'ens3':  
                    if device.ips:
                        ip = device.ips[0].address  
                        print(f"Interface: {device.name}, IP: {ip}")
                        break  
                    else:
                        print(f"Interface: {device.name} sem IP atribuído.")

            if ip is None:
                ip = "Sem IP atribuído"  

            return {"message":f"Informações da VM: {vm.name}", 
                    "nome": f'{vm.name}',
                    "id": f'{vm.id}',
                    "criação": f'{creation_time}',
                    "template": f'{vm.template.name}',
                    "memoria": f'{vm.memory / (1024 * 1024)}',
                    "estado": f'{vm.status}', 
                    "cluster": f'{cluster.name}',
                    "host": f'{host.name}',
                    "cpu": f'{total_cpus}',
                    "ip": f'{ip}',
                    "status":"OK"}
        else:
            print(f"VM '{vm.name}' não encontrada.")
            return {"message":f"VM '{vm.name}' não encontrada", "status":"ERRO"}

def id(name: str):

    with OvirtConnectionManager(config) as conexao:
    
        servico_vms = conexao.system_service().vms_service()
        vms = servico_vms.list(search=name)

        if vms:
            vm = vms[0]
            print(f"ID da VM: {vm.id}")
            print(f"Nome da VM: {vm.name}")
            return {"id":f"{vm.id}.", "status":"OK"}
        else:
            print(f"VM '{vm.name}' não encontrada.")
            return {"message":f"{vm.name} não encontrada.", "status":"ERRO"}
        
def deletar_vm(name: str):

    with OvirtConnectionManager(config) as conexao:

        servico_vms = conexao.system_service().vms_service()
        vms = servico_vms.list(search=name)
        vm = vms[0]

        if not vms:
            print(f'Erro: VM com nome "{vm.name}" não encontrada.')
        else:
            vm_id = vms[0].id
            servico_vm = servico_vms.vm_service(vm.id)
            servico_vm.stop()

        servico_vm.remove()
        print(f'VM {vm.name} deletada com sucesso.')
        return{"message": "VM deletada com sucesso." , "status": "OK"}

def editar_vm(name: str , ram: int , cpu_cores: int , new_name: str , nic: str):

    with OvirtConnectionManager(config) as conexao:

        servico_vms = conexao.system_service().vms_service()
        vms = servico_vms.list(search=name)

        if not vms:
            return {"message": f"Erro: VM com nome '{name}' não encontrada.", "status": "ERROR"}

        vm = vms[0]
        servico_vm = servico_vms.vm_service(vm.id)

        if ram is not None:
            memoria_bytes = ram * 1024 * 1024 * 1024  
            vm_update = types.Vm(memory=memoria_bytes)
            servico_vm.update(vm=vm_update)
            print(f"Memória RAM editada com sucesso")

        if cpu_cores is not None:
            cpu = types.Cpu(topology=types.CpuTopology(cores=cpu_cores, sockets=1, threads=1))
            vm_update = types.Vm(cpu=cpu)
            servico_vm.update(vm=vm_update)
            print(f"CPUs editada com sucesso")

        if new_name is not None:
            vm_update = types.Vm(name=new_name)
            servico_vm.update(vm=vm_update)
            print(f"Nome editado com sucesso")

        if nic is not None:
            interfaces_service = servico_vm.nics_service()
            nics = interfaces_service.list()
            if nics:
                nic_service = interfaces_service.nic_service(nics[0].id)
                nic_update = types.Nic(name=nic)
                nic_service.update(nic=nic_update) 
                print(f"Rede editada com sucesso")

        print(f'VM {vm.name} editada com sucesso.')
        return {"message": f"VM {vm.name} editada com sucesso", "status": "OK"}

def listar_vms(tipo: str, criterio: str):

    with OvirtConnectionManager(config) as conexao:
        servico_vms = conexao.system_service().vms_service()
        vms = servico_vms.list()

        if not vms:
            return {"message": "Nenhuma VM encontrada no ambiente.", "status": "ERROR"}

        vms_filtradas = []

        if tipo.lower() == "cluster":
            cluster_service = conexao.system_service().clusters_service()
            clusters = {cluster.id: cluster.name for cluster in cluster_service.list()}

            vms_filtradas = [
                vm for vm in vms
                if vm.cluster and clusters.get(vm.cluster.id, "").lower().startswith(criterio.lower())
            ]

        elif tipo.lower() == "rede":
            for vm in vms:
                interfaces_service = servico_vms.vm_service(vm.id).nics_service()
                nics = interfaces_service.list()
                if any(nic.name and criterio.lower() in nic.name.lower() for nic in nics):
                    vms_filtradas.append(vm)

        elif tipo.lower() == "usuario":
            for vm in vms:
                if hasattr(vm, 'created_by') and vm.created_by and criterio.lower() == vm.created_by.lower():
                    vms_filtradas.append(vm)

        else:
            return {"message": f"Tipo '{tipo}' não suportado.", "status": "ERROR"}

        if not vms_filtradas:
            return {
                "message": f"Nenhuma VM encontrada para o tipo '{tipo}' com o critério '{criterio}'.",
                "status": "ERROR"
            }

        resultado = [
            {
                "name": vm.name,
                "id": vm.id,
                "comment": getattr(vm, "comment", "N/A"),
                "status": "up" if vm.status == types.VmStatus.UP else "down",  
            }
            for vm in vms_filtradas
        ]

        return {"message": "VMs encontradas com sucesso.", "status": "OK", "data": resultado}
    
