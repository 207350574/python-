import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button
import requests
from datetime import datetime
import json
import mysql.connector
import os

# 天气描述的中英文映射
weather_mapping = {
    'clear sky': '晴天',
    'few clouds': '少云',
    'scattered clouds': '晴转多云',
    'broken clouds': '多云',
    'shower rain': '阵雨',
    'rain': '雨',
    'thunderstorm': '雷阵雨',
    'snow': '雪',
    'light snow':'小雪',
    'moderate snow':'中雪',
    'heavy snow':'大雪',
    'blizzard':'暴雪',
    'mist': '薄雾',
    'smoke': '烟雾',
    'haze': '阴霾',
    'dust': '沙尘',
    'fog': '雾',
    'sand': '沙尘',
    'ash': '火山灰',
    'squall': '狂风',
    'tornado': '龙卷风',
    'overcast clouds': '阴天'
}
# 读取城市中英文对照JSON文件
with open('city_mapping.json', 'r', encoding='utf-8') as f:
    city_mapping = json.load(f)
def get_weather_data(api_key, city):
    # 将中文城市名称转换为英文城市名称
    city = city_mapping.get(city, city)
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'appid': api_key,
        'q': city,
        'units': 'metric'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return data
    except requests.RequestException as e:
        messagebox.showerror("错误", f"请求失败: {e}")
        return None

def get_clothing_suggestion(temperature):
    if temperature < 10:
        return "建议穿着厚外套、毛衣、围巾和手套。"
    elif temperature < 20:
        return "建议穿着长袖衬衫、薄外套和长裤。"
    else:
        return "建议穿着短袖、短裤或短裙。"

def translate_weather_description(description):
    return weather_mapping.get(description, description)  # 如果没有找到映射，返回原始描述
# 历史查询记录列表
history = []
def display_weather():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("警告", "请输入城市名称。")
        return
    
    data = get_weather_data(API_KEY, city)
    if data:
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 将天气描述翻译成中文
        chinese_weather_description = translate_weather_description(weather_description)
        
        weather_label.config(text=f"天气: {chinese_weather_description}")
        temperature_label.config(text=f"温度: {temperature}°C")
        time_label.config(text=f"时间: {current_time}")
        clothing_label.config(text=f"穿搭建议: {get_clothing_suggestion(temperature)}")
        # 将查询添加到历史记录中
        if len(history) >= 5:
            history.pop(0)  # 如果历史记录超过5个，移除最早的记录
        history.append({
            'city': city,
            'temperature': temperature,
            'weather': chinese_weather_description,
            'time': current_time
        })
def display_history():
    if not history:
        messagebox.showinfo("历史记录", "没有历史查询记录。")
        return
    
    history_text = ""
    for record in history:
        history_text += f"城市: {record['city']}\n"
        history_text += f"温度: {record['temperature']}°C\n"
        history_text += f"天气: {record['weather']}\n"
        history_text += f"时间: {record['time']}\n\n"
    
    messagebox.showinfo("历史记录", history_text)
def login():
    username = username_entry.get()
    password = password_entry.get()
    # 连接到MySQL数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="users"
    )
    
    # 创建一个游标对象
    mycursor = mydb.cursor()
    
    # 查询用户表以验证用户名和密码
    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    val = (username, password)
    
    try:
        # 执行SQL查询
        mycursor.execute(sql, val)
        # 获取查询结果
        result = mycursor.fetchone()
        if result:
            messagebox.showinfo("登录成功", "欢迎回来！")
            root.deiconify()  # 显示主窗口
            login_window.destroy()  # 关闭登录窗口
        else:
            messagebox.showerror("登录失败", "用户名或密码错误。")
    except mysql.connector.Error as err:
        messagebox.showerror("错误", f"登录失败: {err}")
    finally:
        # 关闭游标和数据库连接
        mycursor.close()
        mydb.close()
def register():
    username = username_entry.get()
    password = password_entry.get()

    # 检查用户名和密码是否为空
    if not username or not password:
        messagebox.showwarning("警告", "用户名和密码不能为空。")
        return
    #连接到MySQL数据库
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="users"
    )
    
    # 创建一个游标对象
    mycursor = mydb.cursor()
    
    # 插入数据的SQL语句
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    val = (username, password)
    
    try:
        # 执行SQL语句
        mycursor.execute(sql, val)
        # 提交事务
        mydb.commit()
        messagebox.showinfo("注册成功", "注册成功！请登录。")
    except mysql.connector.Error as err:
        # 如果发生错误，回滚事务
        mydb.rollback()
        messagebox.showerror("注册失败", f"注册失败: {err}")
    finally:
        # 关闭游标和数据库连接
        mycursor.close()
        mydb.close()
# 创建主窗口
root = tk.Tk()
root.title("天气查询系统")
root.geometry("400x350")
root.withdraw()  # 隐藏主窗口
# 创建登录窗口
login_window = tk.Toplevel()
login_window.title("登录")
login_window.geometry("300x250")
login_window.configure(bg="lightgray")  # 设置窗口背景颜色为浅灰色
# 创建用户名和密码输入框
username_label = tk.Label(login_window, text="用户名:", bg="lightgray", font=("Arial", 12))
username_label.pack(pady=5)
username_entry = tk.Entry(login_window, font=("Arial", 12))
username_entry.pack(pady=5)

password_label = tk.Label(login_window, text="密码:", bg="lightgray", font=("Arial", 12))
password_label.pack(pady=5)
password_entry = tk.Entry(login_window, show="*", font=("Arial", 12))
password_entry.pack(pady=5)

# 创建登录和注册按钮
login_button = tk.Button(login_window, text="登录", command=login, bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", borderwidth=3)
login_button.pack(pady=10)

register_button = tk.Button(login_window, text="注册", command=register, bg="#2196F3", fg="white", font=("Arial", 12), relief="raised", borderwidth=3)
register_button.pack(pady=10)
# 创建API密钥
API_KEY = "8bf1a172d8b9db10a148729a2ba4ca3a"  # 替换为你的OpenWeatherMap API密钥

# 创建城市输入框
city_entry = tk.Entry(root, width=30)
city_entry.grid(row=0, column=0, padx=10, pady=10)

# 创建查询按钮
query_button = tk.Button(root, text="查询", command=display_weather, bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised", borderwidth=3)
query_button.grid(row=1, column=0, padx=10, pady=10)

# 创建历史查询按钮
history_button = tk.Button(root, text="历史查询", command=display_history, bg="#2196F3", fg="white", font=("Arial", 12), relief="raised", borderwidth=3)
history_button.grid(row=1, column=1, padx=10, pady=10)

# 创建天气显示标签
weather_label = tk.Label(root, text="天气: ")
weather_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

# 创建温度显示标签
temperature_label = tk.Label(root, text="温度: ")
temperature_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

# 创建时间显示标签
time_label = tk.Label(root, text="时间: ")
time_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)

# 创建穿搭建议显示标签
clothing_label = tk.Label(root, text="穿搭建议: ")
clothing_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

# 运行主循环
root.mainloop()