import threading
from flask import Flask, request, make_response
from datareaderthread import DataCollection
import queue
from dataproviderthread import CanDataSimulator

class Server(threading.Thread) :
    def __init__(self, name : str, data : DataCollection) :
        threading.Thread.__init__(self, name=name)
        self.daemon = True
        self.app = Flask(__name__)
        self.data : DataCollection = data
        self.linkQueue : queue.Queue

        @self.app.route('/', methods=['POST', 'GET'])
        def index():
            if request.method == 'POST':
                value1 = request.form.get('value1')
                value2 = request.form.get('value2')
                return 'OK'
            else:
                return 'Use POST requests'

        @self.app.post('/override')
        def override() :
            try :
                data = request.json
                value = data['override']
                uniqueId = 160
                msg = CanDataSimulator()
                msg.arbitration_id = 0x1D41C8E8
                msg.dlc = 8
                msg.data = [(uniqueId & 0xFF), (uniqueId >> 8), value, 0, 0, 0, 0, 0]
                self.linkQueue.put(msg)
                return make_response("", 200)
            except :
                return make_response("", 400)
            
        
        @self.app.post('/relay')
        def relay() :
            try :
                data = request.json
                value = data['relay']
                msg = CanDataSimulator()
                msg.arbitration_id = 0x1D40C8E8
                msg.dlc = 8
                msg.data = [value, 1, 1, 1, 1, 1, 1, 1]
                self.linkQueue.put(msg)
                return make_response("", 200)
            except :
                return make_response("", 400)
            
        
        @self.app.post('/lvd-config')
        def lvdConfig() :
            try :
                data = request.json
                vsat = data['vsat']
                other = data['other']
                bts = data['bts']
                tolerance = data['tolerance']
                msg = CanDataSimulator()
                msg.arbitration_id = 0x1D42C8E8
                msg.dlc = 8
                msg.data = [(vsat & 0xFF), (vsat >> 8), (other & 0xFF), (other >> 8), (bts & 0xFF), (bts >> 8), (tolerance & 0xFF), (tolerance >> 8)]
                self.linkQueue.put(msg)
                return make_response("", 200)
            except :
                return make_response("", 400)
            
        
        @self.app.post('/system-config')
        def systemConfig() :
            try :
                data = request.json
                nominalVoltage = data['nominal_voltage']
                msg = CanDataSimulator()
                msg.arbitration_id = 0x1D43C8E8
                msg.dlc = 8
                msg.data = [(nominalVoltage & 0xFF), (nominalVoltage >> 8), 0, 0, 0, 0]
                self.linkQueue.put(msg)
                return make_response("", 200)
            except :
                return make_response("", 400)
            

        @self.app.get('/get-data')
        def serveData() :
            response = {
                "battery-data" : self.data.buildPackData(),
                "stm32_data" : self.data.buildStm32Data()
            }
            return response
    
    def link(self, queue : queue.Queue) :
        self.linkQueue = queue

    def run(self) :
        self.app.run(host='0.0.0.0', port=8000)
    