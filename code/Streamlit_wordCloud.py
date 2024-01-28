#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
import googleapiclient.discovery
import pandas as pd
from konlpy.tag import Okt

import jpype
from collections import Counter
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

### 폰트 설정 라이브러리
from matplotlib import font_manager, rc

### 폰트 설정
plt.rc("font", family="Malgun Gothic")

### 마이너스기호 설정
plt.rcParams["axes.unicode_minus"] = False
import streamlit as st
# from streamlit_option_menu import option_menu


# In[7]:


def word_cloud():
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY="AIzaSyCGHrcNmSoUKoRGosiIShFLW9o69acZwi4"
    
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)
    
    request = youtube.commentThreads().list(
        part="snippet",
        videoId="5E9zOGX3oMo",
        maxResults=500
    )
    
    comments = []
    
    # Execute the request.
    response = request.execute()
    
    # Get the comments from the response.
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        public = item['snippet']['isPublic']
        comments.append([
            comment['authorDisplayName'],
            comment['publishedAt'],
            comment['likeCount'],
            comment['textOriginal'],
            public
        ])
    
    while (1 == 1):
      try:
       nextPageToken = response['nextPageToken']
      except KeyError:
       break
      nextPageToken = response['nextPageToken']
      # Create a new request object with the next page token.
      nextRequest = youtube.commentThreads().list(part="snippet", videoId="5E9zOGX3oMo", maxResults=500, pageToken=nextPageToken)
      # Execute the next request.
      response = nextRequest.execute()
      # Get the comments from the next response.
      for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        public = item['snippet']['isPublic']
        comments.append([
            comment['authorDisplayName'],
            comment['publishedAt'],
            comment['likeCount'],
            comment['textOriginal'],
            public
        ])
    
    df = pd.DataFrame(comments, columns=['author', 'updated_at', 'like_count', 'text','public'])
    df.info() 
    max_like_count = df['like_count'].max()
    max_like_text = df[df['like_count'] == max_like_count]['text'].values[0]
    print(max_like_text)
    max_like_index = df[df['like_count'] == max_like_count].index[0]
    print(max_like_index)
    save_path="./data/all_comments.csv"
    df.to_csv(save_path, index=False)
    save_path="./data/all_comments.csv"
    df1=pd.read_csv(save_path)    
    okt = Okt()
    all_comment = []
    
    for cmt in df["text"] :
        # print(okt.nouns(cmt))
        ### extend() : 리스트에 값만 추출하여 확장해서 추가하는 방식
        #  - append() : 리스트에 형태(type) 자체를 추가하는 방식
        all_comment.extend(okt.nouns(cmt))
    
    all_comment2 = [w for w in all_comment if len(w) > 1]
    # all_comment2
    all_comment_count = Counter(all_comment2)

    all_top_70 = {}
    for k, v in all_comment_count.most_common(70):
        all_top_70[k] = v
    
    all_top_70 = {k:v for k, v in all_comment_count.most_common(70)}
    # all_top_70
    cmap = plt.get_cmap('viridis')

# Extract values and keys
    values = list(all_top_70.values())
    keys = list(all_top_70.keys())
    
    # Normalize values to use in colormap
    norm = plt.Normalize(min(values), max(values))
    
    # Create a figure and axis
    plt.figure(figsize=(20, 10))
    
    # Title
    plt.title("all 리뷰의 단어 상위 (50개) 빈도 시각화", fontsize=17)
    
    # Bar graph with gradient color
    for key, value in zip(keys, values):
        # Additional condition to skip "태양광" or "전기"
        if key == "태양광" or key == "전기":
            continue
        
        color = cmap(norm(value))
        plt.bar(key, value, color=color)
    
    # x-axis and y-axis labels
    plt.xlabel("리뷰 명사")
    plt.ylabel("빈도(count)")
    
    # Adjust x-axis labels rotation
    plt.xticks(rotation=70)
    
    # Show the graph
    plt.show()
    
    st.success('📊 Graphical view of the top 50 word frequencies! 📈')
    st.pyplot(plt)
    # selected_value = st.selectbox('Select Language', ['English','Korean'])
    # if selected_value == 'English':
    #     st.info("""In the context of this analysis, the chosen YouTube video has been selected, 
    #         and all accompanying comments have been systematically extracted and stored in a CSV file. 
    #         Subsequent to this extraction, a comprehensive word analysis has been conducted to discern
    #         patterns and facilitate psychological analysis.""")
    # elif selected_value == 'Korean':
    #     st.text("""
    #             이 분석의 맥락에서는 선택된 YouTube 비디오가 선별되었으며, 그와 관련된 모든 댓글들이 체계적으로 추출되어
    #             CSV 파일에 저장되었습니다. 이러한 추출 후에는 패턴을 파악하고 심리 분석을 용이하게 하기 위해 포괄적인
    #             단어 분석이 진행되었습니다.
    #             """)


    exclude_words = ["태양광", "전기"]

    
    # Filter out excluded words
    filtered_top_70 = {word: count for word, count in all_top_70.items() if word not in exclude_words}
    
    # WordCloud configuration
    plt.figure(figsize=(8, 8))
    plt.title("리뷰 단어 워드클라우드 시각화")
    font_path = "C:/Windows/Fonts/malgunsl.ttf"
    wc = WordCloud(
        font_path=font_path,
        background_color="ivory",
        width=800,
        height=600
    )
    
    # Generate WordCloud from filtered frequencies
    cloud = wc.generate_from_frequencies(filtered_top_70)
    
    # Display WordCloud image
    plt.imshow(cloud)
    plt.axis("off")
    plt.savefig("./img/리뷰_단어_워드클라우드_시각화.png")
    plt.show()
    
    st.success('🌈 Word cloud visualization of review word frequencies! 📊')

    st.pyplot(plt)
    
    with st.expander("Expand to see the Analysis 📊", expanded=True):
        selected_value = st.selectbox('Select a language to view the Word Cloud Analysis: ', ['English','Korean'])
        if selected_value == 'English':
            st.text("1. Key words such as 'government', 'generation', 'power', 'production', 'facilities', 'issues', 'policy', 'momentum', 'Moon Jae-in', 'storage', etc., represent topics related to energy generation in Korea.\n"
            "2. Government and Generation Policy: Words like 'government' and 'policy' have high frequencies, and the mention of 'Moon Jae-in' suggests opinions related to the role of the Korean government and policy formulation for energy generation.\n"
            "3. Words like 'generation', 'power', 'production', 'energy', etc., emerged as significant keywords related to energy generation in Korea, indicating the country's focus and importance on energy generation and power production.\n"
            "4. Energy Generation Facilities and Storage Technology: Words like 'facilities', 'power plant', 'hydrogen', 'regeneration', 'nuclear power', 'transmission', 'facilities', 'renewable energy', etc., indicate keywords related to energy generation facilities. The mention of 'storage' reflects an interest in energy storage technology.\n"
            "5. Regional Issues: Words like 'Jeolla-do', 'Honam region', 'Honam', etc., represent issues related to Korea's regional characteristics. There is a possibility that issues related to energy generation in specific regions are mentioned.\n"
            "6. Environment and Issues: The word 'environment' along with words like 'issues', 'inadequate', 'coal', 'pollution', etc., reflects concerns and issues related to environmental problems and inadequate policies in the context of energy generation.\n"
            "7. Other Issues: Words like 'price', 'increase', 'efficiency', 'permit', 'plan', 'deficit', etc., indicate issues related to the economic aspects of energy generation. Terms like price, efficiency, and permits showcase the relevance between energy policy and economic activities.\n"
            "8. Through the above analysis, it is evident that the provided word cloud reflects various topics and issues related to energy generation in Korea. This analysis can help understand opinions and issues related to energy policy formulation and serve as a basis for more effective policies and improvement strategies."
            )
        elif selected_value == 'Korean':
            st.text("""
            1. 주요 단어들인 '정부', '발전', '전력', '생산', '시설', '문제', '정책', '기세', '문재인', '저장' 등은 한국의 에너지 발전과 관련된 주제들을 나타내고 있습니다.
            2. 정부와 발전 정책: '정부'와 '정책'이라는 단어들이 빈도수가 높게 나타나며, '문재인'이라는 인물도 언급되었습니다. 이는 한국 정부의 역할과 에너지 발전에 대한 정책 수립과 관련된 의견들을 나타냅니다.
            3. '발전', '전력', '생산', '에너지' 등의 단어들은 한국의 에너지 발전과 관련된 주요 키워드로 나타났습니다. 이는 한국에서 에너지 발전과 전력 생산에 대한 관심과 중요성을 보여줍니다.
            4. 에너지 발전 시설과 저장 기술: '시설', '발전소', '수소', '재생', '원전', '송전', '설비', '신재생에너지' 등의 단어들은 에너지 발전 시설과 관련된 키워드로 나타났습니다. '저장'이라는 단어는 에너지 저장 기술에 대한 관심을 보여줍니다.
            5. 지역과 관련된 이슈: '전라도', '호남지방', '호남' 등의 단어들은 한국의 지역적인 특성과 관련된 이슈를 나타냅니다. 지역별 에너지 발전과 관련된 문제들이 언급되었을 가능성이 있습니다.
            6. 환경과 문제: '환경'이라는 단어와 함께 '문제', '부실', '석탄', '오염' 등의 단어들이 나타났습니다. 이는 에너지 발전과 관련하여 환경 문제와 부실한 정책 등에 대한 우려와 이슈를 반영합니다.
            7. 기타 이슈: '가격', '인상', '효율', '허가', '계획', '적자' 등의 단어들은 에너지 발전과 관련된 경제적인 측면과 이슈들을 나타냅니다. 가격, 효율, 허가 등의 단어들은 에너지 정책과 경제 활동 사이의 관련성을 보여줍니다.
            8. 위의 분석을 통해 주어진 워드 클라우드 결과에는 한국의 에너지 발전과 관련된 다양한 주제와 이슈들이 반영되어 있음을 알 수 있습니다. 이러한 분석을 통해 에너지 정책 수립과 관련된 의견 및 이슈들을 파악할 수 있으며, 이를 바탕으로 보다 효과적인 정책과 개선 방안을 모색할 수 있습니다.
            """)



def main():
    
    st.set_page_config(layout="wide")
    st.subheader("🧠💭 워드 클라우드로 사람의 심리를 2초만에 분석하기!")
    st.subheader('🎯 Objective and Methodology 📊')
    with st.expander("View the Analysis", expanded=True):
        
        selected_value = st.selectbox('View in', ['English', 'Korean'])
        if selected_value == 'English':
            st.text("""
            📝 For this analysis, a specific YouTube video was selected, and its content, along with all associated comments, 
            were systematically extracted and stored in a CSV file. Following the extraction process, a thorough 
            word analysis was conducted to identify patterns and enable psychological analysis.
            """)
        elif selected_value == 'Korean':
            st.text("""
                📝 이 분석을 위해 특정 YouTube 동영상이 선택되었으며, 해당 동영상의 콘텐츠와 모든 관련 댓글은 체계적으로 추출되어 CSV 파일에 저장되었습니다. 
                추출 과정 이후에는 철저한 단어 분석이 수행되어 패턴을 식별하고 심리 분석을 가능하게 했습니다.
                """)
    
    col1, col2= st.columns([1, 1])
    with col1:            
        st.image('./yt.png')
        

    with col2:
        st.subheader("The Comment with the most like is: ")
        st.warning("인증 필요한 산업에 전력을 최대한 보내줘야지.....")
   
    word_cloud()

     
               
 



if __name__ == '__main__':
    main()



# In[ ]:




