from datetime import datetime, timedelta


# Function to check and filter the orders
# redis_conn2: db of the second relation
# user_id: key of entry from the first relation
# user_data: value for given key from the first relation
def probe_and_filter_orders(redis_conn2, user_id, user_data):
    order_keys = redis_conn2.keys()  # get all order keys from redis_db2

    for order_key in order_keys:
        order_data = redis_conn2.hgetall(order_key)  # get all data from redis_db2 for given order key
        order_data_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in order_data.items()}
        if order_data_decoded and order_data_decoded['user_id'] == user_id:  # check if ordr
            user_reg_time = datetime.strptime(user_data['registration_timestamp'], '%Y-%m-%dT%H:%M:%S')
            order_time = datetime.strptime(order_data_decoded['order_timestamp'], '%Y-%m-%dT%H:%M:%S')
            if order_time <= user_reg_time + timedelta(weeks=1):  # filter joined tuples to include only orders placed within one week of user registration
                print({
                    'user_id': user_id,
                    'user_name': user_data['name'],
                    'user_email': user_data['email'],
                    'registration_timestamp': user_data['registration_timestamp'],
                    'order_id': order_key,
                    'product': order_data_decoded['product'],
                    'order_timestamp': order_data_decoded['order_timestamp']
                })


# Pipelined Hash Join
def pipelined_hash_join(redis_conn1, redis_conn2):
    user_keys = redis_conn1.keys()  # get all user keys from redis_db1  

    for user_key in user_keys:
        user_data = redis_conn1.hgetall(user_key)  # get all data from redis_db1 for given user key  
        if user_data:
            user_data_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in user_data.items()}
            probe_and_filter_orders(redis_conn2, user_key.decode('utf-8'), user_data_decoded)
