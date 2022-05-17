import datetime
from fast_bitrix24 import BitrixAsync
from bot_create import config_value


whbitrix = config_value['BX']['wh']
bx = BitrixAsync(whbitrix)

""" Создание процесса """
async def bx_create_smart(title, text, name, id_type):
    method = 'crm.item.add'   
    params = {'entityTypeId' : '184', 'fields': 
             {'title': f'{title}',
              'createdBy': '166', 
              'ufCrm10_1644911192216' : id_type, 
              'ufCrm10_1644926802': f'{datetime.date.today()}', 
              'ufCrm10_1644927739266' : '162', 
              'ufCrm10_1644926433' : text, 
              'ufCrm10_1651723524' : name}}
    res = await bx.call(method, params)
    return res

""" Получение элемента процесса """
async def bx_get_smart(smart_id, elem_id):
    res = await bx.call('crm.item.get', {'entityTypeId': smart_id, 'id' : elem_id})
    return res
