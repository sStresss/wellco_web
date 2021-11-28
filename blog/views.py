from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Well, WellType, Warehouse, var, ProjectGroup, Code, Appl_mpz, Appl_mpz_data, Byer, Appl_byer, Appl_by_data
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
import json

def post_list(request):
    #get well list
    wells = Well.objects.all().order_by('id')
    # print('WELLS: ', wells)
    wells = wells.reverse()
    serial = '0'
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

            cur_date = datetime.datetime.now()

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
            print('prepeare trans modal data init!')
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
            print('json res: ', json_res)
            return JsonResponse(json_res, content_type='application/json')
        if req.find('modal') != -1:
            cur_serial = var.objects.all().order_by('id')
            for elem in cur_serial:
                last_part_month = elem.month
                last_part_num = elem.part_num

            cur_date = datetime.datetime.now()

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
            print('JSON RES: ',json_res)

            return JsonResponse(json_res, content_type='application/json')
        if req.find('transfer_well') != -1:
            trans_type = p_arr[1]
            trans_date = p_arr[2]
            trans_target = p_arr[3]
            trans_subtarget = p_arr[4]
            serial_lst = str(p_arr[5]).split('%')
            if trans_type == 'transfer':
                print('TRANSFER!')
                trans_comment = 'перемещен ' + trans_date + ' числа на объект ' + trans_target + ' по заявке МПЗ№' + trans_subtarget
            else:
                print('SELLING!')
                trans_comment = 'продан ' + trans_date + ' числа организации ' + trans_target + ' по заявке №' + trans_subtarget
            for elem in serial_lst:
                record = Well.objects.get(serial=elem)
                record.comment = trans_comment
                record.locate = trans_target
                record.req_num = trans_subtarget
                record.trans_date = trans_date
                record.save(update_fields=['comment', 'locate', 'req_num', 'trans_date'])
                print('done')
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('m29_get_data') != -1:
            res_arr = []
            temp_p_arr = []
            pp_arr = []
            range_start = '28.10.2021'
            range_end = '28.11.2021'
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

                    if row.trans_date != None:
                        trans_date = str(row.trans_date)
                        date_arr = trans_date.split('.')
                        p_trans_date = datetime.date(datetime.now())
                        trans_date = p_trans_date.replace(int(date_arr[2]), int(date_arr[1]), int(date_arr[0]))

                    if (rel_date < range_start and row.trans_date == None) or (
                            rel_date < range_start and range_start <= trans_date):
                        check_start = True
                    else:
                        check_start = False

                    if (rel_date <= range_end and row.trans_date == None) or (
                            rel_date <= range_end and range_end < trans_date):
                        check_end = True
                    else:
                        check_end = False

                    if (rel_date >= range_start) and (rel_date <= range_end):
                        check_input = True
                    else:
                        check_input = False

                    if row.trans_date != None:
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
            # i = 0
            # for elem in res_arr:
            #     data[i] = elem
            #     json_data = json.dumps(data)
            #     i+=1
            data[0] = res_arr
            json_data = json.dumps(data)
            json_res = json.loads(json_data)
            print('json res: ', json_res)
            return JsonResponse(json_res, content_type='application/json')
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
            print(len(first_code_mpz_lst))
            first_code_mpz_lst_first_elem = first_code_mpz_lst[0]

            return render(request, 'blog/post_list.html', {'wells': wells, 'types': types, 'type_first_elem': type_first_elem, 'wh_lst': wh_lst, 'wh_first_elem': wh_first_elem, 'code_lst': code_lst, 'code_first_elem': code_first_elem, 'first_code_mpz_lst': first_code_mpz_lst, 'first_code_mpz_lst_first_elem': first_code_mpz_lst_first_elem})

def structure(request):
    if request.method == "GET":
        req = str(request.GET)
        req_dict = request.GET.dict()
        print(req_dict)
        p_arr = []
        for elem in req_dict.items():
            p_arr.append(elem[1])
        if req.find('new_pg') != -1:
            ProjectGroup.objects.create(pg_name=p_arr[1])
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('new_code') != -1:
            Code.objects.create(code_name= p_arr[1], connect_id=p_arr[2])
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        if req.find('new_mpz') != -1:
            Appl_mpz.objects.create(mpz_appl_name=p_arr[1], connect_id=p_arr[2])
            data = {'result': str('success')}
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
            print('EDIT MPZ: ', p_arr)
            appl_data_arr = Appl_mpz_data.objects.all().order_by('id')
            cur_id = -1
            for elem in appl_data_arr:
                print('elem: ', elem)
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

            # print('well lst data: ', well_lst)
            data = {}
            arr = []
            p_arr = []
            for type in types:
                value = 0

                for well in well_lst:
                    if str(well.applID) == str(appl_cur_id) and str(well.typeID) == str(type.id):
                        value = int(well.w_value)
                p_arr.append(value)
            for i in range(len(types)):
                pp_arr = []
                pp_arr.append(str(types[i]))
                pp_arr.append(str(p_arr[i]))
                data[i] = pp_arr
                json_data = json.dumps(data)
            json_res = json.loads(json_data)
            print('JSON RES: ', json_res)

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
            Byer.objects.create(by_name=p_arr[1])
            buyers = Byer.objects.all().order_by('id')
            print('BY LEN: ',buyers.__len__())
            json_res = {'by_par_len' : buyers.__len__()}
            return JsonResponse(json_res, content_type='application/json')
        if req.find('del_by') != -1:
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
            for by in buyers_lst:
                if by.by_name == p_arr[2]:
                    cur_by_id = by.id
            app_lst = Appl_byer.objects.order_by('id')
            for app in app_lst:
                if app.by_appl_name == p_arr[1] and app.connect_id == cur_by_id:
                    cur_app_id = app.id
            print('GET BY APP DATA')
            print('BY ID: ', cur_by_id)
            print('AP ID: ', cur_app_id)
            app_data_lst = Appl_by_data.objects.order_by('id')
            types_lst = WellType.objects.order_by('id')
            p_arr = []
            for type in types_lst:
                value = 0
                for p_data in app_data_lst:
                    if p_data.applID_id == cur_app_id and p_data.byID_id == cur_by_id and p_data.typeID_id == type.id:
                        value = p_data.w_value
                p_arr.append(value)
            data = {}
            for i in range(len(types_lst)):
                pp_arr = []
                pp_arr.append(str(types_lst[i]))
                pp_arr.append(str(p_arr[i]))
                data[i] = pp_arr
                json_data = json.dumps(data)
            json_res = json.loads(json_data)
            print(json_res)
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
                print('elem: ', elem)
                if elem.applID == cur_app_id and elem.typeID == well_type_id and elem.parID == cur_by_id:
                    cur_id = elem.id
            if cur_id == -1:
                Appl_by_data.objects.create(applID_id=cur_app_id, byID_id=cur_by_id, typeID_id=well_type_id, w_value=new_val)
            else:
                record = Appl_by_data.objects.get(id=cur_id)
                record.w_value = new_val
                record.save(update_fields=['w_value'])
            print('EDIT BYAPP: ', p_arr)
            data = {'result': str('success')}
            return JsonResponse(data, content_type='application/json')
        else:
            pg_dict = ProjectGroup.objects.all().order_by('id')
            code_dict = Code.objects.all().order_by('id')
            mpz_dict = Appl_mpz.objects.all().order_by('id')
            types = WellType.objects.all().order_by('id')

            return render(request, 'blog/structure.html', {'pg_lst': pg_dict, 'code_lst': code_dict, 'mpz_lst': mpz_dict, 'types': types})




