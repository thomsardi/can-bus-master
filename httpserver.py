import threading
from flask import Flask, request, make_response
# from datareaderthread import DataCollection
from cancallback import DataCollection
import queue
from dataproviderthread import CanDataSimulator
import can

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

        # @self.app.post('/override')
        # def override() :
        #     try :
        #         data = request.json
        #         value = data['override']
        #         uniqueId = 160
        #         # msg = CanDataSimulator()
        #         msg = can.Message()
        #         msg.arbitration_id = 0x1D41C8E8
        #         msg.dlc = 8
        #         msg.data = [(uniqueId & 0xFF), (uniqueId >> 8), value, 0, 0, 0, 0, 0]
        #         msg.is_extended_id = True
        #         self.linkQueue.put(msg)
        #         response = {
        #             "code": "200",
        #             "msg": "SEND_SUCCESS",
        #             "status": True
        #         }
        #         return make_response(response, 200)
        #     except :
        #         response = {
        #             "code": "400",
        #             "msg": "BAD_REQUEST",
        #             "status": False
        #         }
        #         return make_response(response, 400)

        @self.app.route('/override', methods=['POST', 'GET'])
        def override() :
            if request.method == 'POST':
                try :
                    data = request.json
                    value = data['override']
                    uniqueId = 160
                    # msg = CanDataSimulator()
                    msg = can.Message()
                    msg.arbitration_id = 0x1D41C8E8
                    msg.dlc = 8
                    msg.data = [(uniqueId & 0xFF), (uniqueId >> 8), value, 0, 0, 0, 0, 0]
                    msg.is_extended_id = True
                    self.linkQueue.put(msg)
                    response = {
                        "code": "200",
                        "msg": "SEND_SUCCESS",
                        "status": True
                    }
                    return make_response(response, 200)
                except :
                    response = {
                        "code": "400",
                        "msg": "BAD_REQUEST",
                        "status": False
                    }
                    return make_response(response, 400)
            
        
        # @self.app.post('/relay')
        # def relay() :
        #     try :
        #         data = request.json
        #         value = data['relay']
        #         # msg = CanDataSimulator()
        #         msg = can.Message()
        #         msg.arbitration_id = 0x1D41C8E7
        #         msg.dlc = 8
        #         msg.data = [value, 1, 1, 1, 1, 1, 1, 1]
        #         msg.is_extended_id = True
        #         self.linkQueue.put(msg)
        #         response = {
        #             "code": "200",
        #             "msg": "SEND_SUCCESS",
        #             "status": True
        #         }
        #         return make_response(response, 200)
        #     except :
        #         response = {
        #             "code": "400",
        #             "msg": "BAD_REQUEST",
        #             "status": False
        #         }
        #         return make_response(response, 400)

        @self.app.route('/relay', methods=['POST', 'GET'])
        def relay() :
            if request.method == 'POST':    
                try :
                    data = request.json
                    value = data['relay']
                    # msg = CanDataSimulator()
                    msg = can.Message()
                    msg.arbitration_id = 0x1D41C8E7
                    msg.dlc = 8
                    msg.data = [value, 1, 1, 1, 1, 1, 1, 1]
                    msg.is_extended_id = True
                    self.linkQueue.put(msg)
                    response = {
                        "code": "200",
                        "msg": "SEND_SUCCESS",
                        "status": True
                    }
                    return make_response(response, 200)
                except :
                    response = {
                        "code": "400",
                        "msg": "BAD_REQUEST",
                        "status": False
                    }
                    return make_response(response, 400)
            
        
        # @self.app.post('/lvd-low-voltage-config')
        # def lvdLowConfig() :
        #     try :
        #         data = request.json
        #         vsat = data['vsat']
        #         other = data['other']
        #         bts = data['bts']
        #         # msg = CanDataSimulator()
        #         msg = can.Message()
        #         msg.arbitration_id = 0x1D41C8E6
        #         msg.dlc = 8
        #         msg.data = [(vsat & 0xFF), (vsat >> 8), (other & 0xFF), (other >> 8), (bts & 0xFF), (bts >> 8), 0, 0]
        #         msg.is_extended_id = True
        #         self.linkQueue.put(msg)
        #         response = {
        #             "code": "200",
        #             "msg": "SEND_SUCCESS",
        #             "status": True
        #         }
        #         return make_response(response, 200)
        #     except :
        #         response = {
        #             "code": "400",
        #             "msg": "BAD_REQUEST",
        #             "status": False
        #         }
        #         return make_response(response, 400)
            
        @self.app.route('/lvd-low-voltage-config', methods=['POST', 'GET'])
        def lvdLowConfig() :
            if request.method == 'POST':
                try :
                    data = request.json
                    vsat = data['vsat']
                    other = data['other']
                    bts = data['bts']
                    # msg = CanDataSimulator()
                    msg = can.Message()
                    msg.arbitration_id = 0x1D41C8E6
                    msg.dlc = 8
                    msg.data = [(vsat & 0xFF), (vsat >> 8), (other & 0xFF), (other >> 8), (bts & 0xFF), (bts >> 8), 0, 0]
                    msg.is_extended_id = True
                    self.linkQueue.put(msg)
                    response = {
                        "code": "200",
                        "msg": "SEND_SUCCESS",
                        "status": True
                    }
                    return make_response(response, 200)
                except :
                    response = {
                        "code": "400",
                        "msg": "BAD_REQUEST",
                        "status": False
                    }
                    return make_response(response, 400)
            
        # @self.app.post('/lvd-reconnect-voltage-config')
        # def lvdReconnectConfig() :
        #     try :
        #         data = request.json
        #         vsat = data['vsat']
        #         other = data['other']
        #         bts = data['bts']
        #         # msg = CanDataSimulator()
        #         msg = can.Message()
        #         msg.arbitration_id = 0x1D41C8E5
        #         msg.dlc = 8
        #         msg.data = [(vsat & 0xFF), (vsat >> 8), (other & 0xFF), (other >> 8), (bts & 0xFF), (bts >> 8), 1, 1]
        #         msg.is_extended_id = True
        #         self.linkQueue.put(msg)
        #         response = {
        #             "code": "200",
        #             "msg": "SEND_SUCCESS",
        #             "status": True
        #         }
        #         return make_response(response, 200)
        #     except :
        #         response = {
        #             "code": "400",
        #             "msg": "BAD_REQUEST",
        #             "status": False
        #         }
        #         return make_response(response, 400)

        @self.app.route('/lvd-reconnect-voltage-config', methods=['POST', 'GET'])
        def lvdReconnectConfig() :
            if request.method == 'POST':
                try :
                    data = request.json
                    vsat = data['vsat']
                    other = data['other']
                    bts = data['bts']
                    # msg = CanDataSimulator()
                    msg = can.Message()
                    msg.arbitration_id = 0x1D41C8E5
                    msg.dlc = 8
                    msg.data = [(vsat & 0xFF), (vsat >> 8), (other & 0xFF), (other >> 8), (bts & 0xFF), (bts >> 8), 1, 1]
                    msg.is_extended_id = True
                    self.linkQueue.put(msg)
                    response = {
                        "code": "200",
                        "msg": "SEND_SUCCESS",
                        "status": True
                    }
                    return make_response(response, 200)
                except :
                    response = {
                        "code": "400",
                        "msg": "BAD_REQUEST",
                        "status": False
                    }
                    return make_response(response, 400)

        # @self.app.post('/system-config')
        # def systemConfig() :
        #     try :
        #         data = request.json
        #         nominalVoltage = data['nominal_voltage']
        #         # msg = CanDataSimulator()
        #         msg = can.Message()
        #         msg.arbitration_id = 0x1D41C8E4
        #         msg.dlc = 8
        #         msg.data = [(nominalVoltage & 0xFF), (nominalVoltage >> 8), 0, 0, 0, 0]
        #         msg.is_extended_id = True
        #         self.linkQueue.put(msg)
        #         response = {
        #             "code": "200",
        #             "msg": "SEND_SUCCESS",
        #             "status": True
        #         }
        #         return make_response(response, 200)
        #     except :
        #         response = {
        #             "code": "400",
        #             "msg": "BAD_REQUEST",
        #             "status": False
        #         }
        #         return make_response(response, 400)

        @self.app.route('/system-config', methods=['POST', 'GET'])
        def systemConfig() :
            if request.method == 'POST':
                try :
                    data = request.json
                    nominalVoltage = data['nominal_voltage']
                    # msg = CanDataSimulator()
                    msg = can.Message()
                    msg.arbitration_id = 0x1D41C8E4
                    msg.dlc = 8
                    msg.data = [(nominalVoltage & 0xFF), (nominalVoltage >> 8), 0, 0, 0, 0]
                    msg.is_extended_id = True
                    self.linkQueue.put(msg)
                    response = {
                        "code": "200",
                        "msg": "SEND_SUCCESS",
                        "status": True
                    }
                    return make_response(response, 200)
                except :
                    response = {
                        "code": "400",
                        "msg": "BAD_REQUEST",
                        "status": False
                    }
                    return make_response(response, 400)
            

        # @self.app.get('/get-data')
        # def serveData() :
        #     self.data.packCalculate()
        #     response = {
        #         "battery_data" : self.data.buildPackData(),
        #         "stm32_data" : self.data.buildStm32Data()
        #     }
        #     return response
        
        @self.app.route('/get-data')
        def serveData() :
            self.data.packCalculate()
            response = {
                "battery_data" : self.data.buildPackData(),
                "stm32_data" : self.data.buildStm32Data()
            }
            return response
        
        # @self.app.get('/get-param')
        # def getParam() :
        #     lowVoltage : dict = {
        #         "other" : self.data.lowVoltageOther,
        #         "bts" : self.data.lowVoltageBts,
        #         "vsat" : self.data.lowVoltageVsat
        #     }
        #     reconnectVoltage : dict = {
        #         "other" : self.data.reconnectVoltageOther,
        #         "bts" : self.data.reconnectVoltageBts,
        #         "vsat" : self.data.reconnectVoltageVsat
        #     }
        #     response = {
        #         "low_voltage" : lowVoltage,
        #         "reconnect_voltage" : reconnectVoltage
        #     }
        #     return response
        
        @self.app.route('/get-param')
        def getParam() :
            lowVoltage : dict = {
                "other" : self.data.lowVoltageOther,
                "bts" : self.data.lowVoltageBts,
                "vsat" : self.data.lowVoltageVsat
            }
            reconnectVoltage : dict = {
                "other" : self.data.reconnectVoltageOther,
                "bts" : self.data.reconnectVoltageBts,
                "vsat" : self.data.reconnectVoltageVsat
            }
            response = {
                "low_voltage" : lowVoltage,
                "reconnect_voltage" : reconnectVoltage
            }
            return response
    
    def link(self, queue : queue.Queue) :
        self.linkQueue = queue

    def run(self) :
        self.app.run(host='0.0.0.0', port=8001)
    