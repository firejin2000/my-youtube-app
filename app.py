import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime

# 1. 페이지 기본 레이아웃 및 타이틀 설정
st.set_page_config(page_title="MOONSUGOD PLATFORM", page_icon="⚡", layout="wide")

# 2. 밋밋한 화면을 화려하게 바꿔주는 네온 다크 CSS 테마 코드
st.markdown("""
    <style>
    /* 전체 배경을 세련된 딥 네온/다크 컬러로 세팅 */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* 최상단 메인 로고 및 제목 발광 효과 */
    .neon-title {
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(90deg, #ff007f, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(255, 0, 127, 0.6));
        margin-bottom: 2px;
    }
    
    /* 도메인 자막 스타일 */
    .neon-subtitle {
        text-align: center;
        color: #38bdf8 !important;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 35px;
        letter-spacing: 1px;
    }
    
    /* 검색창 컴포넌트 글로잉 테두리 디자인 */
    div.stTextInput > div {
        border-radius: 12px !important;
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.35) !important;
        background-color: #1e293b !important;
        padding: 4px;
    }
    
    /* 검색창 내부 입력 글자 색상 */
    div.stTextInput input {
        color: #ffffff !important;
        font-size: 1.1rem !important;
    }
    
    /* 비디오 리스트 카드 박스 디자인 (테두리 네온 효과) */
    .video-list-card {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid #ff007f;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 25px rgba(255, 0, 127, 0.15);
        transition: all 0.3s ease;
    }
    
    /* 마우스 올렸을 때 반응하는 애니메이션 효과 */
    .video-list-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0, 240, 255, 0.4);
        border-color: #00f0ff;
    }
    
    /* 링크 텍스트 스타일 */
    .video-link-btn {
        display: inline-block;
        color: #00f0ff !important;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
        font-size: 1.05rem;
    }
    
    /* 뱃지 및 메타데이터 스타일 */
    .meta-info {
        color: #94a3b8;
        font-size: 0.9rem;
        margin: 4px 0;
    }
    .view-count {
        color: #22c55e !important; /* 초록색 강조 */
        font-weight: 600;
    }
    .upload-date {
        color: #e2e8f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 상단 비주얼 헤더 영역 배치
st.markdown('<p class="neon-title">⚡ 문수갓 알고리즘 ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="neon-subtitle">레전드 알고리즘, 문수갓으로 영상을 즐겨보세요.</p>', unsafe_allow_html=True)

# 4. 유튜브 API 연동 및 데이터 분석 함수 정의
# ⚠️ 주의: 본인의 YouTube API KEY를 아래 따옴표 안에 정확하게 입력하셔야 작동합니다!
YOUTUBE_API_KEY = "AIzaSyAktdLVvq7o4P6fzHyDf8Ep_TdoMyrK9og"

def format_view_count(views):
    """조회수를 한국어 단위로 변환하는 함수"""
    if not views:
        return "조회수 없음"
    views = int(views)
    if views >= 100000000:
        return f"조회수 {views // 100000000}억회"
    elif views >= 10000:
        return f"조회수 {views // 10000}만회"
    elif views >= 1000:
        return f"조회수 {views // 1000}천회"
    else:
        return f"조회수 {views}회"

def format_published_at(pub_date_str):
    """업로드 날짜를 현재 시점 기준으로 경과 시간 계산하는 함수"""
    try:
        # ISO 8601 포맷 파싱 (끝의 'Z' 처리)
        pub_date = datetime.strptime(pub_date_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
        now = datetime.utcnow()
        diff = now - pub_date
        
        if diff.days >= 365:
            return f"{diff.days // 365}년 전"
        elif diff.days >= 30:
            return f"{diff.days // 30}달 전"
        elif diff.days >= 7:
            return f"{diff.days // 7}주 전"
        elif diff.days >= 1:
            return f"{diff.days}일 전"
        else:
            hours = diff.seconds // 3600
            if hours >= 1:
                return f"{hours}시간 전"
            else:
                return "방금 전"
    except:
        return "알 수 없는 날짜"

def youtube_search(query):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        
        # 1차 검색: 영상들의 고유 ID 값 가져오기
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=5
        )
        response = request.execute()
        
        video_ids = [item['id']['videoId'] for item in response.get("items", [])]
        if not video_ids:
            return []
            
        # 2차 조회: 고유 ID 리스트를 기반으로 상세 정보(조회수 등)를 통째로 가져오기
        stats_request = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics"
        )
        stats_response = stats_request.execute()
        
        results = []
        for item in stats_response.get("items", []):
            views = item['statistics'].get('viewCount', 0)
            pub_date = item['snippet']['publishedAt']
            
            results.append({
                'title': item['snippet']['title'],
                'link': f"https://www.youtube.com/watch?v={item['id']}",
                'channel': item['snippet']['channelTitle'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'views': format_view_count(views),
                'date': format_published_at(pub_date)
            })
        return results
    except Exception as e:
        st.error("⚠️ 유튜브 API 엔진 연결에 실패했습니다. 키를 확인해 주세요.")
        return []

# 5. 검색창 컴포넌트
search_keyword = st.text_input("🔍 검색할 키워드를 입력하고 엔터를 누르세요:", placeholder="예: 백종원, 우주 과학, 플레이리스트")

# 6. 실시간 검색 결과 매핑 시스템
if search_keyword:
    with st.spinner(f"🚀 실제 유튜브 서버에서 '{search_keyword}' 데이터 수집 중..."):
        search_results = youtube_search(search_keyword)
        
    if search_results:
        st.success(f"✨ 총 {len(search_results)}개의 실시간 영상을 찾았습니다!")
        
        # 👑 1위 영상은 상단에 큰 비디오 플레이어로 바로 배치
        st.markdown("### 🏆 취향 추천 1위 영상")
        st.video(search_results[0]['link'])
        
        # 1위 메타데이터 출력 (조회수, 경과 시간 뱃지 형태 적용)
        st.markdown(f"### **{search_results[0]['title']}**")
        st.markdown(f"**📺 채널**: {search_results[0]['channel']} | 🔥 **{search_results[0]['views']}** | 🕒 {search_results[0]['date']}")
        st.markdown(f"[🔗 유튜브 앱에서 열기]({search_results[0]['link']})")
        
        st.markdown("---")
        
        # 🔍 2위~5위 영상은 아래에 깔끔한 격자형(Grid) 네온 리스트 카드로 출력
        st.markdown("### 🔍 연관 검색 결과")
        
        # 좌우 2열로 나누어 세련되게 배치
        cols = st.columns(2)
        
        for index, video in enumerate(search_results[1:], start=2):
            with cols[(index % 2)]:
                st.markdown(f"""
                    <div class="video-list-card">
                        <img src="{video['thumbnail']}" style="width:100%; border-radius:8px; margin-bottom:12px;">
                        <h4 style="color:#ffffff; margin:0 0 8px 0; font-size:1.15rem; line-height:1.4;">{index}위. {video['title']}</h4>
                        <p class="meta-info">📺 채널: {video['channel']}</p>
                        <p class="meta-info">🔥 <span class="view-count">{video['views']}</span> &nbsp;|&nbsp; 🕒 <span class="upload-date">{video['date']}</span></p>
                        <a href="{video['link']}" target="_blank" class="video-link-btn">▶ 실시간 영상 시청하기</a>
                    </div>
                """, unsafe_allow_html=True)

# 7. 사이트 하단 푸터 영역
st.markdown("<br><br><hr style='border-color: #334155;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem; font-weight: 500;'>Powered by moonsugod | Data Layer Optimized</p>", unsafe_allow_html=True)
