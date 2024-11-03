# 中国农历日历显示器 (Chinese Lunar Calendar)

这是一个基于 Python 的终端日历显示程序，集成了公历、农历、节气等中国传统历法元素。

## 功能特点

- 📅 显示当月公历日历
- 🌙 显示当日农历日期
- 🐲 显示生肖年份
- 🌺 显示干支纪年
- 🌞 显示节气信息（上一个/下一个节气及间隔天数）
- 🎨 彩色终端显示支持

## 依赖项
```bash
pip install zhdate colorama ephem
```

## 主要组件

1. **日历显示** (`show_calendar`)
   - 以表格形式显示当月日历
   - 当前日期以红色高亮显示
   - 其他日期以蓝色显示

2. **农历转换** (`ZhDate`)
   - 支持公历转农历
   - 显示农历年月日
   - 显示干支纪年

3. **节气计算** (`get_solar_term_date`, `get_solar_term_dates`)
   - 计算并显示二十四节气
   - 显示距离上一个/下一个节气的天数

## 使用方法

直接运行 Python 文件即可：
```bash
python my_calendar.py
```


## 示例输出
![程序运行截图](./example.png)