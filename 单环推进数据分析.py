# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from base.server_connect import *

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class NewDataDownloader(DataDownloader):
    def return_single_ring_tunneling_data(self, ring, var_list):
        var_code_pd = pd.read_csv(f'../conf/var_code_{self.tunnel_code}.csv', encoding='gbk')
        table_name = server_conf['ShieldDataCloudServer']['table_realtime'] + self.tunnel_table_name
        var_sql = ''
        for var_name in var_list:
            try:
                var_code = var_code_pd[var_code_pd['VarName'] == var_name].iloc[0, 1]
                var_sql += f',{var_code} as "{var_name}" '
            except:
                print(f"{var_name}不在数据表中")
                return KeyError
        sql = f'select\
                realtime as "时间"\
                ,U0X01 as "环号"\
                ,U0X03 as "净行程"\
                {var_sql}\
                from {table_name}\
                where \
                CBA01 > 0\
                and \
                U0X01 = {ring}\
                ORDER BY realtime'
        data = DataCaptur(ShieldDataCloudConnection()).return_pandas_data(sql)
        max_distance = max(data.净行程)
        data = data[data['净行程'] < max_distance - 10]
        return data

    def return_ring_avg_tunneling_data(self, project_name, min_ring, max_ring, var_list):
        var_code_pd = pd.read_csv(f'../base/var_code_{project_name}.csv', encodings='gbk')
        table_name = server_conf['ShieldDataCloudServer']['table_distance'] + project_conf[project_name][
            'tunnel_table_name']
        var_sql = ''
        for var_name in var_list:
            var_code = var_code_pd[var_code_pd['VarName'] == var_name].iloc[0, 1]
            var_sql += f',avg({var_code}) as "{var_name}" '
        sql = f'select\
                min(realtime) as "起推时间"\
                ,U0X01 as "环号"\
                {var_sql}\
                from {table_name}\
                where \
                CBA01 > 0\
                and \
                TBA08 > 0\
                and \
                U0X01 >= {min_ring}\
                and \
                U0X01 <= {max_ring}\
                GROUP BY U0X01\
                ORDER BY realtime'
        data = DataCaptur(ShieldDataCloudConnection()).return_pandas_data(sql)
        return data


def plot_sigle_ring_figer(data, base_data_num: int = 3, y_label_index=2):
    data
    figsize_y = (data.shape[1] - base_data_num) * 3
    figsize_x = 15
    ring_num = data['环号'][0]
    plot_num = data.shape[1] - base_data_num
    fig, axs = plt.subplots(plot_num, 1, sharex=True, figsize=(figsize_x, figsize_y))
    plt.suptitle(f'第{ring_num}环', fontsize=25, x=0.01, y=0.98, ha='left')
    x_label_name = data.iloc[:, y_label_index]
    calibration = int(data.shape[0]/10)
    x_ticks = []
    label_name = []
    for i in range(11):
        x_ticks.append(calibration*i)
        label_name.append(x_label_name[calibration*i])

    x_label = pd.Series(np.arange(data.shape[0]),name = 'index')
    plt.xticks(x_ticks,label_name)
    for i in range(plot_num):
        sub_data = data.iloc[:, i + base_data_num]
        axs[i].plot(x_label, sub_data)
        axs[i].set_ylabel(sub_data.name)
    plt.subplots_adjust(hspace=0)
    plt.xlabel(x_label_name.name)
    plt.show()
    return


if __name__ == "__main__":
    data_loader = NewDataDownloader("5-2-4")
    para_list = ['刀盘扭矩','推进速度上','推进速度给定','螺旋机闸门开度', '螺旋机转速给定','螺旋机扭矩','正面土压力上']
    for i in range(597,598):
        ring_data = data_loader.return_single_ring_tunneling_data(i,para_list)
        plot_sigle_ring_figer(ring_data)
