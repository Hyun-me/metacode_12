import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def crawl_jobkorea():
    url = "https://www.jobkorea.co.kr/Search/?stext=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='list-item')

    company_list, recruit_list, detail_list, url_list = [], [], [], []
    base_url = "https://www.jobkorea.co.kr"

    for article in articles:
        company_tag = article.find('a', class_='corp-name-link dev-view')
        
        company = company_tag.text.strip() if company_tag else None

        recruit = article.get('data-gainfo')
        if recruit and 'dimension45' in recruit:
            start = recruit.find('dimension45":"') + len('dimension45":"')
            end = recruit.find('"', start)
            recruit = recruit[start:end]
        else:
            recruit = "채용공고명 없음"

        detail_tags = article.select('ul.chip-information-group li.chip-information-item')
        details = [li.text.strip() for li in detail_tags]
        detail_str = f"[{', '.join(details)}]" if details else "[]"

        href = company_tag['href'] if company_tag and company_tag.has_attr('href') else None
        full_url = base_url + href if href else None

        company_list.append(company)
        recruit_list.append(recruit)
        detail_list.append(detail_str)
        url_list.append(full_url)

    df = pd.DataFrame({
        "Site": ["JobKorea"] * len(company_list),
        "Col_Company": company_list,
        "Col_Recruit": recruit_list,
        "Col_detail": detail_list,
        "Col_url": url_list
    })
    return df

def crawl_saramin():
    url = "https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=데이터분석"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    job_posts = soup.select("div.item_recruit")

    company_list, recruit_list, detail_list, url_list = [], [], [], []

    for post in job_posts:
        company = post.select_one('div.area_corp > strong.corp_name > a')
        company_name = company.text.strip() if company else None

        recruit_span = post.select_one('div.area_job h2.job_tit > a > span')
        recruit_title = recruit_span.text.strip() if recruit_span else None

        info_items = post.select('div.job_condition span')
        details = [item.text.strip() for item in info_items]
        detail_str = "[" + ", ".join(details) + "]" if details else "[]"

        title_tag = post.select_one('div.area_job h2.job_tit > a')
        href = title_tag['href'] if title_tag and title_tag.has_attr('href') else None
        full_url = "https://www.saramin.co.kr" + href if href else None

        company_list.append(company_name)
        recruit_list.append(recruit_title)
        detail_list.append(detail_str)
        url_list.append(full_url)

    df = pd.DataFrame({
        "Site": ["Saramin"] * len(company_list),
        "Col_Company": company_list,
        "Col_Recruit": recruit_list,
        "Col_detail": detail_list,
        "Col_url": url_list
    })
    return df

st.title("Title")

if st.button("Recruit Searching"):

    df1 = crawl_jobkorea()
    df2 = crawl_saramin()

    df_total = pd.concat([df1, df2], ignore_index=True)

    st.dataframe(df_total)

    count_df = df_total['Site'].value_counts().reset_index()
    count_df.columns = ['Site', 'Count']
    count_df['Ratio'] = round(count_df['Count'] / count_df['Count'].sum() * 100, 2)

    st.dataframe(count_df)

    st.subheader("Recruitment Ratio")
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        count_df['Count'],
        labels=count_df['Site'],
        autopct='%1.1f%%',
        startangle=90,
        textprops=dict(color="w")
    )
    ax.axis('equal')
    ax.legend(wedges, count_df['Site'], title="Site", loc="upper right", bbox_to_anchor=(1, 1))
    st.pyplot(fig)
else:
    st.write("")
