import socket

from practice import asyncio

loop = asyncio.get_event_loop()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(client_socket.connect(('qisuu.com', 80)))

count = 0

def reader():
    print("开始读取 http 响应")
    print(client_socket.recv(1024 * 4).decode())
    global count
    count += 1
    if count > 30:
        loop.stop()
        loop.close()
        client_socket.close()

def writer():
    print("开始发送 http 请求")
    client_socket.sendall(
        b"GET / HTTP/1.1\r\n"
        b"Host:www.qisuu.com\r\n"
        b"Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        b"Accept-Encoding:gzip, deflate, sdch, br\r\n"
        b"Accept-Language:zh-CN,zh;q=0.8,en;q=0.6\r\n"
        b"Cache-Control:max-age=0\r\n"
        b"Connection:keep-alive\r\n"
        b"Cookie:BAIDUID=E1A20313CA631940BB12F1B466D463BA:FG=1; BIDUPSID=E1A20313CA631940BB12F1B466D463BA; PSTM=1481278134; BDUSS=mFMbFh6YjhPUVotfnVQb1lCVlRCbDR1NmdZSWZSUmxpb0duUnA1YTJ1TkVrWE5ZSVFBQUFBJCQAAAAAAAAAAAEAAADQAqYwbGlqaWh1YWl4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEQETFhEBExYU; cflag=15%3A3; BD_HOME=1; BDRCVFR[y-8S9OCiXKD]=mk3SLVN4HKm; BD_CK_SAM=1; PSINO=1; H_PS_PSSID=; BD_UPN=12314753; H_PS_645EC=b532foaVvV1ANBShfIBW3fSM0wmgybCqWVntz2wZN0uIP%2B7YgPSa%2BZvVr4ZInSbf50%2Bu1QL%2Fxcg\r\n"
        b"Upgrade-Insecure-Requests:1\r\n"
        b"User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36\r\n"
        b"\r\n"
    )


# loop.add_reader(client_socket, writer)

loop.add_reader(client_socket, reader)

writer()

loop.run_forever()

# client_socket.close()
