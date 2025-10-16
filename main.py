import shutil, os, subprocess, time
from modules.colores import Fore
from modules.netplancfg import obtenerInterfaces, configFicheroIN, aplicarNetplan
from modules.vlans import configNotPerma, configPerma
from modules.dhcp import aplicarDHCP, reservaIN, subnetIN, poolIN, claseIN, formatDHCP

def comando_disponible(comando):
	return shutil.which(comando) is not None

menu = """
====================================
MENÚ  PRINCIPAL

1.- Ayuda con Netplan
2.- Instalación de VLAN
3.- Configuración de DHCP (Servidor)
====================================
"""

menuExtra = """
3.- Sniffer de red (tcpdump)
4.- Análisis de puertos (nmap)
5.- Captura de tráfico (Wireshark)
6.- Conexión remota (netcat)
7.- Salir
==========================
"""

banner = """
╔═╗      ╔═╗      ╔═╗      ╔═╗      
║ ╠═╦═╗  ║ ╠═╦═╗  ║ ╠═╦═╗  ║ ╠═╦═╗
╚═╝      ╚═╝      ╚═╝      ╚═╝      
        I S O L A T I O N
         B Y  E S A N D I
             FOCUS
╔═╗      ╔═╗      ╔═╗      ╔═╗      
║ ╠═╦═╗  ║ ╠═╦═╗  ║ ╠═╦═╗  ║ ╠═╦═╗  
╚═╝      ╚═╝      ╚═╝      ╚═╝      
"""


def check():
	lista = []
	for cmd in ['tcpdump', 'ifconfig', 'wireshark', "netcat", "dhclient", "nmap", "vlan"]:
		if comando_disponible(cmd):
			print(f"Comando '{cmd}' está disponible")
		else:
			print(f"Comando '{cmd}' NO está disponible")
			if cmd == "ifconfig":
				cmd = "net-tools"
			lista.append(cmd)
	if len(lista) > 0:
		print (Fore.ROJO + "Faltan comandos necesarios, instala los paquetes correspondientes." + Fore.RESET)
		y = input("¿Quieres instalarlos? (S/N) > ")
		if y == "S":
			subprocess.run(["sudo", "apt", "update"], check=True)
			subprocess.run(["sudo", "apt", "install"] + lista)
			print(Fore.VERDE+"Instalación completada, reinicia el script."+Fore.VERDE)
		else:
			print("Se ignorará la instalación, algunas funciones pueden no funcionar...")

if __name__ == '__main__':
	print ("I S O L A T I O N\n\n")
	if not os.geteuid() == 0:
		print(Fore.AMARILLO+"¡Script abierto sin permisos de SUDO! Algunas funciones pueden no funcionar."+Fore.RESET)
		time.sleep(2)
	print("Verificando paquetes...")

	check()
	print (banner)
	while True:
		print (menu)
		x = input("root@isolation >>> ")
		if x == "1":
			print ("Buscando interfaces de red...")
			interfaces = obtenerInterfaces()
			if "lo" in interfaces:
				interfaces.remove("lo")
			print ("Borrando datos antiguos del fichero de Netplan...")
			file = open('output/file.yaml', 'w')
			file.write("network:\n")
			file.write("  version: 2\n")
			file.write("  ethernets:\n")
			file.close()
			print ("============================")
			print ("1.- Configuración Netplan")
			print ("2.- Salida rápida a Internet")
			print ("============================")
			x = input("Selección > ")
			if x == "1":
				configFicheroIN("output/file.yaml", interfaces)
			elif x == "2":
				dg = input("Introduce la dirección del Default Gateway > ")
				print ("Usando el DNS de Google (8.8.8.8)...")
				with open("output/file.yaml", "a") as f:
					for interfaz in interfaces:
						f.write(f"    {interfaz}:\n")
						f.write(f"      dhcp4: yes\n")
						f.write("      routes:\n")
						f.write("        - to: default\n")
						f.write(f"          via: {dg}\n")
						f.write("      nameservers:\n")
						f.write(f"        addresses: [8.8.8.8]\n")
					f.close()
			print ("Configuración guardada en output/file.yaml")
			print ("Recuerda que puedes apagar interfaces con 'sudo ifconfig <interfaz> down'")
			print ("Usa 'sudo ifconfig <interfaz> up' para volver a activarlas")
			print ("'ip link show' para ver las interfaces.")
			x = input("¿Aplicar configuración? (S/N) > ")
			if x == "S":
				aplicarNetplan()
		elif x == "2":
			print("===============================================================")
			print("1.- Configuración temporal (no persiste tras reinicio)")
			print("2.- Configuración permanente (requiere reinicio para aplicar)")
			print("===============================================================")
			y = input("Selección > ")
			if y == "1":
				configNotPerma(obtenerInterfaces())
			elif y == "2":
				configPerma()
		elif x == "3":
			while True:
				print("\n======================================")
				print ("0.- Vaciar fichero de configuración")
				print ("1.- Configurar Subnet")
				print ("2.- Configurar Reserva")
				print ("3.- Definir clases")
				print ("4.- Pools/Directivas (Avanzado)")
				print ("5.- Aplicar configuración")
				print("======================================")
				y = input("Selección > ")
				if y == "0":
					formatDHCP()
					print ("Borrado")
				elif y == "1":
					print ("Puedes prohibir la navegación si el D.G. es null o 0.0.0.0")
					subnetIN()
					print ("Subnet añadida a output/dhcpd.conf")
				elif y == "2":
					reservaIN()
					print ("Reserva añadida a output/dhcpd.conf")
				elif y == "3":
					claseIN()
					print ("Clases añadida a output/dhcpd.conf")
				elif y == "4":
					poolIN()
					print ("Pools añadidos a output/dhcpd.conf")
				elif y == "5":
					aplicarDHCP()
				elif y == "q":
					break

def menu_extra(): # Nota esto está en mantenimiento, no se aconseja su uso
	while True:
		print (menuExtra)
		x = input("root@isolation >>> ")
		if x == "1":
			pass
		elif x == "2":
			eth0 = input("Interfaz WAN > ")
			eth1 = input("Interfaz interna > ")
			print ("Redirigiendo todo el tráfico a la interfaz WAN...")
			os.system(f"sudo iptables -t nat -A POSTROUTING -o {eth0} -j MASQUERADE")
			os.system(f"sudo iptables -A FORWARD -i {eth0} -o {eth1} -m state --state RELATED,ESTABLISHED -j ACCEPT")
			os.system(f"sudo iptables -A FORWARD -i {eth1} -o {eth0} -j ACCEPT")
			print ("Hecho. Usa 'sudo iptables -L' para ver las reglas.")
			print ("Usa 'sudo iptables -F' para eliminar las reglas y restaurar la configuración.")
		elif x == "3":
			if comando_disponible("tcpdump"):
				print ("Listando interfaces de red...")
				os.system("sudo tcpdump -D")
				iface = input("Selecciona la interfaz a usar > ")
				print (f"Iniciando sniffer en {iface}, pulsa Ctrl+C para detener...")
				try:
					os.system(f"sudo tcpdump -i {iface} -vv")
				except KeyboardInterrupt:
					print ("Sniffer detenido.")
			else:
				print (Fore.ROJO + "tcpdump no está instalado." + Fore.RESET)
		elif x == "4":
			if comando_disponible("nmap"):
				target = input("Introduce la IP o rango a escanear")
				print (f"Escaneando {target}...")
				os.system(f"sudo nmap -sS -O {target}")
			else:
				print (Fore.ROJO + "nmap no está instalado." + Fore.RESET)
		elif x == "5":
			if comando_disponible("wireshark"):
				print ("Listando interfaces de red...")
				os.system("sudo wireshark -D")
				iface = input("Selecciona la interfaz a usar > ")
				print (f"Iniciando Wireshark en {iface}...")
				try:
					os.system(f"sudo wireshark -i {iface}")
				except KeyboardInterrupt:
					print ("Wireshark detenido.")
			else:
				print (Fore.ROJO + "Wireshark no está instalado." + Fore.RESET)
		elif x == "6":
			if comando_disponible("netcat"):
				print ("Iniciando netcat en modo escucha en el puerto 4444...")
				print ("En otro equipo, usa 'nc <IP> 4444' para conectarte.")
				try:
					os.system("sudo nc -lvp 4444")
				except KeyboardInterrupt:
					print ("Netcat detenido.")
			else:
				print (Fore.ROJO + "netcat no está instalado." + Fore.RESET)
		elif x == "7":
			print ("Saliendo...")
			break