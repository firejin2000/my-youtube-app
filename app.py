import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 구글 API 키 세팅
API_KEY = "AIzaSyAktdLVvq7o4P6fzHyDf8Ep_TdoMyrK9og"

def youtube_search(keyword):
    """구글 공식 API를 이용해 유튜브 실시간 검색 결과를 가져오는 함수"""
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        request = youtube.search().list(
            q=keyword,
            part="snippet",
            type="video",
            maxResults=5
        )
        response = request.execute()
        
        results = []
        for item in response.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            channel_title = item["snippet"]["channelTitle"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            results.append({
                "title": title,
                "channel": channel_title,
                "link": link,
                "id": video_id
            })
        return results
    except HttpError as e:
        st.error(f"❌ 유튜브 API 에러 발생: {e}")
        return None

# -----------------------------------------------------------------
# 🌐 웹 UI 화면 구성 (스마트폰/모바일 최적화 레이아웃)
# -----------------------------------------------------------------
st.set_page_config(page_title="유튜브 실시간 검색기", page_icon="🎬", layout="centered")

st.title("🎬 실시간 유튜브 검색 시스템")
st.caption("발표 시연 및 취향 분석 알고리즘 플랫폼 ver 3.0")
st.markdown("---")

# 검색창 컴포넌트
search_keyword = st.text_input("🔍 검색할 키워드를 입력하고 엔터를 누르세요:", placeholder="예: 백종원, 우주 과학, 플레이리스트").strip()

if search_keyword:
    with st.spinner(f"🚀 실제 유튜브 서버에서 '{search_keyword}' 검색 중..."):
        search_results = youtube_search(search_keyword)

    if search_results:
        st.success(f"✨ 총 {len(search_results)}개의 실시간 영상을 찾았습니다!")
        
        # 👑 1위 영상은 상단에 큰 비디오 플레이어로 바로 배치 (웹 자동 재생 대용)
        st.markdown("### 🏆 취향 추천 1위 영상")
        st.video(search_results[0]['link'])
        st.markdown(f"**제목**: {search_results[0]['title']}  \n**채널**: {search_results[0]['channel']}")
        st.markdown(f"[🔗 유튜브 앱에서 열기]({search_results[0]['link']})")
        
        st.markdown("---")
        
        # 2위~5위 영상은 아래에 깔끔한 리스트 카드로 출력
        st.markdown("### 🔍 연관 검색 결과")
        for index, video in enumerate(search_results[1:], start=2):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    # 썸네일 이미지 표시
                    st.image(f"https://img.youtube.com/vi/{video['id']}/mqdefault.jpg", use_container_width=True)
                with col2:
                    st.markdown(f"**{index}위. {video['title']}**")
                    st.caption(f"📺 채널명: {video['channel']}")
                    st.markdown(f"[▶️ 영상 보러가기]({video['link']})")
                st.markdown("-" * 30)
    else:
        st.warning("❌ 검색 결과가 없거나 API 제한량이 초과되었습니다.")