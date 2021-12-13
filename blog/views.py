from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from .models import Well, WellType, Warehouse, var, ProjectGroup, Code, Appl_mpz, Appl_mpz_data, Byer, Appl_byer, Appl_by_data
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
import pymysql
import json
from dateutil.relativedelta import relativedelta
import time

month_blocks_arr = []

def post_list(request):
    #get well list
    wells = Well.objects.all().order_by('id')
    wells = wells.reverse()
    serial = '0'
    # mysql_data = pullMySqlBase('localhost', 3303, 'root', 'root', 'welldb')
    # pushPostgreSqlServer(mysql_data)
    if request.method == "GET":
        req = str(request.GET)
        req_dict = request.GET.dict()
        p_arr = []
        print('REQ: ', req_dict)
        for elem in req_dict.items():
            p_arr.append(elem[1])
        if req.find('release') != -1:
            well = Well()
            well.serial = p_arr[3]
            well.type = str(p_arr[2])
            date = str(p_arr[1])
            date_lst = date.split('/')
            date = date_lst[2] + '-' + date_lst[1] + '-' + date_lst[0]
            well.locate = str(p_arr[4])
            well.comment = ''
            well.release()

            cur_serial = var.objects.all().order_by('id')
            for elem in cur_serial:
                last_part_month = elem.month
                last_part_num = elem.part_num

            cur_date = datetime.now()

            if str(cur_date.month) != str(last_part_month):
                cur_part_month = str(cur_date.month)
                cur_part_num = '1'
            else:
                cur_part_num = int(last_part_num)
                cur_part_num += 1
                cur_part_month = last_part_month
            cur_part_month = cur_part_month
            cur_part_num = cur_part_num

            record = var.objects.get(id = 1)
            record.month = cur_part_month
            record.part_num = cur_part_num
            record.save(update_fields=['month', 'part_num'])

            data = {
                'resp': str('success')
            }


            return JsonResponse(data, content_type='application/json')
        if req.find('get_init_transfer_data') != -1:
            code_lst = Code.objects.all().order_by('id')
            appl_mpz_lst = Appl_mpz.objects.all().order_by('id')
            buyer_lst = Byer.objects.all().order_by('id')
            appl_buy_lst = Appl_byer.objects.all().order_by('id')
            res_arr = []
            p_res_arr = []
            p_arr = []
            pp_arr = []
            data = {}
            for elem in code_lst:
                p_arr = []
                pp_arr = []
                p_arr.append(elem.code_name)
                for p_elem in appl_mpz_lst:
                    if elem.id == p_elem.connect_id:
                        pp_arr.append(p_elem.mpz_appl_name)
                p_arr.append(pp_arr)
                p_res_arr.append(p_arr)
            res_arr.append(p_res_arr)
            data[0] = p_res_arr
            p_res_arr = []
            for elem in buyer_lst:
                p_arr = []
                pp_arr = []
                p_arr.append(elem.by_name)
                for p_elem in appl_buy_lst:
                    if elem.id == p_elem.connect_id:
                        pp_arr.append(p_elem.by_appl_name)
                p_arr.append(pp_arr)
                p_res_arr.append(p_arr)
            res_arr.append(p_res_arr)
            data[1] = p_res_arr
            json_data = json.dumps(data)
            json_res = json.loads(json_data)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('modal') != -1:
            cur_serial = var.objects.all().order_by('id')
            for elem in cur_serial:
                last_part_month = elem.month
                last_part_num = elem.part_num

            cur_date = datetime.now()

            if str(cur_date.month) != str(last_part_month):
                cur_part_month = str(cur_date.month)
                cur_part_num = '1'
            else:
                cur_part_num = int(last_part_num)
                cur_part_num += 1
                cur_part_month = last_part_month
            cur_part_month = cur_part_month
            cur_part_num = cur_part_num

            if len(cur_part_month) == 1:
                cur_part_month = '0' + str(cur_part_month)
            else:
                cur_part_month = str(cur_part_month)
            cur_part_year = str(cur_date.year)
            cur_part_year = cur_part_year[2] + cur_part_year[3]
            cur_serial_num = cur_part_month + cur_part_year + '/' + str(cur_part_num)
            data = {
                'serial': str(cur_serial_num)
            }
            return JsonResponse(data, content_type='application/json')
        if req.find('get_well_lst') != -1:
            type = p_arr[1]
            well_lst = Well.objects.all().order_by('id')
            data = {}
            p_arr
            i = 0
            check = False
            for well in well_lst:
                if str(well.type) == str(type):
                    check = True
                    pp_arr = []
                    pp_arr.append(str(well.type))
                    pp_arr.append(str(well.serial))
                    pp_arr.append(str(well.created_date))

                    data[i] = pp_arr
                    json_data = json.dumps(data)
                    i += 1
            if check == True:
                json_res = json.loads(json_data)
            else:
                json_res = {}
            return JsonResponse(json_res, content_type='application/json')
        if req.find('transfer_well') != -1:
            trans_type = p_arr[1]
            trans_date = p_arr[2]
            trans_target = p_arr[3]
            trans_subtarget = p_arr[4]
            serial_lst = str(p_arr[5]).split('%')
            if trans_type == 'transfer':
                trans_comment = 'перемещен ' + trans_date + ' числа на объект ' + trans_target + ' по заявке МПЗ№' + trans_subtarget
            else:
                trans_comment = 'продан ' + trans_date + ' числа организации ' + trans_target + ' по заявке №' + trans_subtarget
            for elem in serial_lst:
                record = Well.objects.get(serial=elem)
                record.comment = trans_comment
                record.locate = trans_target
                record.req_num = trans_subtarget
                record.trans_date = trans_date
                record.save(update_fields=['comment', 'locate', 'req_num', 'trans_date'])
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('m29_get_data') != -1:
            res_arr = []
            temp_p_arr = []
            pp_arr = []
            if p_arr[2] == 'null':
                date = datetime.now().date()
                p_range_start = str(date - relativedelta(months=1)).split('-')
                range_start = p_range_start[2] + '.' + p_range_start[1] + '.' + p_range_start[0]
                p_range_end = (str(date)).split('-')
                range_end = p_range_end[2] + '.' + p_range_end[1] + '.' + p_range_end[0]
            else:
                range_start = str(p_arr[1]).replace('/','.')
                range_end = str(p_arr[2]).replace('/', '.')
            # refactor start range date to datetime obj
            date_arr_start = range_start.split('.')
            p_range_start = datetime.date(datetime.now())
            range_start = p_range_start.replace(int(date_arr_start[2]), int(date_arr_start[1]), int(date_arr_start[0]))

            # refactor end range date to datetime obj
            date_arr_end = range_end.split('.')
            p_range_end = datetime.date(datetime.now())
            range_end = p_range_end.replace(int(date_arr_end[2]), int(date_arr_end[1]), int(date_arr_end[0]))

            wells = WellType.objects.all().order_by('id')
            for well in wells:
                temp_p_arr = []
                count_start = 0
                count_end = 0
                count_input = 0
                count_output = 0
                temp_p_arr.append(str(well.type_name))
                rows = Well.objects.filter(type=well.type_name).order_by('id')
                # get state by start and end range
                for row in rows:
                    rel_date = str(row.created_date)
                    date_arr = rel_date.split('-')
                    p_rel_date = datetime.date(datetime.now())
                    rel_date = p_rel_date.replace(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))

                    if str(row.trans_date) != '':
                        trans_date = str(row.trans_date)
                        date_arr = trans_date.split('.')
                        p_trans_date = datetime.date(datetime.now())
                        trans_date = p_trans_date.replace(int(date_arr[2]), int(date_arr[1]), int(date_arr[0]))
                    else:
                        trans_date = None

                    if (rel_date < range_start and str(row.trans_date) == '') or (
                            rel_date < range_start and range_start <= trans_date):
                        check_start = True
                    else:
                        check_start = False

                    if (rel_date <= range_end and str(row.trans_date) == '') or (
                            rel_date <= range_end and range_end < trans_date):
                        check_end = True
                    else:
                        check_end = False

                    if (rel_date >= range_start) and (rel_date <= range_end):
                        check_input = True
                    else:
                        check_input = False

                    if str(row.trans_date) != '':
                        if (trans_date >= range_start) and (trans_date <= range_end):
                            check_output = True
                        else:
                            check_output = False
                    else:
                        check_output = False

                    if check_start == True:
                        count_start += 1
                    if check_end == True:
                        count_end += 1
                    if check_input == True:
                        count_input += 1
                    if check_output == True:
                        count_output += 1

                temp_p_arr.append(str(count_start))
                temp_p_arr.append(str(count_end))
                temp_p_arr.append(str(count_input))
                temp_p_arr.append(str(count_output))
                res_arr.append(temp_p_arr)
            data = {}
            data[0] = res_arr
            json_data = json.dumps(data)
            json_res = json.loads(json_data)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('check_login') != -1:
            print('check login')
            user = authenticate(username=str(p_arr[1]), password=str(p_arr[2]))
            token = ''
            if user is not None:
                data = {
                    'result': str('success')
                }
            else:
                data = {
                    'result': str('error')
                }
            return JsonResponse(data, content_type='application/json')
        if req.find('check_session') != -1:
            print('p_arr: ', p_arr)
            if len(p_arr[2]) != '':
                user = authenticate(username=str(p_arr[1]))
                if user is not None:
                    if user.is_active:
                        is_auth = user.is_authenticated
                        data = {
                            'result': str('success')
                        }
                else:
                    data = {
                        'result': str('error')
                }
            else:
                    data = {
                        'result': str('notlogin')
                }

            return JsonResponse(data, content_type='application/json')
        else:
            # get type list
            types = WellType.objects.all().order_by('id')
            type_first_elem = types[0].type_name

            # get wh list
            first_code_mpz_lst_first_elem = ''
            wh_lst = Warehouse.objects.all().order_by('id')
            wh_first_elem = wh_lst[0]
            types = WellType.objects.all().order_by('id')
            code_lst = Code.objects.all().order_by('id')
            code_first_elem = code_lst[0].code_name
            appl_mpz_lst = Appl_mpz.objects.all().order_by('id')
            first_code_mpz_lst = []
            for elem in appl_mpz_lst:
                if code_lst[0].id == elem.connect_id:
                    first_code_mpz_lst.append(elem.mpz_appl_name)
            first_code_mpz_lst_first_elem = first_code_mpz_lst[0]

            return render(request, 'blog/post_list.html', {'wells': wells, 'types': types, 'type_first_elem': type_first_elem, 'wh_lst': wh_lst, 'wh_first_elem': wh_first_elem, 'code_lst': code_lst, 'code_first_elem': code_first_elem, 'first_code_mpz_lst': first_code_mpz_lst, 'first_code_mpz_lst_first_elem': first_code_mpz_lst_first_elem})

def structure(request):
    if request.method == "GET":
        req = str(request.GET)
        req_dict = request.GET.dict()
        p_arr = []
        for elem in req_dict.items():
            p_arr.append(elem[1])
        if req.find('new_pg') != -1:
            unique = 'false'
            pg_lst = ProjectGroup.objects.all().order_by('id')
            for pg in pg_lst:
                if pg.pg_name == p_arr[1]:
                    unique = 'true'
                    break
            if unique == 'false':
                ProjectGroup.objects.create(pg_name=p_arr[1])
                data = {'result': str('success')}
            else:
                data = {'result': str('error')}
            return JsonResponse(data, content_type='application/json')
        if req.find('new_code') != -1:
            unique = 'false'
            code_lst = Code.objects.all().order_by('id')
            for code in code_lst:
                if code.code_name == p_arr[1]:
                    unique = 'true'
                    break
            if unique == 'false':
                Code.objects.create(code_name= p_arr[1], connect_id=p_arr[2])
                data = {'result': str('success')}
            else:
                data = {'result': str('error')}
            return JsonResponse(data, content_type='application/json')
        if req.find('new_mpz') != -1:
            unique = 'false'
            mpz_lst = Appl_mpz.objects.all().order_by('id')
            print(mpz_lst)
            for mpz in mpz_lst:
                print('==============')
                print('mpz: ', mpz.mpz_appl_name)
                print('new: ', p_arr[1])
                if mpz.mpz_appl_name == p_arr[1]:
                    unique = 'true'
                    break
            if unique == 'false':
                Appl_mpz.objects.create(mpz_appl_name=p_arr[1], connect_id=p_arr[2])
                data = {'result': str('success')}
            else:
                data = {'result': str('error')}
            return JsonResponse(data, content_type='application/json')
        if req.find('del_pg') != -1:
            record = ProjectGroup.objects.get(id = p_arr[1])
            record.delete()
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('del_code') != -1:
            record = Code.objects.get(id = p_arr[1])
            record.delete()
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('del_mpz') != -1:
            record = Appl_mpz.objects.get(id = p_arr[1])
            record.delete()
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('edit_mpz_well') != -1:
            appl_data_arr = Appl_mpz_data.objects.all().order_by('id')
            cur_id = -1
            for elem in appl_data_arr:
                if elem.applID == p_arr[1] and elem.typeID == p_arr[2]:
                    cur_id = elem.id
            if cur_id == -1:
                Appl_mpz_data.objects.create(applID_id=p_arr[1], typeID_id=p_arr[2], w_value=p_arr[3])
            else:
                record = Appl_mpz_data.objects.get(id=cur_id)
                record.w_value = p_arr[3]
                record.save(update_fields=['w_value'])
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('get_mpz') != -1:
            well_lst = Appl_mpz_data.objects.all().order_by('id')
            types = WellType.objects.all().order_by('id')
            appl_lst = Appl_mpz.objects.all().order_by('id')
            appl_cur_id = p_arr[1]
            data = {}
            arr = []
            p_arr = []
            for type in types:
                value = 0
                for well in well_lst:
                    if str(well.applID) == str(appl_cur_id) and str(well.typeID) == str(type.id):
                        value = int(well.w_value)
                p_arr.append(value)
            # print('MPZ IN: ', p_arr)
            wells = Well.objects.all().order_by('id')
            appls = Appl_mpz.objects.all().order_by('id')
            mpz_cur_num = '0'
            for appl in appls:
                if str(appl.id) == str(appl_cur_id):
                    mpz_cur_num = str(appl.mpz_appl_name)
            ppp_arr = []
            for type in types:
                well_counter = 0
                for well in wells:
                    if str(well.req_num) == str(mpz_cur_num) and str(well.type) == str(type.type_name):
                        well_counter+=1
                ppp_arr.append(well_counter )
            # print('MPZ OUT: ', ppp_arr)
            j = 0
            pppp_arr = []
            for j in range(len(types)):
                delta = int(p_arr[j]) - int(ppp_arr[j])
                pppp_arr.append(delta)
            # print('MPZ DELTA: ', pppp_arr)
            for i in range(len(types)):
                pp_arr = []
                pp_arr.append(str(types[i]))
                pp_arr.append(str(p_arr[i]))
                pp_arr.append(str(ppp_arr[i]))
                pp_arr.append(str(pppp_arr[i]))
                data[i] = pp_arr
                json_data = json.dumps(data)
            json_res = json.loads(json_data)
            # print('json_res: ', json_res)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('get_by_data') != -1:
            data = {}
            buyers = Byer.objects.all().order_by('id')
            appl_byers = Appl_byer.objects.all().order_by('id')
            i = 0
            for elem in buyers:
                p_arr = []
                pp_arr = []
                p_arr.append(elem.by_name)
                for p_elem in appl_byers:
                    if p_elem.connect_id == elem.id:
                        pp_arr.append(p_elem.by_appl_name)
                p_arr.append(pp_arr)
                data[i] = p_arr
                json_data = json.dumps(data)
                i+=1
            json_res = json.loads(json_data)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('new_by') != -1:
            unique = 'false'
            buyers = Byer.objects.all().order_by('id')
            for buyer in buyers:
                if p_arr[1] == buyer.by_name:
                    unique = 'true'
                    break
            if unique == 'false':
                Byer.objects.create(by_name=p_arr[1])
                json_res = {'unique': unique, 'by_par_len' : buyers.__len__()}
            else:
                json_res = {'unique' : unique}
            return JsonResponse(json_res, content_type='application/json')
        if req.find('del_by') != -1:
            print('DELL BY: ', p_arr[1])
            record = Byer.objects.get(by_name = p_arr[1])
            record.delete()
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('new_app_by') != -1:
            buyers = Byer.objects.all().order_by('id')
            byers = Byer.objects.all().order_by('id')
            for elem in buyers:
                if elem.by_name == p_arr[2]:
                    par_id = elem.id
            appl_byers = Appl_byer.objects.all().order_by('id')
            check_unique = False
            for p_elem in appl_byers:

                if p_elem.connect_id == par_id:
                    if p_arr[1] == p_elem.by_appl_name:
                        check_unique = True
            if check_unique == False:
                Appl_byer.objects.create(by_appl_name=p_arr[1], connect_id=par_id)
                data = {'result': str('success')}
            else:
                data = {'result': str('denied')}
            return JsonResponse(data, content_type='application/json')
        if req.find('del_app_by') != -1:
            appl_buyers_lst = Appl_byer.objects.all().order_by('id')
            buyers_lst = Byer.objects.all().order_by('id')
            for by in buyers_lst:
                if by.by_name == p_arr[2]:
                    cur_by_id = by.id
            for app in appl_buyers_lst:
                if app.by_appl_name == p_arr[1] and app.connect_id == cur_by_id:
                    record = Appl_byer.objects.get(id=app.id)
                    record.delete()
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('get_app_by_data') != -1:
            buyers_lst = Byer.objects.all().order_by('id')
            cur_app_name = p_arr[1]
            cur_by_name = p_arr[2]
            for by in buyers_lst:
                if by.by_name == p_arr[2]:
                    cur_by_id = by.id
            app_lst = Appl_byer.objects.order_by('id')
            for app in app_lst:
                if app.by_appl_name == p_arr[1] and app.connect_id == cur_by_id:
                    cur_app_id = app.id
            app_data_lst = Appl_by_data.objects.order_by('id')
            types_lst = WellType.objects.order_by('id')
            p_arr = []
            for type in types_lst:
                value = 0
                for p_data in app_data_lst:
                    if p_data.applID_id == cur_app_id and p_data.byID_id == cur_by_id and p_data.typeID_id == type.id:
                        value = p_data.w_value
                p_arr.append(value)
            # print('MPZ IN: ', p_arr)
            wells = Well.objects.all().order_by('id')
            ppp_arr = []
            for type in types_lst:
                well_counter = 0
                for well in wells:
                    if str(well.req_num) == str(cur_app_name) and str(well.locate) == str(cur_by_name) and str(well.type) == str(type.type_name):
                        well_counter+=1
                ppp_arr.append(well_counter)
            # print('MPZ OUT: ', ppp_arr)
            j = 0
            pppp_arr = []
            for j in range(len(types_lst)):
                delta = int(p_arr[j]) - int(ppp_arr[j])
                pppp_arr.append(delta)
            # print('MPZ DELTA: ', pppp_arr)
            data = {}
            for i in range(len(types_lst)):
                pp_arr = []
                pp_arr.append(str(types_lst[i]))
                pp_arr.append(str(p_arr[i]))
                pp_arr.append(str(ppp_arr[i]))
                pp_arr.append(str(pppp_arr[i]))
                data[i] = pp_arr
                json_data = json.dumps(data)
            json_res = json.loads(json_data)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('edit_byapp_well') != -1:
            app_name = p_arr[1]
            well_type_id = p_arr[2]
            new_val = p_arr[3]
            par_name = p_arr[4]
            buyers_lst = Byer.objects.all().order_by('id')
            for by in buyers_lst:
                if by.by_name == par_name:
                    cur_by_id = by.id
            app_lst = Appl_byer.objects.order_by('id')
            for app in app_lst:
                if app.by_appl_name == app_name and app.connect_id == cur_by_id:
                    cur_app_id = app.id
            appl_data_arr = Appl_by_data.objects.all().order_by('id')
            cur_id = -1
            for elem in appl_data_arr:
                if elem.applID == cur_app_id and elem.typeID == well_type_id and elem.parID == cur_by_id:
                    cur_id = elem.id
            if cur_id == -1:
                Appl_by_data.objects.create(applID_id=cur_app_id, byID_id=cur_by_id, typeID_id=well_type_id, w_value=new_val)
            else:
                record = Appl_by_data.objects.get(id=cur_id)
                record.w_value = new_val
                record.save(update_fields=['w_value'])
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        else:
            pg_dict = ProjectGroup.objects.all().order_by('id')
            code_dict = Code.objects.all().order_by('id')
            mpz_dict = Appl_mpz.objects.all().order_by('id')
            types = WellType.objects.all().order_by('id')

            return render(request, 'blog/structure.html', {'pg_lst': pg_dict, 'code_lst': code_dict, 'mpz_lst': mpz_dict, 'types': types})

def statistic(request):
    if request.method == "GET":
        req = str(request.GET)
        req_dict = request.GET.dict()
        p_arr = []
        if req.find('stat_get_release_data') != -1:
            release_subhead_arr = makeReleaseSubHead()
            release_head_arr = makeReleaseHead(release_subhead_arr)
            release_data = makeReleaseData()
            release_color = getReleaseColorArray()
            transfer_head_arr = makeTransferHead()
            transfer_subhead_arr = makeTransferSubHead(transfer_head_arr)
            transfer_color = getTransferColorArray(transfer_head_arr)
            transfer_data = getReleaseResultDataArray()
            print('TRANSFER DATA: ', transfer_data)

            data = {}
            data[0] = release_head_arr
            data[1] = release_subhead_arr
            data[2] = release_data
            data[3] = release_color
            data[4] = transfer_head_arr
            data[5] = transfer_subhead_arr
            data[6] = transfer_data
            data[7] = transfer_color
            json_data = json.dumps(data)
            json_res = json.loads(json_data)
            return JsonResponse(json_res, content_type='application/json')
        else:
            return render(request, 'blog/statistic.html',
                          {'load': 'success'})

#----------------------------------------STATISTIC RELEASE HEAD---------------------------------------------------------
def makeReleaseHead(release_subhead_arr):
    month_arr = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                 'Ноябрь', 'Декабрь']
    #start custom init
    years_count, cur_years_lst = getYearsCount()
    cur_count = getSummTblBackCellCount(int(years_count))
    i = -1
    cell_name = ''
    mon_block_start = 0
    p_arr = []
    for i in range(cur_count):
        if i == 0:
            cell_name = ''
        if i > 0 and i <= years_count:
            cell_name = ''
        if i > years_count and i < cur_count-1:
            cell_name = str(month_arr[i-years_count-1])
        if i == cur_count-1:
            cell_name = ''
        p_arr.append(cell_name)
    pp_arr = []
    res_arr = []
    i = 0
    j = 0
    for elem in release_subhead_arr:
        pp_arr = []
        i = 0
        if len(elem) > 1:

            pp_arr.append(p_arr[j])
            for i in range(len(elem)-1):
                pp_arr.append('')
        else:
            pp_arr.append(p_arr[j])
        res_arr.append(pp_arr)
        j+=1
    return res_arr

def getYearsCount():
    arr = []
    now = int(datetime.now().date().year)
    count = 1
    st_date = 2020
    arr.append(st_date)
    while st_date != now:
        st_date+=1
        arr.append(st_date)
        count+=1
    return count, arr

def getSummTblBackCellCount(years_count):
    res = years_count + 14
    return res

#----------------------------------------STATISTIC RELEASE SUBHEAD------------------------------------------------------

def makeReleaseSubHead():
    # start custom init
    cell_name = ''
    years_count, cur_years_lst = getYearsCount()
    month_blocks_arr = getWeekLst()
    cur_count = len(month_blocks_arr) + 2 + years_count
    i = -1
    p_arr = []
    res_arr = []
    pp_arr = []
    for i in range(cur_count):
        pp_arr = []
        j = 0
        if i == 0:
            cell_name = 'Колодец'
            pp_arr.append(cell_name)
        if i > 0 and i <= years_count:
            cell_name = str(cur_years_lst[i - 1])
            pp_arr.append(cell_name)
        if i > years_count and i < cur_count - 1:
            cur_ind = i - years_count - 1
            elem = month_blocks_arr[cur_ind]
            p_elem = elem[2]
            for pp_elem in p_elem:
                if str(pp_elem) != 'O':
                    cell_name = str(pp_elem) + '\n' + str(
                        elem[3][j])
                else:
                    cell_name = str(pp_elem)
                j+=1
                pp_arr.append(cell_name)
        if i == cur_count - 1:
            cell_name = 'Остаток'
            pp_arr.append(cell_name)
        res_arr.append(pp_arr)

    return res_arr

def getSummTblFrontCellCount(years_count):
    week_arr = getWeekLst()
    count = 0
    for elem in week_arr:
        count = count + int(elem[1])
    res = count + 2 + years_count
    return res

def getWeekLst():
    p_arr = []
    week_arr = []
    res_arr = []
    cur_month = 1
    past_month = 0
    cur_year = int(datetime.now().year)
    week_lst = culcWeekLst(cur_year)
    count = 0
    i = 1
    for i in range(1,13,1):
        count = 0
        p_arr = []
        pp_arr= []
        day = 0
        for elem in week_lst:
            p_week = str(elem)
            week = p_week.split('-')
            if i == int(week[1]):
                count+=1
                pp_arr.append(week[2])
            if count == 1:
                day = int(week[2])
        p_arr.append(i)
        p_arr.append(count)
        p_arr.append(day)
        p_arr.append(pp_arr)
        week_arr.append(p_arr)
        i+=1
    for elem in week_arr:
        p_arr = []
        mon = elem[0]
        week = elem[1]
        day = elem[2]
        w_lst = elem[3]
        l_lst = []
        check = False

        if day != 1:
            p_rel_date = datetime.now().date()
            rel_date = p_rel_date.replace(int(datetime.now().year), int(mon), 1)
            if int(rel_date.weekday()) < 5:
                week+=1
                check = True
        week+=1
        if week == 7:
            week = 6
        if str(w_lst[0]) != '01' and check == True:
            w_lst.insert(0, '01')
            last_week_day = 0
        i = 0
        for i in range(len(w_lst)):
            if i < len(w_lst)-1:
                last_week_day = int(w_lst[i+1]) -1
                if last_week_day < 10:
                    last_week_day = '0' + str(last_week_day)
                else:
                    last_week_day = str(last_week_day)
            else:
                last_week_day = getMonthCount(datetime.now().year, mon)
            l_lst.append(last_week_day)


        w_lst.append('O')
        l_lst.append(' ')
        p_arr.append(mon)
        p_arr.append(week)
        p_arr.append(w_lst)
        p_arr.append(l_lst)
        res_arr.append(p_arr)
    month_blocks_arr = res_arr

    return res_arr

def culcWeekLst(year):
    """ will return all the week from selected year """
    import datetime
    WEEK = {'MONDAY': 0, 'TUESDAY': 1, 'WEDNESDAY': 2, 'THURSDAY': 3, 'FRIDAY': 4, 'SATURDAY': 5, 'SUNDAY': 6}
    MONTH = {'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
             'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12}
    year = int(year)
    month = MONTH['JANUARY']
    day = WEEK['MONDAY']
    dt = datetime.date(year, month, 1)
    dow_lst = []
    while dt.weekday() != day:
        dt = dt + datetime.timedelta(days=1)
    lst_month = MONTH.values()
    sorted(lst_month)
    for mont in lst_month:
        while dt.month == mont:
            dow_lst.append(dt)
            dt = dt + datetime.timedelta(days=7)
    return dow_lst

def getMonthCount(year, month):
    p_rel_date = datetime.now().date()
    next_day = p_rel_date.replace(year, month, 1)
    check_month = True
    count = 0
    while check_month == True:
        next_day = next_day + timedelta(days=1)
        count += 1
        if int(next_day.month) != month:
            check_month = False

    return count

def getSubblocks():
    arr = []
    name_arr = []
    p_name_arr = []
    count = 0
    month_blocks_arr = getWeekLst()
    for elem in month_blocks_arr:
        weight = 120 / int(elem[1])
        names = elem[2]
        p_names = elem[3]
        i = 0
        for i in range(int(elem[1])):
            count+=1
            arr.append(weight)
        for elem in names:
            name_arr.append(elem)
        for elem in p_names:
            p_name_arr.append(str(elem))
    return arr, name_arr, p_name_arr

#----------------------------------------STATISTIC RELEASE DATA---------------------------------------------------------

def makeReleaseData():
    data = []
    p_data = []
    # get well type lst
    welltype_rows = WellType.objects.all().order_by('id')
    # cur.execute("SELECT WellType, DateRelease FROM tbl_main")
    well_rows = Well.objects.order_by('id')
    # cur.execute("SELECT WellType, Location FROM tbl_main")
    # loc_rows = cur.fetchall()
    for row in welltype_rows:
        years_stat = getYearsStat(row.type_name, well_rows)
        week_stat = getWeekStat(row.type_name, well_rows)
        cur_count_stat = getCurState(row.type_name, well_rows)
        p_data.append('С-пласт ' + str(row.type_name))
        for elem in years_stat:
            p_data.append(elem)
        for p_elem in week_stat:
            p_data.append(p_elem)
        p_data.append(cur_count_stat)
        data.append(p_data)
        p_data = []
    return data

def getYearsStat(type, well_rows):
    res_arr = []
    years_count, years_arr = getYearsCount()

    for year in years_arr:
        count = 0
        for row in well_rows:
            p_row = str(row.created_date).split('-')
            y_row = p_row[0]
            # pp_row = str(row.type).split(' ')
            t_row = row.type
            if t_row == str(type) and y_row == str(year):
                count+=1
        res_arr.append(count)
    return res_arr

def getWeekStat(cur_well_type, well_rows):
    res_arr = []
    month_blocks_arr = getWeekLst()
    for elem in month_blocks_arr:
        i = 0
        mon_count = 0
        mon_arr= []
        mon = elem[0]
        week_start = elem[2]
        week_end = elem[3]
        for i in range(0, len(week_start)-1, 1):

            count = 0
            start_day = int(week_start[i])
            end_day = int(week_end[i])
            date = datetime.now().date()
            date_start = date.replace(int(datetime.now().year), int(mon), start_day)
            date_end = date.replace(int(datetime.now().year), int(mon), end_day)
            for well in well_rows:
                date_rel = str(well.created_date)
                p_day_rel = date_rel.split('-')
                day_rel = int(p_day_rel[2])
                mon_rel = int(p_day_rel[1])
                year_rel = int(p_day_rel[0])

                well_type = str(well.type)
                date_rel = date.replace(int(year_rel), int(mon_rel), int(day_rel))
                if well_type.find(cur_well_type) != -1 and date_rel >= date_start and date_rel <= date_end:
                    count+=1
            mon_count = mon_count+count
            mon_arr.append(count)
        for p_elem in mon_arr:
            res_arr.append(p_elem)
        res_arr.append(mon_count)
        mon_count = 0
        mon_arr = []
    return res_arr

def getCurState(cur_well_type, loc_arr):
    count = 0
    for well in loc_arr:
        type = str(well.type)
        loc = str(well.locate)
        if type.find(cur_well_type) != -1 and loc.find('склад') != -1:
            count+=1
    return count

def getReleaseColorArray():
    res_arr = []
    check = "0"
    month_blocks_arr = getWeekLst()
    years_count, cur_years_lst = getYearsCount()
    cur_count = getSummTblFrontCellCount(int(years_count))
    for elem in month_blocks_arr:
        if check == "1":
            check = "0"
        else:
            check = "1"
        for p_elem in elem[2]:
            res_arr.append(check)
    res_arr.append('1')
    while len(res_arr) != cur_count:
        res_arr.insert(0, "0")
    return res_arr

#----------------------------------------STATISTIC TRANSFER HEAD--------------------------------------------------------

def makeTransferHead():
    release_head_arr = []
    p_arr = []
    p_color_arr = []
    check = False
    ch_count = 0
    i = 0

    manager_rows = ProjectGroup.objects.all().order_by('id')
    p_arr.append('')
    for row in manager_rows:
        p_arr.append(str(row.pg_name))
    p_arr.append('Сторонние продажи')
    p_arr.append('ИТОГО')
    i = 0
    pp_arr = []
    for i in range(len(p_arr)):
        pp_arr = []
        if i == 0:
            pp_arr.append(p_arr[i])
        if i > 0:
            pp_arr.append(p_arr[i])
            pp_arr.append('')
            pp_arr.append('')
        release_head_arr.append(pp_arr)

    return release_head_arr

#----------------------------------------STATISTIC RELEASE SUBHEAD------------------------------------------------------

def makeTransferSubHead(head_arr):
    p_arr = []
    pp_arr = ['В заявках', 'Выдано', 'К выдаче']
    res_arr = []
    p_ind = 0
    p_arr.append('Колодец')
    res_arr.append(p_arr)
    i = 0
    for i in range((len(head_arr)-1)):
        p_arr = []
        res_arr.append(pp_arr)
    return res_arr

#----------------------------------------STATISTIC RELEASE DATA---------------------------------------------------------

def getReleaseResultDataArray():
    in_req_data_array = getInRequestsDataArr()
    release_data_array = getReleaseDataArray()
    delta_data_array = getDeltaDataArr(in_req_data_array, release_data_array)
    type_rows = WellType.objects.all().order_by('id')
    p_arr = []
    j = 0
    elem = in_req_data_array[0][1]
    pp_arr = []
    for j in range(len(elem)):
        i = 0
        pp_arr = []
        for i in range(len(in_req_data_array)):
            elem_in_req = in_req_data_array[i][1]
            data_in_req = elem_in_req[j]
            elem_release = release_data_array[i][1]
            data_release = elem_release[j]
            elem_delta = delta_data_array[i][1]
            data_delta = elem_delta[j]
            pp_arr.append(data_in_req)
            pp_arr.append(data_release)
            pp_arr.append(data_delta)
        p_arr.append(pp_arr)
    i = 0
    for elem in p_arr:
        type_name = 'С-пласт ' + str(type_rows[i].type_name)
        elem.insert(0, type_name)
        i+=1
    result_data_arr = p_arr
    return result_data_arr

def getInRequestsDataArr():
    #GET IN REQUESTS DATA ARRAY
    #GET PG DATA LST
    obj_lst_arr = []
    in_req_arr = []
    p_arr = []
    pp_arr = []
    pm_rows = ProjectGroup.objects.all().order_by('id')

    for row in pm_rows:
        p_arr = []
        pp_arr = []
        p_arr.append(row.pk)
        p_code_rows = Code.objects.all().order_by('id')
        codes_rows = []
        for p_elem in p_code_rows:
            if p_elem.connect_id == row.pk:
                codes_rows.append(p_elem.pk)

        for p_row in codes_rows:
            pp_arr.append(p_row)
        p_arr.append(pp_arr)
        obj_lst_arr.append(p_arr)


    pm_req_lst = []
    p_arr = []
    for elem in obj_lst_arr:
        p_arr = []
        pp_arr = []
        p_arr.append(elem[0])
        p_req_rows = Appl_mpz.objects.all().order_by('id')
        for p_elem in elem[1]:
            req_rows = []
            # cur.execute(
            #     "SELECT ID FROM tbl_requestlst WHERE codeID = (" + str(
            #         p_elem) + ")")

            for ppp_elem in p_req_rows:
                if ppp_elem.connect_id == p_elem:
                    req_rows.append(ppp_elem.pk)
            for row in req_rows:
                pp_arr.append(row)
        p_arr.append(pp_arr)
        pm_req_lst.append(p_arr)
        p_arr = []
        pp_arr = []
    obj_lst_arr = []

    # cur.execute(
    #     "SELECT ID, TypeName FROM tbl_type ")
    # type_rows = cur.fetchall()
    type_rows = WellType.objects.all().order_by('id')

    for elem in pm_req_lst:
        pp_arr = []
        p_arr = []
        ppp_arr = []
        summ_arr = []
#                 # print('PG GROUP: ', elem[0])
        p_arr.append(elem[0])
        if len(elem[1]) == 0:
            for p_elem in type_rows:
                pp_arr.append(0)
            p_arr.append(pp_arr)
        else:
            for p_elem in elem[1]:
                ppp_arr = []
                for pp_elem in type_rows:

                    data = 0
                    # cur.execute(
                    #     "SELECT w_value FROM tbl_appl_data WHERE applID = (" + str(
                    #         p_elem) + ") AND typeID = (" + str(pp_elem[0]) + ")")
                    # req_data_rows = cur.fetchall()
                    p_req_data_rows = Appl_mpz_data.objects.all().order_by('id')
                    req_data_rows = []

                    for p_req_elem in p_req_data_rows:
                        if (str(p_req_elem.applID_id) == str(p_elem)) and (str(p_req_elem.typeID_id) == str(pp_elem.pk)):
                            req_data_rows.append(p_req_elem.w_value)
                    if len(req_data_rows) == 0:
                        data = 0
                    else:
                        for row in req_data_rows:
                            data = int(row)
                    ppp_arr.append(data)
                pp_arr.append(ppp_arr)
            ppp_arr = []
            i = 0
            j = 0
            ppp_arr = []
            for i in range(len(pp_arr[0])):
                count = 0
                for j in range(len(pp_arr)):
                    count = count + pp_arr[j][i]
                ppp_arr.append(count)
            p_arr.append(ppp_arr)
        obj_lst_arr.append(p_arr)

    #PG DATA LST DONE
    #GET OTHER DAT LST
    pp_arr = []
    for elem in type_rows:
        p_arr= []
        data = 0
        # cur.execute(
        #     "SELECT w_value FROM tbl_buyers_appl_data WHERE typeID = (" + str(
        #         elem[0]) + ")")
        # buyers_appl_data_rows = cur.fetchall()
        buyers_appl_data_rows = []
        p_buyers_appl_data_rows = Appl_by_data.objects.all().order_by('id')
        for p_buy_data_elem in p_buyers_appl_data_rows:
            if p_buy_data_elem.typeID_id == elem.pk:
                buyers_appl_data_rows.append(p_buy_data_elem.w_value)
        if len(buyers_appl_data_rows) == 0:
            data = 0
        else:
            for row in buyers_appl_data_rows:
                data = data + int(row)
        pp_arr.append(data)
    other_ind = len(obj_lst_arr) + 1
    p_arr.append(other_ind)
    p_arr.append(pp_arr)
    obj_lst_arr.append(p_arr)

    #PG+OTHER DATA ARR DONE
    #GET RES PG+OTHER DATA

    i = 0
    j = 0
    p_arr = []
    pp_arr = []
    for i in range(len(obj_lst_arr[0][1])):
        data = 0
        j = 0
        for j in range(len(obj_lst_arr)):
            elem = obj_lst_arr[j][1]
            data = data + int(elem[i])
        pp_arr.append(data)
    p_arr = []
    summ_ind = other_ind + 1
    p_arr.append(summ_ind)
    p_arr.append(pp_arr)
    obj_lst_arr.append(p_arr)
    return obj_lst_arr

def getReleaseDataArray():
    #GET RELEASE DATA ARRAY
    #GET PM DATA ARRAY

    release_data_arr = []
    pm_arr = []

    # cur.execute("SELECT ID FROM tbl_manager")
    # pm_rows = cur.fetchall()
    pm_rows = ProjectGroup.objects.all().order_by('id')
    type_rows = WellType.objects.all().order_by('id')

    for row in pm_rows:
        p_arr = []
        pp_arr = []
        p_arr.append(row.pk)
        codes_names_rows = []
        p_code_names_rows = Code.objects.all().order_by('id')
        for p_code_name_elem in p_code_names_rows:
            if p_code_name_elem.connect_id == row.pk:
                codes_names_rows.append(p_code_name_elem.code_name)

        for p_row in codes_names_rows:
            pp_arr.append(p_row)
        p_arr.append(pp_arr)
        pm_arr.append(p_arr)
    p_arr = []
    pp_arr = []
    ppp_arr = []
    for elem in pm_arr:
        codes = elem[1]
        for type in type_rows:
            p_type = 'С-пласт '
            count = 0
            for p_elem in codes:
                p_type = type.type_name
                well_rows = []
                p_well_rows = Well.objects.all().order_by('id')
                for p_well_elem in p_well_rows:
                    if (p_well_elem.type == p_type and p_well_elem.locate == p_elem):
                        well_rows.append(p_well_elem.pk)
                count = count + len(well_rows)
            ppp_arr.append(count)
        pp_arr.append(elem[0])
        pp_arr.append(ppp_arr)
        p_arr.append(pp_arr)
        pp_arr = []
        ppp_arr = []
    release_data_arr = p_arr

    #PM DATA ARRAY DONE
    #GET OTHER DATA ARR
    buyers_rows = Byer.objects.all().order_by('id')
    pp_arr = []
    p_arr = []
    for type in type_rows:
        p_type = type.type_name
        count = 0
        for buyer in buyers_rows:
            well_rows = []
            p_well_rows = Well.objects.all().order_by('id')
            for p_well_elem in p_well_rows:
                if (p_well_elem.type == p_type) and (p_well_elem.locate == buyer.by_name):
                    well_rows.append(p_well_elem.pk)
            count = count + len(well_rows)
        pp_arr.append(count)

    other_ind = len(release_data_arr) + 1
    p_arr.append(other_ind)
    p_arr.append(pp_arr)
    release_data_arr.append(p_arr)

    #OTHER DATA APPEND TO RELEASE ARR
    #GET SUMM DATA AND APPEND TO RELEASE DATA ARR
    i = 0
    j = 0
    p_arr = []
    pp_arr = []
    for i in range(len(release_data_arr[0][1])):
        data = 0
        j = 0
        for j in range(len(release_data_arr)):
            elem = release_data_arr[j][1]
            data = data + int(elem[i])
        pp_arr.append(data)
    p_arr = []
    summ_ind = other_ind + 1
    p_arr.append(summ_ind)
    p_arr.append(pp_arr)
    release_data_arr.append(p_arr)
    return release_data_arr

def getDeltaDataArr(in_req_data_array, release_data_array):
    delta_data_arr = []
    i = 0
    j = 0
    p_arr = []
    pp_arr = []
    ppp_arr = []
    for i in range(len(in_req_data_array)):
        data = 0
        pp_arr = []
        ppp_arr = []
        j = 0
        elem = in_req_data_array[0][1]
        for j in range(len(elem)):
            elem_in_req = in_req_data_array[i][1]
            elem_release = release_data_array[i][1]
            data_in_req = elem_in_req[j]
            data_release = elem_release[j]
            data = data_in_req - data_release
            ppp_arr.append(data)
        pp_arr.append(in_req_data_array[i][0])
        pp_arr.append(ppp_arr)
        p_arr.append(pp_arr)
        delta_data_arr = p_arr
        delta_data_array = delta_data_arr
    return delta_data_arr

def getTransferColorArray(head_arr):
    print('LEN HEAD ARR: ', head_arr)
    i = 0
    ch_count = 0
    p_color_arr = []
    p_arr = []
    check = "0"
    p_color_arr.append(check)
    for i in range((len(head_arr))):
        if i > 0:
            if check == "1":
                check = "0"
            else:
                check = "1"
            p_color_arr.append(check)
            p_color_arr.append(check)
            p_color_arr.append(check)
    release_color_arr = p_color_arr
    print("TRANSFER COLOR LEN: ", release_color_arr.__len__())
    print("TRANSFER COLOR LEN: ", release_color_arr)
    return release_color_arr

#----------------------------------------------DB TRANSFER--------------------------------------------------------------

def pullMySqlBase(SqlHostname, SqlPort, SqlUserName, SqlPwd, SqlDBName):
    con = pymysql.connect(host=SqlHostname,
                          port=SqlPort,
                          user=SqlUserName,
                          passwd=SqlPwd,
                          db=SqlDBName)
    with con:
        data = con.cursor()
        data.execute("SELECT * FROM tbl_main")
        data_rows = data.fetchall()
    return data_rows

def pushPostgreSqlServer(data):
    for elem in data:
        if elem[5] != None:
            comment = elem[5]
        else:
            comment = ''
        if elem[6] != None:
            req_num = elem[6]
        else:
            req_num = ''
        if elem[7] != None:
            trans_date = elem[7]
        else:
            trans_date = ''
        print(elem)
        release_date_arr = str(elem[3]).split('.')
        well = Well()
        well.serial = elem[1]
        well.type = (str(elem[2]).split(' '))[1]
        well.created_date = release_date_arr[2] + '-' + release_date_arr[1] + '-' + release_date_arr[0]
        well.locate = elem[4]
        well.comment = comment
        well.req_num = req_num
        well.trans_date = trans_date
        well.release()
