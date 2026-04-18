import streamlit as st
from playwright.sync_api import sync_playwright
import time

# --- CẤU HÌNH GIAO DIỆN STREAMLIT (LUMA STYLE) ---
st.set_page_config(page_title="Khảo Sát Auto", page_icon="✨", layout="centered")

# Custom CSS để làm mượt giao diện, bo góc các element
st.markdown("""
    <style>
    .stTextInput input { border-radius: 8px; }
    .stButton button { 
        border-radius: 8px; 
        background-color: #1E1E1E; 
        color: white; 
        border: 1px solid #333;
        transition: 0.3s;
    }
    .stButton button:hover {
        border-color: #666;
        background-color: #2D2D2D;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✨ Auto Survey Filler")
st.markdown("Công cụ tự động đánh giá khảo sát học phần.")

# --- FORM NHẬP LIỆU ---
with st.container():
    st.subheader("Cấu hình đánh giá")
    course_url = st.text_input("🔗 Link Form Khảo Sát", placeholder="Nhập URL của Microsoft Forms...")
    course_code = st.text_input("📚 Mã học phần", placeholder="Ví dụ: IT101...")
    
    rating_options = ["Rất không hài lòng", "Không hài lòng", "Phân vân", "Hài lòng", "Rất hài lòng"]
    target_rating = st.select_slider("🎯 Mức độ đánh giá mong muốn", options=rating_options, value="Rất hài lòng")

# --- HÀM TỰ ĐỘNG HÓA PLAYWRIGHT ---
def run_automation(url, code, rating):
    try:
        with sync_playwright() as p:
            # Khởi chạy trình duyệt (để headless=False nếu muốn xem nó tự click)
            browser = p.chromium.launch(headless=False) 
            page = browser.new_page()
            
            st.info("Đang mở trình duyệt và tải trang...")
            page.goto(url)
            
            # Đợi load xong form (tùy chỉnh thời gian đợi)
            page.wait_for_load_state('networkidle')
            
            # Giả lập điền mã học phần (Cần tìm đúng selector của ô input)
            # Ví dụ: page.get_by_placeholder("Nhập câu trả lời của bạn").fill(code)
            
            st.info(f"Đang tự động chọn mức: {rating}...")
            # Microsoft Forms thường dùng aria-label hoặc value text cho radio button
            # Cấu trúc Playwright tìm và click tất cả các nút có text tương ứng
            radio_buttons = page.locator(f"//label[contains(., '{rating}')] | //div[@aria-label='{rating}']")
            count = radio_buttons.count()
            
            for i in range(count):
                radio_buttons.nth(i).scroll_into_view_if_needed()
                radio_buttons.nth(i).click()
                time.sleep(0.1) # Delay nhỏ để tránh bị hệ thống chặn
                
            # page.get_by_text("Gửi").click() # Mở comment dòng này nếu muốn tự động Submit
            
            st.success(f"Đã hoàn thành đánh giá cho {count} tiêu chí!")
            time.sleep(2) # Giữ trình duyệt một chút để kiểm tra
            browser.close()
            
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")

# --- NÚT CHẠY ---
st.divider()
if st.button("🚀 Chạy Auto-Fill", use_container_width=True):
    if not course_url:
        st.warning("Vui lòng nhập Link Form Khảo Sát!")
    else:
        run_automation(course_url, course_code, target_rating)