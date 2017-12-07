# 将数据中的_id类型由ObjectId转化为String以Json化
def jsonifym(b):
    b['_id'] = str(b['_id'])
    return b
