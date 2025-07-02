import argparse         # Importa o módulo para análise de argumentos de linha de comando
import subprocess       # Importa o módulo para executar comandos do sistema operacional
import re               # Importa o módulo para trabalhar com expressões regulares
import sys              # Importa o módulo para acessar funcionalidades específicas do sistema
import os

def run(cmd):
    # Executa um comando no shell e retorna apenas a saída padrão (stdout) em inglês e UTF-8

    env = os.environ.copy()

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    return result.stdout

def remover_ips(interface):
    # Remove todos os IPs extras configurados na interface de rede especificada
    print(f"Removendo IPs extras da interface {interface}...")
    saida = run(f'netsh interface ipv4 show addresses name="{interface}"')
    if "não encontrado" in saida:
        print(f"A interface {interface} não foi encontrada.")
        return
    # Busca todos os IPs configurados na interface, aceitando tanto português quanto inglês
    ips = re.findall(r'(?:Endere[cç]o IP|IP Address)[^:]*:\s*([\d\.]+)', saida)
    print(f"IPs encontrados na interface {interface}: {ips}")
    if not ips:
        print("Nenhum IP extra encontrado para remover.")
        return
    for ip in ips:
        # Ignora IPs padrão e reservados
        if ip in ["0.0.0.0", "127.0.0.1", "255.255.255.255"] or ip.startswith("169.254"):
            continue
        print(f"Removendo IP {ip}")
        # Remove o IP encontrado da interface e exibe a saída do comando para debug
        resultado_remocao = run(f'netsh interface ipv4 delete address name="{interface}" addr={ip}')
        #print(f"Saída do comando de remoção do IP {ip}:\n{resultado_remocao}")

def set_dhcp(interface):
    # Restaura a interface para obter IP e DNS automaticamente via DHCP
    print(f"Reestabelecendo interface {interface} para DHCP...")
    run(f'netsh int ipv4 set address name="{interface}" source=dhcp')
    run(f'netsh int ipv4 set dnsservers name="{interface}" source=dhcp')

def add_ip(interface, ip, mask):
    # Ativa a coexistência de DHCP e IP estático na interface
    print(f"Ativando coexistência DHCP+IP estático na interface {interface}")
    run(f'netsh interface ipv4 set interface name="{interface}" dhcpstaticipcoexistence=enabled')
    # Adiciona um IP extra à interface de rede
    print(f"Adicionando IP extra {ip}/{mask} na interface {interface}")
    run(f'netsh interface ipv4 add address name="{interface}" addr={ip} mask={mask}')

def main():
    # Função principal: analisa argumentos e executa a ação apropriada
    parser = argparse.ArgumentParser(
        description="Adiciona ou remove IP extra em uma interface de rede.",
        epilog=""":
Exemplos de uso:
  Adicionar IP extra:
    py.exe add_ip.py -i "Wi-Fi" -ip 192.168.100.99 -nm 255.255.255.0
  Remover IPs extras e restaurar DHCP:
    py.exe add_ip.py -c -i "Wi-Fi"
  Ver ajuda:
    py.exe add_ip.py -h
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-c", "--clean", action="store_true", dest="clean", help="Reestabelece a interface para DHCP e remove IPs extras")
    parser.add_argument("-i", "--iface", dest="interface", default="Wi-Fi", help="Nome da interface de rede")
    parser.add_argument("-ip", "--ip", dest="ip", default="192.168.100.99", help="IP extra a ser adicionado")
    parser.add_argument("-nm", "--nm", dest="mask", default="255.255.255.0", help="Máscara de rede do IP extra")
    args = parser.parse_args()

    if args.clean:
        # Se o argumento de limpeza for passado, remove IPs extras e restaura DHCP
        remover_ips(args.interface)
        set_dhcp(args.interface)
    else:
        # Caso contrário, adiciona o IP extra informado
        add_ip(args.interface, args.ip, args.mask)

if __name__ == "__main__":
    # Garante que o script só rode no Windows
    if not sys.platform.startswith("win"):
        print("Este script só funciona no Windows.")
        sys.exit(1)
    main()