import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_school_info(url):
    """获取单页的学校信息"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有学校项
        schools = soup.find_all('div', class_='sch-item')
        
        school_list = []
        for school in schools:
            # 获取学校名称和主页链接
            name_tag = school.find('a', class_='name')
            name = name_tag.text.strip()
            school_main_url = 'https://gaokao.chsi.com.cn' + name_tag['href']
            
            # 从主页获取简介页面链接
            try:
                main_response = requests.get(school_main_url, headers=headers)
                main_response.encoding = 'utf-8'
                main_soup = BeautifulSoup(main_response.text, 'html.parser')
                
                # 查找"学校简介"链接
                intro_link = main_soup.find('a', text='学校简介')
                if intro_link:
                    school_url = 'https://gaokao.chsi.com.cn' + intro_link['href']
                else:
                    print(f"未找到{name}的学校简介链接")
                    continue
                    
                time.sleep(1)  # 添加延时避免请求过快
            except Exception as e:
                print(f"获取{name}简介页面链接时出错: {e}")
                continue
            
            # 获取学校基本信息
            info = school.find('a', class_='sch-department').text.strip()
            location = info.split('|')[0].encode('utf-8').decode('utf-8').replace('\ue6a4', '').strip()
            department = info.split('|')[1].replace('主管部门：', '').strip()
            
            # 获取办学层次和特性
            level_info = school.find('a', class_='sch-level').text.strip()
            level_parts = level_info.split('|')
            education_level = level_parts[0].strip()
            school_type = level_parts[1].strip() if len(level_parts) > 1 else ''
            
            # 获取满意度
            satisfaction = school.find('a', class_='num')
            satisfaction = satisfaction.text.strip() if satisfaction else ''
            
            # 获取学校详细信息
            detail_info = get_school_detail(school_url)
            
            school_info = {
                '学校名称': name,
                '所在地': location,
                '主管部门': department,
                '办学层次': education_level,
                '学校特性': school_type,
                '满意度': satisfaction,
                '学校简介': detail_info.get('简介', '')
            }

            school_list.append(school_info)
            print(f"已获取{name}的信息")
            
        return school_list
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

def get_school_detail(url):
    """获取学校详细信息"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取学校简介
        intro_divs = soup.find_all('div', class_='yxk-detail-con')
        intro = ''
        for div in intro_divs:
            prev_h4 = div.find_previous_sibling('h4', class_='yxk-second-title')
            if prev_h4 and '学校简介' in prev_h4.text:
                paragraphs = div.find_all('p')
                intro = '\n'.join(p.text.strip() for p in paragraphs if p.text.strip())
                break
        
        # 只返回简介信息
        return {
            '简介': intro
        }
        
    except Exception as e:
        print(f"获取学校详细信息时出错: {e}")
        return {
            '简介': ''
        }

def get_all_schools():
    """获取所有页面的学校信息"""
    base_url = "https://gaokao.chsi.com.cn/sch/search--ss-on,option-qg,searchType-1,start-{}.dhtml"
    all_schools = []
    page = 0
    
    while True:
        url = base_url.format(page)
        schools = get_school_info(url)

        if not schools:
            break
            
        all_schools.extend(schools)
        print(f"已获取第{page//20 + 1}页数据，共{len(schools)}所学校")
        
        page += 20
        time.sleep(3)  # 增加到3秒，避免请求过于频繁
        
    return all_schools

def main():
    # 获取所有学校信息
    schools = get_all_schools()
    
    # 转换为DataFrame并保存为CSV
    df = pd.DataFrame(schools)
    df.to_csv('schools_info.csv', index=False, encoding='utf-8-sig')  # 使用utf-8-sig编码以支持中文
    print(f"共获取{len(schools)}所学校信息，已保存到schools_info.csv")

if __name__ == "__main__":
    main()
