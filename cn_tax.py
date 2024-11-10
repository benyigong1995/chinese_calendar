from dataclasses import dataclass
from typing import Dict
import colorama
from colorama import Fore, Style
from tabulate import tabulate

# 初始化colorama
colorama.init()

@dataclass
class TaxConstants:
    """税收相关常量"""
    YEAR = 2024
    
    # 个税起征点
    TAX_FREE_THRESHOLD = 5000
    
    # 个税税率表
    TAX_BRACKETS = [
        (0, 36000, 0.03),
        (36000, 144000, 0.10),
        (144000, 300000, 0.20),
        (300000, 420000, 0.25),
        (420000, 660000, 0.30),
        (660000, 960000, 0.35),
        (960000, float('inf'), 0.45)
    ]
    
    # 社保基数上下限（以北京为例）
    SOCIAL_INSURANCE_BASE_MIN = 3613
    SOCIAL_INSURANCE_BASE_MAX = 31884
    
    # 公积金基数上下限（以北京为例）
    HOUSING_FUND_BASE_MIN = 3613
    HOUSING_FUND_BASE_MAX = 31884
    
    # 完整社保费率（以北京为例）
    PENSION_RATE = 0.08      # 养老保险
    MEDICAL_RATE = 0.02      # 医疗保险 + 大病医疗 0.02 + 0.008
    UNEMPLOYMENT_RATE = 0.005  # 失业保险
    INJURY_RATE = 0.0       # 工伤保险（由企业承担）
    MATERNITY_RATE = 0.0    # 生育保险（由企业承担）
    HOUSING_FUND_RATE = 0.12   # 公积金（假设12%）
    
    # 企业承担的费率（用于计算总税负）
    EMPLOYER_PENSION_RATE = 0.16     # 企业养老保险
    EMPLOYER_MEDICAL_RATE = 0.095    # 企业医疗保险
    EMPLOYER_UNEMPLOYMENT_RATE = 0.005  # 企业失业保险
    EMPLOYER_INJURY_RATE = 0.004     # 企业工伤保险（费率浮动）
    EMPLOYER_MATERNITY_RATE = 0.008  # 企业生育保险
    EMPLOYER_HOUSING_FUND_RATE = 0.12  # 企业公积金
    
    # 专项附加扣除标准
    class SpecialDeductionLimits:
        # 住房租金扣除标准（每月）
        RENT_TIER_1 = 2000  # 一线城市
        RENT_TIER_2 = 1500  # 二线城市
        RENT_TIER_3 = 1100  # 其他城市
        
        # 其他专项附加扣除标准（每月）
        HOUSING_LOAN = 1000     # 住房贷款利息
        CHILDREN_EDU = 1000     # 子女教育（每个子女）
        CONTINUING_EDU = 400    # 继续教育
        ELDERLY_CARE = 2000     # 赡养老人（独生子女最高）
        
        # 城市分类
        TIER_1_CITIES = ['北京', '上海', '广州', '深圳']
        TIER_2_CITIES = [
            '天津', '重庆', '南京', '杭州', '武汉', '成都', '西安',
            '济南', '长春', '哈尔滨', '沈阳', '南宁', '昆明', '合肥',
            '郑州', '福州', '南昌', '长沙', '贵阳', '兰州', '西宁',
            '呼和浩特', '乌鲁木齐', '拉萨', '银川', '石家庄',
            '大连', '青岛', '宁波', '厦门', '深圳'
        ]

@dataclass
class SpecialDeductions:
    """专项附加扣除"""
    housing_rent: float = 0      # 住房租金，最高1500/月
    housing_loan: float = 0      # 住房贷款利息，固定1000/月
    children_edu: float = 0      # 子女教育，每个子女1000/月
    continuing_edu: float = 0    # 继续教育，400/月
    elderly_care: float = 0      # 赡养老人，最高2000/月
    medical_expense: float = 0   # 大病医疗

def calculate_social_insurance(monthly_salary: float) -> Dict[str, float]:
    """计算社保和公积金"""
    # 确定计算基数
    base = min(max(monthly_salary, TaxConstants.SOCIAL_INSURANCE_BASE_MIN), 
              TaxConstants.SOCIAL_INSURANCE_BASE_MAX)
    
    # 个人缴纳部分
    pension = base * TaxConstants.PENSION_RATE
    medical = base * TaxConstants.MEDICAL_RATE
    unemployment = base * TaxConstants.UNEMPLOYMENT_RATE
    housing_fund = base * TaxConstants.HOUSING_FUND_RATE
    
    # 企业缴纳部分
    employer_pension = base * TaxConstants.EMPLOYER_PENSION_RATE
    employer_medical = base * TaxConstants.EMPLOYER_MEDICAL_RATE
    employer_unemployment = base * TaxConstants.EMPLOYER_UNEMPLOYMENT_RATE
    employer_injury = base * TaxConstants.EMPLOYER_INJURY_RATE
    employer_maternity = base * TaxConstants.EMPLOYER_MATERNITY_RATE
    employer_housing_fund = base * TaxConstants.EMPLOYER_HOUSING_FUND_RATE
    
    personal_total = pension + medical + unemployment + housing_fund
    employer_total = (employer_pension + employer_medical + employer_unemployment + 
                     employer_injury + employer_maternity + employer_housing_fund)
    
    return {
        "personal": {
            "pension": pension,
            "medical": medical,
            "unemployment": unemployment,
            "housing_fund": housing_fund,
            "total": personal_total
        },
        "employer": {
            "pension": employer_pension,
            "medical": employer_medical,
            "unemployment": employer_unemployment,
            "injury": employer_injury,
            "maternity": employer_maternity,
            "housing_fund": employer_housing_fund,
            "total": employer_total
        },
        "base": base
    }

def calculate_marginal_rates(monthly_salary: float) -> Dict[str, float]:
    """计算边际税率"""
    annual_income = monthly_salary * 12
    
    # 个税边际税率
    tax_rate = 0
    for lower, upper, rate in TaxConstants.TAX_BRACKETS:
        if lower <= annual_income <= upper:
            tax_rate = rate
            break
    
    # 社保边际税率（如果未达到上限）
    insurance_rate = 0
    if monthly_salary <= TaxConstants.SOCIAL_INSURANCE_BASE_MAX:
        insurance_rate = (TaxConstants.PENSION_RATE + 
                         TaxConstants.MEDICAL_RATE + 
                         TaxConstants.UNEMPLOYMENT_RATE)
    
    # 公积金边际税率（如果未达到上限）
    housing_fund_rate = 0
    if monthly_salary <= TaxConstants.HOUSING_FUND_BASE_MAX:
        housing_fund_rate = TaxConstants.HOUSING_FUND_RATE
    
    total_rate = tax_rate + insurance_rate + housing_fund_rate
    
    return {
        "tax": tax_rate,
        "insurance": insurance_rate,
        "housing_fund": housing_fund_rate,
        "total": total_rate
    }

def calculate_tax(monthly_salary: float, deductions: SpecialDeductions) -> Dict[str, float]:
    """计算个人所得税"""
    # 计算社保和公积金
    insurance = calculate_social_insurance(monthly_salary)
    
    # 计算专项附加扣除总额
    special_deductions = (
        deductions.housing_rent +
        deductions.housing_loan +
        deductions.children_edu +
        deductions.continuing_edu +
        deductions.elderly_care +
        deductions.medical_expense
    )
    
    # 计算应纳税所得额
    taxable_income = (monthly_salary - 
                     TaxConstants.TAX_FREE_THRESHOLD - 
                     insurance["personal"]["total"] - 
                     special_deductions)
    
    # 计算税额
    tax = 0
    if taxable_income > 0:
        annual_taxable = taxable_income * 12
        for lower, upper, rate in TaxConstants.TAX_BRACKETS:
            if annual_taxable > lower:
                tax_part = min(annual_taxable - lower, upper - lower) * rate
                tax += tax_part
    
    monthly_tax = tax / 12
    net_income = monthly_salary - monthly_tax - insurance["personal"]["total"]
    
    return {
        "gross_salary": monthly_salary,
        "insurance": insurance,
        "special_deductions": special_deductions,
        "taxable_income": taxable_income,
        "tax": monthly_tax,
        "net_income": net_income
    }

def print_tax_details(results: Dict[str, float]):
    """打印税收详情"""
    monthly_salary = results["gross_salary"]
    total_cost = (monthly_salary + 
                 results["insurance"]["employer"]["total"])
    
    tables = {
        "收入概况": [
            ["月度工资", format_money(monthly_salary)],
            ["计税基数", format_money(results["insurance"]["base"])]
        ],
        
        "个人缴纳五险一金": [
            ["养老保险", format_money(results["insurance"]["personal"]["pension"])],
            ["医疗保险", format_money(results["insurance"]["personal"]["medical"])],
            ["失业保险", format_money(results["insurance"]["personal"]["unemployment"])],
            ["住房公积金", format_money(results["insurance"]["personal"]["housing_fund"])],
            ["合计", format_money(results["insurance"]["personal"]["total"])]
        ],
        
        "企业缴纳五险一金": [
            ["养老保险", format_money(results["insurance"]["employer"]["pension"])],
            ["医疗保险", format_money(results["insurance"]["employer"]["medical"])],
            ["失业保险", format_money(results["insurance"]["employer"]["unemployment"])],
            ["工伤保险", format_money(results["insurance"]["employer"]["injury"])],
            ["生育保险", format_money(results["insurance"]["employer"]["maternity"])],
            ["住房公积金", format_money(results["insurance"]["employer"]["housing_fund"])],
            ["合计", format_money(results["insurance"]["employer"]["total"])]
        ],
        
        "个税计算": [
            ["应纳税所得额", format_money(results["taxable_income"])],
            ["专项附加扣除", format_money(results["special_deductions"])],
            ["个人所得税", format_money(results["tax"])]
        ],
        
        "最终收入": [
            ["税前月收入", format_money(monthly_salary)],
            ["税后月收入", format_money(results["net_income"])],
            ["年度税后收入", format_money(results["net_income"] * 12)],
            ["企业总成本", format_money(total_cost)]
        ]
    }
    
    # 计算并显示边际税率
    marginal_rates = calculate_marginal_rates(monthly_salary)
    tables["边际税率分析"] = [
        ["个税边际税率", format_percent(marginal_rates["tax"])],
        ["社保边际费率", format_percent(marginal_rates["insurance"])],
        ["公积金边际费率", format_percent(marginal_rates["housing_fund"])],
        ["总边际税率", format_percent(marginal_rates["total"])]
    ]
    
    # 计算总体税负率
    total_deductions = (results["tax"] + 
                       results["insurance"]["personal"]["total"] + 
                       results["insurance"]["employer"]["total"])
    total_tax_rate = total_deductions / total_cost
    
    tables["总体税负分析"] = [
        ["个人所得税率", format_percent(results["tax"] / monthly_salary)],
        ["个人五险一金率", format_percent(results["insurance"]["personal"]["total"] / monthly_salary)],
        ["企业五险一金率", format_percent(results["insurance"]["employer"]["total"] / monthly_salary)],
        ["总体税负率", format_percent(total_tax_rate)]
    ]
    
    for title, data in tables.items():
        print_subsection(title)
        print(tabulate(data, headers=["项目", "金额/比率"], 
                      tablefmt="grid", numalign="right"))

def format_money(amount: float) -> str:
    """格式化金额输出"""
    return f"¥{amount:,.2f}"

def format_percent(rate: float) -> str:
    """格式化百分比输出"""
    return f"{rate*100:.1f}%"

def print_section(title: str):
    """打印带格式的章节标题"""
    print(f"\n{Fore.CYAN}{'='*20} {title} {'='*20}{Style.RESET_ALL}")

def print_subsection(title: str):
    """打印带格式的子章节标题"""
    print(f"\n{Fore.GREEN}{title}{Style.RESET_ALL}")

def get_rent_deduction_limit(city: str) -> float:
    """获取城市对应的住房租金扣除限额"""
    if city in TaxConstants.SpecialDeductionLimits.TIER_1_CITIES:
        return TaxConstants.SpecialDeductionLimits.RENT_TIER_1
    elif city in TaxConstants.SpecialDeductionLimits.TIER_2_CITIES:
        return TaxConstants.SpecialDeductionLimits.RENT_TIER_2
    else:
        return TaxConstants.SpecialDeductionLimits.RENT_TIER_3

def main():
    """主函数"""
    try:
        monthly_salary = float(input("请输入月度工资（元）：¥"))
        
        # 获取城市信息
        city = input("请输入所在城市（用于计算租金扣除标准）：")
        rent_limit = get_rent_deduction_limit(city)
        print(f"\n您所在城市的住房租金扣除限额为：¥{rent_limit}/月")
        
        # 获取专项附加扣除信息
        print("\n请输入专项附加扣除信息（每月）：")
        rent_deduction = float(input(f"住房租金扣除（最高{rent_limit}）：¥") or 0)
        rent_deduction = min(rent_deduction, rent_limit)  # 确保不超过限额
        
        deductions = SpecialDeductions(
            housing_rent=rent_deduction,
            housing_loan=float(input("住房贷款利息扣除（固定1000）：¥") or 0),
            children_edu=float(input("子女教育扣除（每个子女1000）：¥") or 0),
            continuing_edu=float(input("继续教育扣除（400）：¥") or 0),
            elderly_care=float(input("赡养老人扣除（最高2000）：¥") or 0),
            medical_expense=float(input("大病医疗扣除：¥") or 0)
        )
        
        results = calculate_tax(monthly_salary, deductions)
        print_tax_details(results)
        
    except ValueError:
        print(f"{Fore.RED}错误：请输入有效的数字！{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}发生错误：{str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()