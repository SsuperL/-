import pika
import os
class Server(object):
    def __init__(self):
        self.connetion=pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel=self.connetion.channel()
        self.channel.queue_declare(queue='localhost')

    def callback(self,ch,method,props,body):
        '''接收消息并返回结果'''
        cmd=body
        response=self.Execute(cmd)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,#要返回的队列名
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),#使correlation_id等于客户端的并发送回去
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)#确认收到

    def Execute(self,cmd):
        cmd=cmd.decode()
        res=os.popen(cmd).read()
        if not res:
            res='Wrong Command!'
        return res


    def run(self):
        self.channel.basic_consume(self.callback,queue='localhost')
        self.channel.start_consuming()


server=Server()
server.run()