import os
import pandas as pd


class AppExc(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


ExcDict = {'TooManyFiles': 'Too many files in current folder',
           'WithoutTxtFiles': 'files with ".txt" extension not found',
           'FlipValues': 'Время окончания должно быть больше времени начала'}
for exc, mess in ExcDict.items():
    ExcDict[exc] = (type(exc, (Exception, ), {})(mess))


class PandasExceptions(Exception):
    pass


path = 'C:/Users/Kirill/Desktop/Test_export'
os.chdir(path)
writer = pd.ExcelWriter('test.xlsx')

def slash_reflector(file_name):
    true_file_name = file_name.replace('\\', '/')
    return true_file_name


def check_txt_ext(file_list):
    if len(file_list) < 60:  # Настроить предельное количество файлов
        bool_storage = False
        # must be while with condition (not bool_storage and i < len(file_list))
        for file in file_list:
            bool_storage = bool_storage or '.txt' in file
        if not bool_storage:
            raise ExcDict['WithoutTxtFiles']
    else:
        raise ExcDict['TooManyFiles']


def add_txt(file_list, path):
    path = slash_reflector(path)
    slash = ''
    if path[-1] != '/':
        slash = '/'
    output_list = []
    for file in file_list:
        if '.txt' in file:
            file = path + slash + file
            output_list.append(file)
    return output_list


def check_of_adding():
    while True:
        stop_continue = str(input("Do you want add more files? y/n: \n"))
        if stop_continue.lower() == 'y':
            return False
        elif stop_continue.lower() == 'n':
            return True
        else:
            print("You must enter 'y' or 'n'")


def data_length_checker(data):
    if len(data) == 0:
        print('No relevant data')
        return False
    else:
        return True


def define_time():
    while True:
        try:
            print('Установите временной интервал для анализа данных в мс.')
            # start = int(input('Время начала: '))
            # stop = int(input('Время окончания: '))
            start = 0
            stop = 3000
            if stop < start:
                raise ExcDict['FlipValues']
        except ValueError:
            print('Введите целочисленные данные')
        except Exception as e:
            print(e)
        else:
            break

    def time_int():
        return start, stop

    return time_int


def time_check_up_decorator(start_time, end_time):
    def decorator(func):
        def wrapped(file):
            try:
                data = func(file)
            except Exception:
                raise PandasExceptions(f'Invalid data format for: {file}')
            else:
                header = 'Export Start Trial Time [ms]'
                if data.loc[data.loc[:, header].idxmax(), header] != start_time:
                    print(f'Указанное значение начала интервала анализа данных'
                          f' в файле {file}'
                          f' не соответвует указанному пользователем')
                    return False
                header = 'Export End Trial Time [ms]'
                if data.loc[data.loc[:, header].idxmax(), header] != end_time:
                    print(f'Указанное значение конца интервала анализа данных'
                          f' в файле {file}'
                          f' не соответвует указанному пользователем')
                    return False
                print(data)
                return True
        return wrapped
    return decorator


def binding_with_time(file_list, start_time, stop_time, *args):
    output_file_list = []
    slash = ''
    path = ''

    @time_check_up_decorator(start_time, stop_time)
    def open_csv(data_file):
        return pd.read_csv(data_file, sep='\t')

    # must be try-except:
    if len(args) > 0:
        path = slash_reflector(args[0])
        if path[-1] != '/':
            slash = '/'
    for file in file_list:
        trigger = False
        if '.txt' in file:
            try:
                trigger = open_csv(file)
            except PandasExceptions as e:
                print(e)
        if trigger:
            file = path + slash + file
            output_file_list.append(file)
    return output_file_list


def input_console_data(time):
    data = []
    start_time, stop_time = time()
    while True:
        print("Specify the full path to the data folder")
        print("Example 'X:/Users/MySMIexportFolder': ")
        # path = str(input())
        path = 'C:/Users/Kirill/Desktop/Test_export'
        try:
            os.chdir(path)
            check_txt_ext(os.listdir('.'))
            relevant_files = binding_with_time(os.listdir('.'), start_time, stop_time, path)
        except FileNotFoundError:
            print('Folder not exist')
        except Exception as e:
            print(e)
        else:
            data += relevant_files
            # data += add_txt(os.listdir('.'), path)
        finally:
            if check_of_adding() and data_length_checker(data):
                break
    return data


def file_list_console_output():
    time = define_time()
    data = set()
    for file in input_console_data(time):
        data.add(file)
    return tuple(data), time


def open_csv(file):
    return pd.read_csv(file, sep='\t')


def add_suff(trial):
    suffix = ''
    trial_suffix = {2: '_M_NF', 4: '_M_HF_f', 10: '_M_AF_f', 8: '_Self',
                    6: '_F_SF_f', 20: '_F_HF_f', 16: '_Self', 18: '_F_AF_f',
                    12: '_F_NF', 14: '_M_SF_f'}
    trnum = int(trial[-2:])
    if trnum in trial_suffix:
        suffix = trial_suffix[trnum]
    return suffix


def strings_df(data_frame, time):
    names = set()
    time = time()
    time = [str(t) for t in time]
    time.append('ms')
    time = '_'.join(time)
    dflist_vert = []
    dflist_hor = []
    trigger = False
    ln = data_frame.__len__()
    ln_aoi = len(data_frame.columns) - 7
    for i in range(ln):
        # С loc могут возникнуть проблемы iloc надёжнее
        par = data_frame.iloc[i, 4]
        if i != ln - 1:
            trigger = par != data_frame.iloc[i + 1, 4]
        if trigger or i == ln - 1:
            dflist_hor.append(pd.concat(dflist_vert, ignore_index=False, axis=1))
            dflist_vert.clear()
        if par not in names:
            names.add(par)
            # adding headers:
            dflist_vert.append(pd.DataFrame([par + '/headers', 'values'], columns=['']))
        aoi = data_frame.iloc[i, 6]
        visit = 'v' + str(data_frame.iloc[i, 5])
        for j in range(ln_aoi):
            val = data_frame.iloc[i, j + 7]
            var = data_frame.columns[j + 7].replace(' ', '_')
            one_var = pd.DataFrame(['_'.join([var, aoi, visit, time]), val], columns=[''])
            print(one_var)
            dflist_vert.append(one_var)
    # main body, significant operators
    # ignore_index ?:
    new_df = pd.concat(dflist_hor, axis=0)
    new_df.to_excel(writer, index=False)
    writer.save()


def main(file_list, time):
    ln = len(file_list)
    # Must be refactored for GUI version:
    print(f'Amount of relevant files: {ln}', file_list, '\n')
    dflist = []
    for f in file_list:
        dflist.append(open_csv(f))
    commondf = pd.concat(dflist, ignore_index=True)
    sort_order = ['Participant', 'visit', 'Trial', 'AOI Name']
    commondf.sort_values(by=sort_order, inplace=True)
    indices_for_drop = []
    tr = list(commondf.columns).index('Trial')
    aois = list(commondf.columns).index('AOI Name')
    for i in range(len(commondf.index)):
        # Какие то проблемы с индексацией loc по названию столбцов.
        # Значения с OUT почему-то пропускаются.
        trial = commondf.iloc[i, tr]
        aoi = commondf.iloc[i, aois]
        if int(trial[-1]) % 2 != 0 or 'OUT' in aoi:
            indices_for_drop.append(commondf.iloc[i].name)
        if 'Space' in aoi:
            aoi = 'nofeatures' + add_suff(trial)
            commondf.iloc[i, aois] = aoi
        if int(trial[-2:]) == 8:
            commondf.iloc[i, aois] = aoi + '_1'
        if int(trial[-2:]) == 16:
            commondf.iloc[i, aois] = aoi + '_2'
    for i in range(len(indices_for_drop)):
        commondf.drop(indices_for_drop[i], inplace=True)
    print(commondf.iloc[:, [0, 4, 5, 6]])
    strings_df(commondf, time)


if __name__ == "__main__":
    main(*file_list_console_output())
