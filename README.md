# ISOLATION
**ISOLATION** es un script diseñado para facilitar la configuración de servicios de red, tales como Netplan, servidores DHCP y VLANs.

## Funcionalidades
- Configuración de Netplan para la gestión de interfaces de red.
- Configuración y administración de servidores DHCP.
- Gestión y configuración de VLANs.

## Requisitos
- Python 3.13 o superior

## Configuración
En el fichero `config/dhcp.txt` se debe escribir el código inicial para la configuración de servicios DHCP

## Uso
Al ejecutar el script, este verificará el funcionamiento de determinados paquetes. (no es necesario instalarlos todos.
Dentro se debe escoger una opción)

Al ejecutar el script, este verificará el funcionamiento de ciertos paquetes necesarios (no es obligatorio tener todos instalados).

Luego, se presentará un menú donde podrás seleccionar la opción deseada para configurar el servicio correspondiente.
Nota: en los casos de aplicar la configuración se creará siempre un backup del archivo anterior.

## Licencia
Este proyecto está licenciado bajo la **Licencia Pública General GNU versión 3 (GPLv3)**.   
Para más información, consulta el archivo `LICENSE` incluido en este repositorio.