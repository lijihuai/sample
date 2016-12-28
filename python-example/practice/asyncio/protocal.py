import asyncio

import collections

import datetime

STATUS_LINE = "status_line"

STATUS_CODE = "status_code"

HTTP_ENTITY = "http_entity"

Content_Length = "Content-Length"

Transfer_Encoding = "Transfer-Encoding"

class MyHTTProtocol(asyncio.Protocol):


    def __init__(self, loop):
        self.data_length = 0
        self.http_fragment_dict = collections.OrderedDict()
        self.http_fragment_dict[HTTP_ENTITY] = b''
        self.loop = loop
        self.bytes = b''
        self.entity_body_recieving = -1 # 表示都还没有开始解析到响应消息实体

    def connection_made(self, transport):
        # transport.close()
        # pass
        self.transport = transport
        print("连接建立成功，开始第一次HTTP请求")
        print(transport.get_extra_info('peername'), transport.get_extra_info('socket'))
        transport.write(
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
        # print("再次创建一个连接")
        # self.loop.stop()
        # coro_2 = self.loop.create_connection(lambda: MyProtocol(self.loop), 'qisuu.com', 80, sock=socket.socket)
        # self.loop.run_until_complete(coro_2)
        # print("创建一个新连接成功")

    def data_received(self, data):
        print("响应数据到达", datetime.datetime.now())

        if (self.entity_body_recieving < 0):
            self.bytes += data
            self.get_status_line_or_header()
        elif self.entity_body_recieving > 0:
            self.get_entity(data)
            if self.entity_body_recieving == 0:
                # todo 发起下一个 HTTP 请求
                pass
        else:
            if self.entity_body_recieving == 0:
                print("数据传输完成，关闭套接字")
                self.transport.close()
            if data != '\r\n' or data != '\n':
                raise Exception()

    def get_status_line_or_header(self):
        left, middle, right = b'', b'\r\n', b''
        while middle:
            left, middle, right = self.bytes.partition(b'\r\n')
            if STATUS_LINE not in self.http_fragment_dict:
                # 解析状态行
                if middle == b'\r\n':
                    self.http_fragment_dict[STATUS_LINE] = left.decode()
                    self.http_fragment_dict[STATUS_CODE] = left.decode().split(" ")[1]
                    self.bytes = right
            elif self.entity_body_recieving < 0: # 还在解析响应头
                if middle == b'\r\n':
                    if left:
                        [key, _, value] = [b.strip().decode() for b in left.partition(b":")]
                        self.http_fragment_dict[key] = value
                        self.bytes = right
                    else: # 说明响应头已经读取完了，轮到解析消息正文了
                        stats_code = self.http_fragment_dict[STATUS_CODE]
                        if "200"<= stats_code < "300" and stats_code != "204":
                            if Content_Length in self.http_fragment_dict:
                                self.get_entity = self.get_content
                                self.entity_body_recieving = int(self.http_fragment_dict[Content_Length])
                            elif Transfer_Encoding in self.http_fragment_dict:
                                self.get_entity = self.get_chunked
                        if right:
                            self.get_entity(right)
                        break
                elif not middle:
                    pass # 此时说明消息头还没接收完整
                else:
                    raise Exception()
            else:
                raise Exception()


    def get_content(self, data):
        if len(data) <= self.entity_body_recieving:
            self.entity_body_recieving -= len(data)
            self.http_fragment_dict[HTTP_ENTITY] += data

        # 实际上消息体是要把最后的结尾标记 CRLF 也算进去的，所以下面两种情况是不可能发生的
        elif len(data) == self.entity_body_recieving + 1:
            self.entity_body_recieving = 0
            self.http_fragment_dict[HTTP_ENTITY] += data[:-1]
        elif len(data) == self.entity_body_recieving + 2:
            self.entity_body_recieving = 0
            self.http_fragment_dict[HTTP_ENTITY] += data.partition[:-2]
            print("好吧，太好玩了，传输完毕，关闭套接字")

        else:
            # print(self.http_fragment_dict[Content_Length])
            # print(len(data), self.entity_body_recieving)
            raise Exception()

    def get_chunked(self, data):
        pass # TODO

        # print("***************************" * 5)

    def connection_lost(self, exc):
        print("连接断开", datetime.datetime.now())
        # print("停止一个连接，然后准备再次创建一个连接")
        # self.loop.stop()
        # coro_2 = self.loop.create_connection(lambda: MyProtocol(self.loop), 'qisuu.com', 80, sock=socket.socket)
        # self.loop.run_until_complete(coro_2)
        # print("创建一个新连接成功")



loop = asyncio.get_event_loop()

coro = loop.create_connection(lambda: MyHTTProtocol(loop),
                              'qisuu.com', 80)
loop.run_until_complete(coro)
# loop.run_until_complete(coro_2)
loop.run_forever()
# print(coro)
loop.close()
# print("**********" * 10)
# print("**********" * 10)
