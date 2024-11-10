from dataclasses import dataclass
import colorama
from colorama import Fore, Style
from tabulate import tabulate

colorama.init()

@dataclass
class HealthConstants:
    """健康相关常量"""
    # 体脂率范围
    BODY_FAT_MALE = (14, 17)      # 男性健康体脂率范围
    BODY_FAT_FEMALE = (21, 24)    # 女性健康体脂率范围
    
    # 身高参考点 (cm)
    HEIGHT_REFERENCE = {
        'male': {
            'min': 160,    # 最低参考身高
            'max': 185     # 最高参考身高
        },
        'female': {
            'min': 150,    # 最低参考身高
            'max': 175     # 最高参考身高
        }
    }
    
    # 调整体重系数参考值 (kg/cm)
    WEIGHT_COEF_REFERENCE = {
        'male': {
            'min': 0.29,    # 160cm对应系数
            'mid': 0.33,    # 175cm对应系数
            'max': 0.35     # 185cm以上对应系数
        },
        'female': {
            'min': 0.23,    # 150cm对应系数
            'mid': 0.26,    # 165cm对应系数
            'max': 0.28     # 175cm以上对应系数
        }
    }
    
    # 体成分比例
    BODY_COMPOSITION = {
        'male': {
            'muscle': 0.50,    # 肌肉占比
            'bone': 0.15,      # 骨骼占比
            'organ': 0.21      # 器官占比
        },
        'female': {
            'muscle': 0.41,    # 肌肉占比
            'bone': 0.12,      # 骨骼占比
            'organ': 0.23      # 器官占比
        }
    }

class WeightCalculator:
    def __init__(self, height: float):
        if height < 100 or height > 250:
            raise ValueError("身高数值不合理")
        self.height = height

    def calculate_weight_coefficient(self, height: float, is_male: bool) -> float:
        """使用分段线性插值计算体重系数"""
        ref = HealthConstants.HEIGHT_REFERENCE['male' if is_male else 'female']
        coef = HealthConstants.WEIGHT_COEF_REFERENCE['male' if is_male else 'female']
        
        if height > 185:  # 超高身高使用更高系数
            return coef['max']
        elif height > 175:  # 高身高区间
            ratio = (height - 175) / (185 - 175)
            return coef['mid'] + ratio * (coef['max'] - coef['mid'])
        else:  # 普通身高区间
            ratio = (height - ref['min']) / (175 - ref['min'])
            return coef['min'] + ratio * (coef['mid'] - coef['min'])

    def calculate_weight_range(self, is_male: bool) -> dict:
        """计算理想体重范围"""
        # 计算基础体重
        weight_coef = self.calculate_weight_coefficient(self.height, is_male)
        base_weight = self.height * weight_coef
        
        # 计算体重范围
        fat_range = HealthConstants.BODY_FAT_MALE if is_male else HealthConstants.BODY_FAT_FEMALE
        min_weight = base_weight * (1 + fat_range[0]/100)
        max_weight = base_weight * (1 + fat_range[1]/100)
        
        # 计算体成分
        min_comp = self.calculate_composition(min_weight, is_male)
        max_comp = self.calculate_composition(max_weight, is_male)
        
        return {
            'min_weight': round(min_weight, 1),
            'max_weight': round(max_weight, 1),
            'composition': {
                'min': min_comp,
                'max': max_comp
            }
        }

    def calculate_composition(self, weight: float, is_male: bool) -> dict:
        """计算体重组成"""
        comp = HealthConstants.BODY_COMPOSITION['male' if is_male else 'female']
        
        return {
            'muscle': round(weight * comp['muscle'], 1),
            'bone': round(weight * comp['bone'], 1),
            'organ': round(weight * comp['organ'], 1)
        }

def print_weight_details(height: float):
    """打印详细信息"""
    calculator = WeightCalculator(height)
    male_range = calculator.calculate_weight_range(True)
    female_range = calculator.calculate_weight_range(False)
    
    # 基本数据
    basic_data = [
        ["理想体重", 
         f"{male_range['min_weight']}-{male_range['max_weight']}kg",
         f"{female_range['min_weight']}-{female_range['max_weight']}kg"],
        ["体脂率", 
         f"{HealthConstants.BODY_FAT_MALE[0]}-{HealthConstants.BODY_FAT_MALE[1]}%",
         f"{HealthConstants.BODY_FAT_FEMALE[0]}-{HealthConstants.BODY_FAT_FEMALE[1]}%"]
    ]
    
    # 体成分数据
    composition_data = [
        ["肌肉重量",
         f"{male_range['composition']['min']['muscle']}-{male_range['composition']['max']['muscle']}kg",
         f"{female_range['composition']['min']['muscle']}-{female_range['composition']['max']['muscle']}kg"],
        ["骨骼重量",
         f"{male_range['composition']['min']['bone']}-{male_range['composition']['max']['bone']}kg",
         f"{female_range['composition']['min']['bone']}-{female_range['composition']['max']['bone']}kg"],
        ["器官重量",
         f"{male_range['composition']['min']['organ']}-{male_range['composition']['max']['organ']}kg",
         f"{female_range['composition']['min']['organ']}-{female_range['composition']['max']['organ']}kg"]
    ]
    
    print(f"\n{Fore.CYAN}身高 {height}cm 的健康体重参考{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}基本指标{Style.RESET_ALL}")
    print(tabulate(basic_data, headers=["项目", "男性", "女性"], tablefmt="grid"))
    
    print(f"\n{Fore.GREEN}体成分分析{Style.RESET_ALL}")
    print(tabulate(composition_data, headers=["项目", "男性", "女性"], tablefmt="grid"))
    
    print(f"\n{Fore.YELLOW}说明：{Style.RESET_ALL}")
    print("1. 计算考虑了性别差异的骨骼密度、肌肉比例和代谢特征")
    print("2. 男性通常有更高的骨密度和肌肉比例")
    print("3. 实际数值会因个体差异、运动习惯等因素而变化")

def main():
    """主函数"""
    try:
        print(f"{Fore.CYAN}健康体重计算器 (2024){Style.RESET_ALL}")
        height = float(input("请输入身高(cm)："))
        print_weight_details(height)
        
    except ValueError as e:
        print(f"{Fore.RED}错误：{str(e) if '身高数值不合理' in str(e) else '请输入有效的身高！'}{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}发生错误：{str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()