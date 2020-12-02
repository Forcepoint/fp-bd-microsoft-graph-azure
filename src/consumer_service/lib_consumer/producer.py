
from confluent_kafka import Producer
import json

if __name__ == "__main__":
    a = {'user_id': 'Lazy Man', 'timestamp': '2019-10-04T11:59:59.999Z', 'risk_level': 3}
    b = json.dumps(a)
    p = Producer({'bootstrap.servers': 'kafka-iamlab.wbsntest.net:9094'})
    p.produce('ENTITY_RISK_LEVEL', b)
    p.flush(30)