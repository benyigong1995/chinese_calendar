from dataclasses import dataclass
from typing import Dict, List, Tuple
import colorama
from colorama import Fore, Style
from tabulate import tabulate

# 初始化colorama
colorama.init()

@dataclass
class TaxBracket:
    """税收等级数据类"""
    lower: float
    upper: float
    rate: float

class TaxConstants:
    """税收相关常量"""
    YEAR = 2024
    MAX_401K = 23000
    SS_LIMIT = 168600
    SDI_LIMIT = 153164
    MEDICARE_THRESHOLD = 200000
    
    # 联邦税率表
    FEDERAL_BRACKETS = {
        "single": [
            TaxBracket(0, 11600, 0.10),
            TaxBracket(11600, 47150, 0.12),
            TaxBracket(47150, 100525, 0.22),
            TaxBracket(100525, 191950, 0.24),
            TaxBracket(191950, 243725, 0.32),
            TaxBracket(243725, 609350, 0.35),
            TaxBracket(609350, float('inf'), 0.37)
        ],
        "married": [
            TaxBracket(0, 23200, 0.10),
            TaxBracket(23200, 94300, 0.12),
            TaxBracket(94300, 201050, 0.22),
            TaxBracket(201050, 383900, 0.24),
            TaxBracket(383900, 487450, 0.32),
            TaxBracket(487450, 731200, 0.35),
            TaxBracket(731200, float('inf'), 0.37)
        ]
    }
    
    # 加州税率表
    CA_BRACKETS = {
        "single": [
            TaxBracket(0, 10412, 0.01),
            TaxBracket(10412, 24684, 0.02),
            TaxBracket(24684, 38959, 0.04),
            TaxBracket(38959, 54081, 0.06),
            TaxBracket(54081, 68350, 0.08),
            TaxBracket(68350, 349137, 0.093),
            TaxBracket(349137, 418961, 0.103),
            TaxBracket(418961, 698272, 0.113),
            TaxBracket(698272, float('inf'), 0.123)
        ],
        "married": [
            TaxBracket(0, 20824, 0.01),
            TaxBracket(20824, 49368, 0.02),
            TaxBracket(49368, 77918, 0.04),
            TaxBracket(77918, 108162, 0.06),
            TaxBracket(108162, 136700, 0.08),
            TaxBracket(136700, 698274, 0.093),
            TaxBracket(698274, 837922, 0.103),
            TaxBracket(837922, 1396544, 0.113),
            TaxBracket(1396544, float('inf'), 0.123)
        ]
    }
    
    # 标准扣除额
    STANDARD_DEDUCTION = {
        "single": 14600,
        "married": 29200
    }
    
    # 加州标准扣除额
    CA_STANDARD_DEDUCTION = {
        "single": 5363,
        "married": 10726
    }

def format_money(amount: float) -> str:
    """格式化金额输出"""
    return f"${amount:,.2f}"

def format_percent(rate: float) -> str:
    """格式化百分比输出"""
    return f"{rate*100:.1f}%"

def print_section(title: str):
    """打印带格式的章节标题"""
    print(f"\n{Fore.CYAN}{'='*20} {title} {'='*20}{Style.RESET_ALL}")

def print_subsection(title: str):
    """打印带格式的子章节标题"""
    print(f"\n{Fore.GREEN}{title}{Style.RESET_ALL}")

def calculate_federal_tax(income: float, filing_status: str) -> float:
    """计算联邦税"""
    standard_deduction = TaxConstants.STANDARD_DEDUCTION[filing_status]
    taxable_income = max(0, income - standard_deduction)
    
    total_tax = 0
    remaining_income = taxable_income
    
    for bracket in TaxConstants.FEDERAL_BRACKETS[filing_status]:
        if remaining_income <= 0:
            break
        taxable_amount = min(remaining_income, bracket.upper - bracket.lower)
        total_tax += taxable_amount * bracket.rate
        remaining_income -= taxable_amount
    
    return total_tax

def calculate_ca_state_tax(income: float, capital_gains: float, filing_status: str) -> float:
    """计算加州州税"""
    standard_deduction = TaxConstants.CA_STANDARD_DEDUCTION[filing_status]
    taxable_income = max(0, income + capital_gains - standard_deduction)
    
    total_tax = 0
    remaining_income = taxable_income
    
    for bracket in TaxConstants.CA_BRACKETS[filing_status]:
        if remaining_income <= 0:
            break
        taxable_amount = min(remaining_income, bracket.upper - bracket.lower)
        total_tax += taxable_amount * bracket.rate
        remaining_income -= taxable_amount
    
    return total_tax

def calculate_fica_taxes(income: float) -> Dict[str, float]:
    """计算FICA税（社保税和医疗保险税）"""
    ss_tax = min(income, TaxConstants.SS_LIMIT) * 0.062
    medicare_tax = income * 0.0145
    
    additional_medicare = (income - TaxConstants.MEDICARE_THRESHOLD) * 0.009 if income > TaxConstants.MEDICARE_THRESHOLD else 0
    
    return {
        "social_security": ss_tax,
        "medicare": medicare_tax,
        "additional_medicare": additional_medicare,
        "total": ss_tax + medicare_tax + additional_medicare
    }

def calculate_ca_sdi(income: float) -> float:
    """计算加州SDI（州残障保险）"""
    return min(income, TaxConstants.SDI_LIMIT) * 0.009

def calculate_capital_gains_tax(capital_gains: float, income: float, filing_status: str) -> float:
    """计算资本利得税"""
    brackets = {
        "single": [
            TaxBracket(0, 44625, 0),
            TaxBracket(44625, 492300, 0.15),
            TaxBracket(492300, float('inf'), 0.20)
        ],
        "married": [
            TaxBracket(0, 89250, 0),
            TaxBracket(89250, 553850, 0.15),
            TaxBracket(553850, float('inf'), 0.20)
        ]
    }
    
    total_income = income + capital_gains
    for bracket in brackets[filing_status]:
        if bracket.lower <= total_income <= bracket.upper:
            return capital_gains * bracket.rate
    
    return capital_gains * 0.20

def calculate_marginal_rates(income: float, filing_status: str) -> Dict[str, float]:
    """计算边际税率"""
    # 获取联邦和加州的边际税率
    federal_rate = 0
    for bracket in TaxConstants.FEDERAL_BRACKETS[filing_status]:
        if bracket.lower <= income <= bracket.upper:
            federal_rate = bracket.rate
            break
    
    ca_rate = 0
    for bracket in TaxConstants.CA_BRACKETS[filing_status]:
        if bracket.lower <= income <= bracket.upper:
            ca_rate = bracket.rate
            break
    
    # FICA税率
    fica_rate = 0.0145  # 基础医疗保险税率
    if income <= TaxConstants.SS_LIMIT:
        fica_rate += 0.062  # 社保税率
    if income > TaxConstants.MEDICARE_THRESHOLD:
        fica_rate += 0.009  # 额外医疗保险税率
    
    # SDI税率
    sdi_rate = 0.009 if income <= TaxConstants.SDI_LIMIT else 0
    
    total_rate = federal_rate + ca_rate + fica_rate + sdi_rate
    
    return {
        "federal": federal_rate,
        "california": ca_rate,
        "fica": fica_rate,
        "sdi": sdi_rate,
        "total": total_rate
    }

def print_tax_summary(description: str, amount: float, total_income: float):
    """打印税收摘要"""
    rate = amount / total_income if total_income > 0 else 0
    print(f"  {description}: {format_money(amount)} ({format_percent(rate)})")

def print_marginal_rates(income: float, filing_status: str):
    """打印边际税率详情"""
    rates = calculate_marginal_rates(income, filing_status)
    
    print_subsection("边际税率分析")
    print(f"  联邦边际税率：{format_percent(rates['federal'])}")
    print(f"  加州边际税率：{format_percent(rates['california'])}")
    print(f"  FICA边际税率：{format_percent(rates['fica'])}")
    print(f"  SDI边际税率：{format_percent(rates['sdi'])}")
    print(f"  总边际税率：{format_percent(rates['total'])}")
    print(f"  额外收入$100的税收：{format_money(rates['total']*100)}")

@dataclass
class TaxResult:
    """税收计算结果数据类"""
    federal_tax: float
    capital_gains_tax: float
    ca_tax: float
    fica_taxes: Dict[str, float]
    sdi_tax: float
    total_tax: float
    net_income: float
    marginal_rates: Dict[str, float]

def calculate_tax_results(annual_income: float, capital_gains: float, actual_401k: float) -> Dict[str, TaxResult]:
    """计算所有税收结果"""
    results = {}
    adjusted_income = annual_income - actual_401k
    
    for status in ["single", "married"]:
        federal_tax = calculate_federal_tax(adjusted_income, status)
        capital_gains_tax = calculate_capital_gains_tax(capital_gains, adjusted_income, status)
        fica_taxes = calculate_fica_taxes(annual_income)
        ca_tax = calculate_ca_state_tax(adjusted_income, capital_gains, status)
        sdi_tax = calculate_ca_sdi(annual_income)
        
        total_tax = (federal_tax + capital_gains_tax + ca_tax + 
                    fica_taxes["total"] + sdi_tax)
        total_income = annual_income + capital_gains
        net_income = total_income - total_tax - actual_401k
        marginal_rates = calculate_marginal_rates(adjusted_income, status)
        
        results[status] = TaxResult(
            federal_tax=federal_tax,
            capital_gains_tax=capital_gains_tax,
            ca_tax=ca_tax,
            fica_taxes=fica_taxes,
            sdi_tax=sdi_tax,
            total_tax=total_tax,
            net_income=net_income,
            marginal_rates=marginal_rates
        )
    
    return results

def print_comparison_tables(annual_income: float, capital_gains: float = 0, maximize_401k: bool = True):
    """打印对比表格"""
    actual_401k = min(annual_income, TaxConstants.MAX_401K) if maximize_401k else 0
    total_income = annual_income + capital_gains
    results = calculate_tax_results(annual_income, capital_gains, actual_401k)
    
    print_section(f"{TaxConstants.YEAR}年税收分析")
    
    # 收入概况
    print_subsection("收入概况")
    print(f"总工资收入：{format_money(annual_income)}")
    print(f"401(k)供款：{format_money(actual_401k)}")
    print(f"调整后收入：{format_money(annual_income - actual_401k)}")
    print(f"资本利得：{format_money(capital_gains)}")
    
    # 税收对比表格
    tables = {
        "税前扣除": [
            ["401(k)供款", format_money(actual_401k), format_money(actual_401k)],
            ["联邦标准扣除额", 
             format_money(TaxConstants.STANDARD_DEDUCTION["single"]),
             format_money(TaxConstants.STANDARD_DEDUCTION["married"])],
            ["加州标准扣除额",
             format_money(TaxConstants.CA_STANDARD_DEDUCTION["single"]),
             format_money(TaxConstants.CA_STANDARD_DEDUCTION["married"])]
        ],
        
        "联邦税详情": [
            ["联邦所得税", 
             f"{format_money(results['single'].federal_tax)} ({format_percent(results['single'].federal_tax/total_income)})",
             f"{format_money(results['married'].federal_tax)} ({format_percent(results['married'].federal_tax/total_income)})"],
            ["资本利得税",
             f"{format_money(results['single'].capital_gains_tax)} ({format_percent(results['single'].capital_gains_tax/total_income)})",
             f"{format_money(results['married'].capital_gains_tax)} ({format_percent(results['married'].capital_gains_tax/total_income)})"]
        ],
        
        "加州税详情": [
            ["加州州税",
             f"{format_money(results['single'].ca_tax)} ({format_percent(results['single'].ca_tax/total_income)})",
             f"{format_money(results['married'].ca_tax)} ({format_percent(results['married'].ca_tax/total_income)})"]
        ],
        
        "工资税详情": [
            ["社保税",
             f"{format_money(results['single'].fica_taxes['social_security'])} ({format_percent(results['single'].fica_taxes['social_security']/total_income)})",
             f"{format_money(results['married'].fica_taxes['social_security'])} ({format_percent(results['married'].fica_taxes['social_security']/total_income)})"],
            ["医疗保险税",
             f"{format_money(results['single'].fica_taxes['medicare'])} ({format_percent(results['single'].fica_taxes['medicare']/total_income)})",
             f"{format_money(results['married'].fica_taxes['medicare'])} ({format_percent(results['married'].fica_taxes['medicare']/total_income)})"],
            ["额外医疗保险税",
             f"{format_money(results['single'].fica_taxes['additional_medicare'])} ({format_percent(results['single'].fica_taxes['additional_medicare']/total_income)})",
             f"{format_money(results['married'].fica_taxes['additional_medicare'])} ({format_percent(results['married'].fica_taxes['additional_medicare']/total_income)})"],
            ["加州SDI",
             f"{format_money(results['single'].sdi_tax)} ({format_percent(results['single'].sdi_tax/total_income)})",
             f"{format_money(results['married'].sdi_tax)} ({format_percent(results['married'].sdi_tax/total_income)})"]
        ],
        
        "总体税收情况": [
            ["联邦税总额",
             f"{format_money(results['single'].federal_tax + results['single'].capital_gains_tax)} ({format_percent((results['single'].federal_tax + results['single'].capital_gains_tax)/total_income)})",
             f"{format_money(results['married'].federal_tax + results['married'].capital_gains_tax)} ({format_percent((results['married'].federal_tax + results['married'].capital_gains_tax)/total_income)})"],
            ["加州税总额",
             f"{format_money(results['single'].ca_tax)} ({format_percent(results['single'].ca_tax/total_income)})",
             f"{format_money(results['married'].ca_tax)} ({format_percent(results['married'].ca_tax/total_income)})"],
            ["工资税总额",
             f"{format_money(results['single'].fica_taxes['total'] + results['single'].sdi_tax)} ({format_percent((results['single'].fica_taxes['total'] + results['single'].sdi_tax)/total_income)})",
             f"{format_money(results['married'].fica_taxes['total'] + results['married'].sdi_tax)} ({format_percent((results['married'].fica_taxes['total'] + results['married'].sdi_tax)/total_income)})"],
            ["总税收",
             f"{format_money(results['single'].total_tax)} ({format_percent(results['single'].total_tax/total_income)})",
             f"{format_money(results['married'].total_tax)} ({format_percent(results['married'].total_tax/total_income)})"],
            ["税后年收入",
             format_money(results['single'].net_income),
             format_money(results['married'].net_income)],
            ["税后月收入",
             format_money(results['single'].net_income/12),
             format_money(results['married'].net_income/12)]
        ],
        
        "边际税率分析": [
            ["联邦边际税率",
             format_percent(results['single'].marginal_rates['federal']),
             format_percent(results['married'].marginal_rates['federal'])],
            ["加州边际税率",
             format_percent(results['single'].marginal_rates['california']),
             format_percent(results['married'].marginal_rates['california'])],
            ["FICA边际税率",
             format_percent(results['single'].marginal_rates['fica']),
             format_percent(results['married'].marginal_rates['fica'])],
            ["SDI边际税率",
             format_percent(results['single'].marginal_rates['sdi']),
             format_percent(results['married'].marginal_rates['sdi'])],
            ["总边际税率",
             format_percent(results['single'].marginal_rates['total']),
             format_percent(results['married'].marginal_rates['total'])]
        ]
    }
    
    # 打印所有表格
    for title, data in tables.items():
        print_subsection(title)
        print(tabulate(data, headers=["项目", "单身申报", "夫妻共同申报"], 
                      tablefmt="grid", numalign="right"))

def main():
    """主函数"""
    try:
        annual_income = float(input("请输入年度工资收入（美元）：$"))
        capital_gains = float(input("请输入资本利得收入（美元）：$"))
        print_comparison_tables(annual_income, capital_gains, maximize_401k=True)
    except ValueError:
        print(f"{Fore.RED}错误：请输入有效的数字！{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}发生错误：{str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()