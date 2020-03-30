# {
#     'index':0,  #快索引
#     'timestamp':'', #时间戳
#     'transactions':[  #交易信息
#         {
#            'sender':'', #信息交易的发送者
#             'recipient':'', #接受者
#             'amount':5,  #金额
#         }
#     ],
#     'porrf':'',  #工作量证明
#     'pervious_hash':'', #上一个区块的hash值
#     }
import hashlib
import json
from time import time
from urllib import request
from urllib.parse import urlparse
from uuid import uuid4
from argparse import ArgumentParser

import requests

from flask import Flask, jsonify


class Blockchain:
    def __init__(self):
        self.chain = []   #链结构的信息
        self.current_transactions = []  #交易信息
        self.nodes = set()
        self.new_block(proof=100,previous_hash= 1)


    def register_node(self,address:str):  #注册一个节点
        # http://127.0.0.0.1:5001
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url)

    def vaild_chain(self,chain):
        last_block  = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != self.hash(last_block)
                return False

            if not self.valid_proof(last_block['proof'],block['proof']):
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self,chain):
        neighbous = self.nodes
        max_length = len(self.chain)
        new_chain = None
        for node in neighbous:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

            if length > max_length and self.valid_chain(chain):
                  max_length = length
                  new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None): #新添加一个快
        block ={
            'index':len(self.chain) + 1,
            'timestamp': time(),
            'transcations':self.current_transactions,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.last_block)

        }

        self.current_transactions = []
        self.chain.append(block)

        return block


    def new_transactions(self,sender,recipient,amount): #新添加交易
        self.current_transactions.append(
            {
                'sender':sender,
                'recipient':recipient,
                'amount':amount,

            })

        return self.last_block['index'] + 1



    @staticmethod
    def hash(self,block): #计算交易的hash值

        block_string = json.dumps(block,sort_keys=True).encode()

        return hashlib.sha3_256(block_string).hexdigest()


    def last_block(self):  #获取左后一个快:

        return self.chain[-1]


    def proff_of_work(self,last_proof):     #实现工作量证明
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof += 1

            print(proof)

    def valid_proof(self,last_proof,proof):  #
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha3_256(guess).hexdigest()

        print(guess_hash)

        if guess_hash[0:8] == "00000000":
            return True
        else:
            return False


app = Flask(__name__)

block_chain = Blockchain()

node_id=str(uuid4).replace('-','')


@app.route('/transactions/new',methods=['POST','GET'])
def new_transaction():    #添加一个新的交易
    value = requests.get()
    values = value.json()
    required = ['sender','recipient','amount']
    if values is None:
        return '404'
    if not all(k in values for k in required):
        return '400'
    index = block_chain.new_transactions(
                                    values['sender'],
                                    values['recipient'],
                                    values['amount'],
    )

    response = {'message':f'Transaction will be added to bLOCK{index}'}
    return jsonify(response),201

@app.route('/mine',methods=['GET'])
def min():   #定义一个挖矿
    last_block = block_chain.last_block()
    last_proof = last_block['proof']
    proof = block_chain.proff_of_work(last_block)
    block_chain.new_transactions(sender='0',
                                 recipient=node_id,
                                 amount=1
                                 )

    block = block_chain.new_block(proof,None)

    response = {
        'message':'new block',
        'index': block['index'],
        'traansactions':block['transactions'],
        'proof':block['proof'],
        'previous_hash':block['previous_hash']
    }

    return jsonify(response),200

@app.route('/chain',methods=['GET'])
def full_chain():  #返回整个区块链
    response = {
        'chain':block_chain.chain,
        'length':len(block_chain.chain),
    }
    return jsonify(response),200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():    #注册一个交易
    value = requests.get()
    values = value.json()
    nodes = values.get('nodes')

    if nodes is None:
        return 'Error',400

    for node in nodes:
        block_chain.register_node(node)

    response = {
        'message':'New nodes havd benn added',
        'total_nodes':list(block_chain.nodes)

    }
    return jsonify(response)

@app.route('/nodes/resolve',methods=['GET'])
def consenssus():
    replace = block_chain.resolve_conflicts()
    if replace:
        response = {
            'message': 'chain is chgange',
            'new_chain':block_chain.chain
        }
    else:
        response = {
            'message': 'chain is max_length',
            'new_chain': block_chain.chain
        }

    return jsonify(response),200

if __name__ == '__main__':
    parser = ArgumentParser()
    #-p --port
    parser.add_argument('-p', '--port',default=5001,type=int,help='port to listen to ')
    argus = parser.parse_args()
    port = argus.port
    app.run(host='0.0.0.0',port=port)

    # test = Blockchain()
    # test.proff_of_work(100)












