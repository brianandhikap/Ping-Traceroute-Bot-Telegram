import logging
import subprocess
import requests
from shlex import quote
from aiogram.utils import markdown as md
from aiogram import Bot, Dispatcher, executor, types

from config import API_TOKEN, PROXY_URL, SHOW_PUBLIC_IP
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot)


def icmp_ping(ip):
        command = "ping {} -c 4".format(quote(ip))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = ''
        for line in process.stdout.read().decode().split('\n'):
                if not ('PING' in line or '---' in line):
                        result += line + '\n'
        return result.strip()

def tcp_ping(ip, port):
        command = "tcping {} -p {} -c 4".format(quote(ip), quote(port))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        return process.stdout.read().decode()

def run_besttrace(ip):
        command = "tracepath -p33434 -n -4 {}".format(quote(ip))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = ''
        for line in process.stdout.read().decode().split('\n'):
                if not ('*' in line or 'BestTrace' in line):
                        result += line + '\n'
        return result.strip()

def run_besttracedns(ip):
        command = "tracepath -p33434 -4 {}".format(quote(ip))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = ''
        for line in process.stdout.read().decode().split('\n'):
                if not ('*' in line or 'BestTrace' in line):
                        result += line + '\n'
        return result.strip()

def dns_lookup(host, type):
        command = "nslookup -type={} {}".format(quote(type), quote(host))
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = ''
        for line in process.stdout.read().decode().split('\n'):
                if not (';' in line):
                        result += line + '\n'
        return result.strip()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
        content = '''
Hallo!
Aku Ping Pong

Fitur:
/ping <ip> - Buat ngeping
/trace <ip> - Buat Traceroute
/tracedns <ip> - Buat Traceroute pakai DNS kak
/dns <ip> - Buat ngintip DNS
/gpon <> Buat ngintip yang punya
/pon <> Buat ngintip redaman
/olt <> Buat nyari yang LOS
/sn <sn> Buat nyari alamat dari SN kak

Mohon maaf kalau salah kak, jangan di bully.
'''
    #belum tau /tcp <ip> <port> - Buat TCP ping IP:PORT
        if SHOW_PUBLIC_IP:
                ip = requests.get("https://ipinfo.io/json").json()['ip']
                city = requests.get("https://ipinfo.io/json").json()['city']
                await message.reply(f"{content}\nIP ku {ip} ni, Di {city}".strip())
        else:
                await message.reply(content.strip())


@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
        ip = message.get_args()
        logging.info(f'{message.from_id}Bentar ping {ip}')
        if not ip:
                await message.reply("Ping Pong gak tau IP itu.")
                return
        waiting_message = await message.reply(f"Tunggu sebentar ya")
        try:
                result = icmp_ping(ip)
                if result:
                        await waiting_message.edit_text(f"Ini hasil nya ngeping ke {ip}:\n\n{result}\n\nUdah ya")
                else:
                        await waiting_message.edit_text(f"Ini hasil nya ngeping ke {ip}:\n\nNo result\n\nUdah ya")
        except Exception as e:
                await waiting_message.edit_text(f"Ini hasil nya ngeping ke {ip}:\n\n{e}\n\nUdah ya")


@dp.message_handler(commands=['tcp'])
async def tcp(message: types.Message):
        args = message.get_args().split()
        if len(args) < 2:
                await message.reply("Ping Pong gak tau IP sama portnya")
                return
        ip = args[0]
        port = args[1]
        logging.info(f'{message.from_id} TCP ping {ip} {port}')
        waiting_message = await message.reply(f"TCP pinging to {ip}:{port} ...")
        result = tcp_ping(ip, port)
        await waiting_message.edit_text(f"TCP ping to {ip}:{port}:\n {result}")


@dp.message_handler(commands=['trace'])
async def trace(message: types.Message):
        ip = message.get_args()
        logging.info(f'{message.from_id} trace {ip}')
        if not ip:
                await message.reply("Ping Pong gak tau IP itu.")
                return
        waiting_message = await message.reply(f"Tunggu sebentar ya")
        try:
                result = run_besttrace(ip)
                await waiting_message.edit_text(f"Trace ke {ip}:\n\nHOP - - - - - - HOST - - - - - - RTT (ms) \n----------------------------------------------------\n{result}\n\nUdah ya..")
        except Exception as e:
                await waiting_message.edit_text(f"Trace ke {ip}:\n\nHOP - - - - - - HOST - - - - - - RTT (ms) \n----------------------------------------------------\n{e}\n\nUdah ya..")

@dp.message_handler(commands=['tracedns'])
async def tracedns(message: types.Message):
        ip = message.get_args()
        logging.info(f'{message.from_id} trace {ip}')
        if not ip:
                await message.reply("Ping Pong gak tau IP itu.")
                return
        waiting_message = await message.reply(f"Tunggu sebentar ya")
        try:
                result = run_besttracedns(ip)
                await waiting_message.edit_text(f"Trace ke {ip}:\n\nHOP - - - - - - HOST - - - - - - RTT (ms) \n----------------------------------------------------\n{result}\n\nUdah ya..")
        except Exception as e:
                await waiting_message.edit_text(f"Trace ke {ip}:\n\nHOP - - - - - - HOST - - - - - - RTT (ms) \n----------------------------------------------------\n{e}\n\nUdah ya..")


@dp.message_handler(commands=['dns'])
async def dns(message: types.Message):
        args = message.get_args().split()
        if len(args) < 1:
                await message.reply("Ping Pong gak tau hostnamenya.")
                return
        host = args[0]
        type = 'A'
        if len(args) > 1:
                type = args[1]
        logging.info(f'{message.from_id} DNS lookup {host} as {type}')
        waiting_message = await message.reply(f"DNS lookup {host} as {type} ...")
        try:
                result = dns_lookup(host, type)
                await waiting_message.edit_text(f"DNS lookup {host} as {type}:\n\n{result}\n\nUdah ya..")
        except Exception as e:
                await waiting_message.edit_text(f"DNS lookup {host} as {type} failed:\n\n{e}\n\nUdah ya..")


if __name__ == '__main__':
        executor.start_polling(dp)        