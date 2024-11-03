import calendar
from datetime import datetime, timedelta
from zhdate import ZhDate
from colorama import init, Fore, Style
import ephem  # 需要先安装：pip install ephem

def get_solar_term_date(year, month, day):
    """计算指定年月日的节气"""
    # 节气列表，包含名称和对应的黄经度数
    solar_terms = [
        (315, '立春'), (330, '雨水'), (345, '惊蛰'), (0, '春分'),
        (15, '清明'), (30, '谷雨'), (45, '立夏'), (60, '小满'),
        (75, '芒种'), (90, '夏至'), (105, '小暑'), (120, '大暑'),
        (135, '立秋'), (150, '处暑'), (165, '白露'), (180, '秋分'),
        (195, '寒露'), (210, '霜降'), (225, '立冬'), (240, '小雪'),
        (255, '大雪'), (270, '冬至'), (285, '小寒'), (300, '大寒')
    ]
    
    # 计算太阳黄经
    sun = ephem.Sun()
    date = ephem.Date(datetime(year, month, day))
    sun.compute(date)
    
    # 将弧度转换为角度
    sun_long = sun.hlong * 180.0 / ephem.pi
    
    # 寻找最近的节气
    for degrees, term_name in solar_terms:
        if degrees > sun_long:
            next_term = (degrees, term_name)
            prev_idx = (solar_terms.index((degrees, term_name)) - 1) % 24
            prev_term = solar_terms[prev_idx]
            return prev_term[1], next_term[1]
    
    return solar_terms[-1][1], solar_terms[0][1]

def get_solar_term_dates(year, month, day):
    """获取上一个和下一个节气的具体日期"""
    # 定义2024年的节气日期（可以按年份扩展）
    solar_terms_2024 = [
        ('小寒', 1, 6), ('大寒', 1, 21), ('立春', 2, 4), ('雨水', 2, 19),
        ('惊蛰', 3, 5), ('春分', 3, 20), ('清明', 4, 4), ('谷雨', 4, 19),
        ('立夏', 5, 5), ('小满', 5, 20), ('芒种', 6, 5), ('夏至', 6, 21),
        ('小暑', 7, 7), ('大暑', 7, 22), ('立秋', 8, 7), ('处暑', 8, 23),
        ('白露', 9, 7), ('秋分', 9, 22), ('寒露', 10, 8), ('霜降', 10, 23),
        ('立冬', 11, 7), ('小雪', 11, 22), ('大雪', 12, 7), ('冬至', 12, 21)
    ]
    
    current_date = datetime(year, month, day)
    
    # 转换节气日期为datetime对象
    term_dates = []
    for term, m, d in solar_terms_2024:
        term_dates.append((term, datetime(year, m, d)))
    
    # 找到最近的上一个和下一个节气
    prev_term = None
    next_term = None
    prev_days = None
    next_days = None
    
    for i, (term, date) in enumerate(term_dates):
        if date.date() <= current_date.date():
            prev_term = term
            prev_days = (current_date.date() - date.date()).days
        elif date.date() > current_date.date():
            next_term = term
            next_days = (date.date() - current_date.date()).days
            break
    
    # 处理年末年初的特殊情况
    if not prev_term:
        # 如果没有找到上一个节气，说明是年初，需要查看上一年的冬至
        last_year_dongzhi = datetime(year-1, 12, 21)
        prev_term = '冬至'
        prev_days = (current_date.date() - last_year_dongzhi.date()).days
    
    if not next_term:
        # 如果没有找到下一个节气，说明是年末，需要查看下一年的小寒
        next_year_xiaohan = datetime(year+1, 1, 6)
        next_term = '小寒'
        next_days = (next_year_xiaohan.date() - current_date.date()).days
    
    return prev_term, prev_days, next_term, next_days

def show_calendar():
    # 初始化 colorama
    init()
    
    # 设置中文显示
    calendar.setfirstweekday(calendar.SUNDAY)
    months = ['一月', '二月', '三月', '四月', '五月', '六月',
              '七月', '八月', '九月', '十月', '十一月', '十二月']
    weekdays = ['日', '一', '二', '三', '四', '五', '六']
    
    # 获取当前时间
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    
    # 生成日历
    cal = calendar.monthcalendar(year, month)
    
    # 显示标题，使用居中对齐
    calendar_width = 25
    title = f"{year}年{months[month-1]}"

    print(f"\n{title:^{calendar_width}}\n")
    
    # 修改星期显示，使用蓝色
    weekday_line = ' '.join(f'{Fore.BLUE}{d:>2}{Style.RESET_ALL}' for d in weekdays)
    print(weekday_line)
    
    # 修改日期显示的格式，当前日期红色，其他日期蓝色
    for week in cal:
        line = ' '.join(f'{Fore.RED}{d:>3}{Style.RESET_ALL}' if d == day 
                       else f'{Fore.BLUE}{d:>3}{Style.RESET_ALL}' if d != 0 
                       else '   ' for d in week)
        print(line)
    
    # 显示农历信息
    lunar_date = ZhDate.from_datetime(now)
    
    def get_gz_year(year):
        heavenly_stems = '甲乙丙丁戊己庚辛壬癸'
        earthly_branches = '子丑寅卯辰巳午未申酉戌亥'
        return heavenly_stems[(year - 4) % 10] + earthly_branches[(year - 4) % 12]

    # 获取农历年月日
    lunar_year = get_gz_year(lunar_date.lunar_year)
    lunar_month = lunar_date.lunar_month
    lunar_day = lunar_date.lunar_day
    
    # 添加生肖
    zodiac = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    zodiac_year = (lunar_date.lunar_year - 4) % 12
    
    # 将数字转换为中文
    lunar_month_names = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
    lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                      '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                      '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
    
    # 获取当前节气和上下节气
    prev_term, prev_days, next_term, next_days = get_solar_term_dates(year, month, day)
    
    # 修改农历信息显示，添加颜色和节气
    lunar_info = (
        f"{Fore.GREEN}{lunar_year}{Style.RESET_ALL}"
        f"({Fore.YELLOW}{zodiac[zodiac_year]}{Style.RESET_ALL})年 "
        f"{Fore.GREEN}{lunar_month_names[lunar_month-1]}月{lunar_day_names[lunar_day-1]}{Style.RESET_ALL}"
    )
    
    print("\n")
    print(f"{lunar_info:^{calendar_width+20}}")  # 增加宽度以确保居中
    
    # 显示上一个节气信息
    if prev_term:
        print(f"{Fore.CYAN}上一节气：{prev_term} (已过{prev_days}天){Style.RESET_ALL}".center(calendar_width))
    
    # 显示下一个节气信息
    if next_term:
        print(f"{Fore.CYAN}下一节气：{next_term} (还有{next_days}天){Style.RESET_ALL}".center(calendar_width))

if __name__ == "__main__":
    show_calendar()