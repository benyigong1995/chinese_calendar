from dataclasses import dataclass
from typing import Dict, List, Tuple
import colorama
from colorama import Fore, Style
from tabulate import tabulate
from datetime import date, datetime

# 初始化colorama
colorama.init()

@dataclass
class LoanConstants:
    """贷款相关常量"""
    # 2024年基准利率
    COMMERCIAL_RATE = 0.045  # 商业贷款基准利率 4.5%
    FUND_RATE = 0.031       # 公积金贷款基准利率 3.1%
    
    # 最长贷款年限
    MAX_COMMERCIAL_YEARS = 30  # 商业贷款最长年限
    MAX_FUND_YEARS = 30       # 公积金贷款最长年限
    
    # 公积金贷款额度上限（以北京为例）
    MAX_FUND_LOAN = 1_200_000  # 120万
    
    # 首付比例要求
    MIN_DOWN_PAYMENT_RATIO = 0.3  # 最低首付30%
    
    # 公积金贷款额度计算系数（以北京为例）
    FUND_LOAN_MULTIPLIER = 15  # 可贷额度 = 月缴存额 * 15

class LoanCalculator:
    """房贷计算器"""
    def __init__(self, 
                 house_price: float,
                 down_payment_ratio: float,
                 monthly_fund_deposit: float,
                 years: int,
                 commercial_rate: float = LoanConstants.COMMERCIAL_RATE,
                 fund_rate: float = LoanConstants.FUND_RATE):
        """
        初始化贷款计算器
        :param house_price: 房屋总价
        :param down_payment_ratio: 首付比例
        :param monthly_fund_deposit: 月公积金缴存额
        :param years: 贷款年限
        :param commercial_rate: 商业贷款年利率
        :param fund_rate: 公积金贷款年利率
        """
        # 验证首付比例
        if down_payment_ratio < LoanConstants.MIN_DOWN_PAYMENT_RATIO:
            raise ValueError(f"首付比例不能低于{LoanConstants.MIN_DOWN_PAYMENT_RATIO*100}%")
            
        # 计算总贷款额度
        self.total_amount = house_price * (1 - down_payment_ratio)
        
        # 计算可用公积金贷款额度
        max_fund_by_deposit = monthly_fund_deposit * LoanConstants.FUND_LOAN_MULTIPLIER
        self.fund_amount = min(max_fund_by_deposit, 
                             LoanConstants.MAX_FUND_LOAN,
                             self.total_amount)
        
        # 剩余部分使用商业贷款
        self.commercial_amount = self.total_amount - self.fund_amount
        
        self.years = min(years, LoanConstants.MAX_COMMERCIAL_YEARS)
        self.commercial_rate = commercial_rate
        self.fund_rate = fund_rate
        self.months = self.years * 12
        
        # 月利率
        self.monthly_commercial_rate = commercial_rate / 12
        self.monthly_fund_rate = fund_rate / 12

    def calculate_equal_installment(self) -> Dict:
        """计算等额本息还款"""
        # 商业贷款月供
        commercial_monthly = self._equal_installment_payment(
            self.commercial_amount, 
            self.monthly_commercial_rate, 
            self.months
        ) if self.commercial_amount > 0 else 0
        
        # 公积金贷款月供
        fund_monthly = self._equal_installment_payment(
            self.fund_amount,
            self.monthly_fund_rate,
            self.months
        ) if self.fund_amount > 0 else 0
        
        # 总月供
        total_monthly = commercial_monthly + fund_monthly
        
        # 计算总利息
        total_payment = total_monthly * self.months
        total_interest = total_payment - self.total_amount
        
        return {
            "monthly_payment": total_monthly,
            "commercial_monthly": commercial_monthly,
            "fund_monthly": fund_monthly,
            "total_payment": total_payment,
            "total_interest": total_interest,
            "total_commercial_interest": (commercial_monthly * self.months - self.commercial_amount) if self.commercial_amount > 0 else 0,
            "total_fund_interest": (fund_monthly * self.months - self.fund_amount) if self.fund_amount > 0 else 0
        }

    def calculate_equal_principal(self) -> Dict:
        """计算等额本金还款"""
        # 每月本金
        monthly_commercial_principal = self.commercial_amount / self.months if self.commercial_amount > 0 else 0
        monthly_fund_principal = self.fund_amount / self.months if self.fund_amount > 0 else 0
        
        # 计算首月利息
        first_month_commercial_interest = self.commercial_amount * self.monthly_commercial_rate if self.commercial_amount > 0 else 0
        first_month_fund_interest = self.fund_amount * self.monthly_fund_rate if self.fund_amount > 0 else 0
        
        # 计算每月递减金额
        commercial_decrease = monthly_commercial_principal * self.monthly_commercial_rate if self.commercial_amount > 0 else 0
        fund_decrease = monthly_fund_principal * self.monthly_fund_rate if self.fund_amount > 0 else 0
        
        # 首月月供
        first_month_payment = (monthly_commercial_principal + first_month_commercial_interest +
                             monthly_fund_principal + first_month_fund_interest)
        
        # 末月月供
        last_month_payment = (monthly_commercial_principal + first_month_commercial_interest - commercial_decrease * (self.months - 1) +
                            monthly_fund_principal + first_month_fund_interest - fund_decrease * (self.months - 1))
        
        # 计算总利息
        total_commercial_interest = (first_month_commercial_interest * self.months - 
                                   commercial_decrease * (self.months - 1) * self.months / 2) if self.commercial_amount > 0 else 0
        total_fund_interest = (first_month_fund_interest * self.months - 
                             fund_decrease * (self.months - 1) * self.months / 2) if self.fund_amount > 0 else 0
        
        return {
            "first_month_payment": first_month_payment,
            "last_month_payment": last_month_payment,
            "monthly_decrease": commercial_decrease + fund_decrease,
            "total_interest": total_commercial_interest + total_fund_interest,
            "total_commercial_interest": total_commercial_interest,
            "total_fund_interest": total_fund_interest,
            "total_payment": self.total_amount + total_commercial_interest + total_fund_interest
        }

    @staticmethod
    def _equal_installment_payment(principal: float, monthly_rate: float, months: int) -> float:
        """计算等额本息月供"""
        if monthly_rate == 0:
            return principal / months
        return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

def format_money(amount: float) -> str:
    """格式化金额输出"""
    return f"¥{amount:,.2f}"

def print_loan_details(calculator: LoanCalculator):
    """打印贷款详情"""
    equal_installment = calculator.calculate_equal_installment()
    equal_principal = calculator.calculate_equal_principal()
    
    tables = {
        "贷款信息": [
            ["总贷款金额", format_money(calculator.total_amount)],
            ["商业贷款金额", format_money(calculator.commercial_amount)],
            ["公积金贷款金额", format_money(calculator.fund_amount)],
            ["贷款年限", f"{calculator.years}年"],
            ["商业贷款利率", f"{calculator.commercial_rate*100:.2f}%"],
            ["公积金贷款利率", f"{calculator.fund_rate*100:.2f}%"]
        ],
        
        "等额本息还款": [
            ["月供", format_money(equal_installment["monthly_payment"])],
            ["商业贷款月供", format_money(equal_installment["commercial_monthly"])],
            ["公积金贷款月供", format_money(equal_installment["fund_monthly"])],
            ["总还款额", format_money(equal_installment["total_payment"])],
            ["总利息", format_money(equal_installment["total_interest"])],
            ["商业贷款总利息", format_money(equal_installment["total_commercial_interest"])],
            ["公积金贷款总利息", format_money(equal_installment["total_fund_interest"])]
        ],
        
        "等额本金还款": [
            ["首月月供", format_money(equal_principal["first_month_payment"])],
            ["末月月供", format_money(equal_principal["last_month_payment"])],
            ["月供递减金额", format_money(equal_principal["monthly_decrease"])],
            ["总还款额", format_money(equal_principal["total_payment"])],
            ["总利息", format_money(equal_principal["total_interest"])],
            ["商业贷款总利息", format_money(equal_principal["total_commercial_interest"])],
            ["公积金贷款总利息", format_money(equal_principal["total_fund_interest"])]
        ]
    }
    
    print(f"\n{Fore.CYAN}{'='*20} 房贷计算结果 {'='*20}{Style.RESET_ALL}")
    
    for title, data in tables.items():
        print(f"\n{Fore.GREEN}{title}{Style.RESET_ALL}")
        print(tabulate(data, headers=["项目", "金额"], 
                      tablefmt="grid", numalign="right"))

def main():
    """主函数"""
    try:
        print(f"{Fore.CYAN}房贷计算器 (2024){Style.RESET_ALL}")
        house_price = float(input("请输入房屋总价（万元）：")) * 10000
        down_payment_ratio = float(input("请输入首付比例（如：0.3 表示30%）："))
        monthly_fund_deposit = float(input("请输入月公积金缴存额（元）："))
        years = int(input("请输入贷款年限（最长30年）："))
        
        # 可选：自定义利率
        use_custom_rate = input("是否使用自定义利率？(y/n)：").lower() == 'y'
        if use_custom_rate:
            commercial_rate = float(input("请输入商业贷款年利率（%）：")) / 100
            fund_rate = float(input("请输入公积金贷款年利率（%）：")) / 100
        else:
            commercial_rate = LoanConstants.COMMERCIAL_RATE
            fund_rate = LoanConstants.FUND_RATE
        
        calculator = LoanCalculator(
            house_price=house_price,
            down_payment_ratio=down_payment_ratio,
            monthly_fund_deposit=monthly_fund_deposit,
            years=years,
            commercial_rate=commercial_rate,
            fund_rate=fund_rate
        )
        
        print_loan_details(calculator)
        
    except ValueError as e:
        print(f"{Fore.RED}错误：{str(e)}{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}发生错误：{str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()