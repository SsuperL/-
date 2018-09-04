import pika,os
import uuid,threading,random

class Client(object):
    def __init__(self):
        self.connection=pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel=self.connection.channel()
        result=self.channel.queue_declare(exclusive=False)
        self.callback_queue=result.method.queue
        self.channel.basic_consume(self.callback,no_ack=True,queue=self.callback_queue)
        self.res={}

    def callback(self,ch,method,props,body):
        if self.corr_id==props.correlation_id:
            #判断从服务器端接收的UUID和之前发送的是否相等，借此判断是否是同一个消息队列
            self.response=body#从服务器端收到的消息

    def call(self,n):
        self.response=None
        self.corr_id=str(uuid.uuid4())#客户端发送请求时生成一个唯一的UUID

        self.channel.basic_publish(exchange='',
                                   routing_key='localhost',
                                   properties=pika.BasicProperties(#消息持久化
                                       reply_to=self.callback_queue,
                                   correlation_id=self.corr_id),
                                   body=n)
        while self.response is None:
            self.connection.process_data_events()
            #一般情况下channel.start_consuming表示阻塞模式下接收消息
            #这里不阻塞收消息，且隔一段时间检查有没有消息
            #即非阻塞版的start_consuming
            #print('no message...')#进行到这一步代表没有消息
        task_id=random.randint(0000,9999)
        self.res[task_id]={'result':self.response.decode(),'command':n}
        return self.response.decode()

    def check(self,cmd):
        command=cmd.split()
        if cmd=='check all':
            for i in self.res.keys():
                print('[task_id]',i,'[command]',self.res[i]['command'])
        else:
            task_id = int(command[1])
            print(self.res[task_id]['result'])
            del self.res[task_id]

def main():
    client = Client()
    while True:
        cmd=input('>>').strip()
        command=cmd.split()
        if command[0]=='check':
            client.check(cmd)
        else:
            response=client.call(cmd)
        # print(response)


thread=threading.Thread(target=main)
thread.start()