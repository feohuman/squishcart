import cv2
import streamlit as st


def qr_code_reader(image):
    qr_reader = cv2.QRCodeDetector()
    data, points, _ = qr_reader.detectAndDecode(image)
    if data:
        return data
    return None

def scan_code() -> str:
    cap = cv2.VideoCapture(0)

    frame_placeholder = st.empty()

    stop_button_pressed = st.button("Stop")

    while cap.isOpened() and not stop_button_pressed:
        ret, image = cap.read()
        if not ret:
            st.error("Can't receive frame (stream end?). Exiting ...")
            break
        decoded = qr_code_reader(image)
        if decoded:
            cap.release()
            cv2.destroyAllWindows()
            return decoded
        pretty = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(pretty)

    cap.release()
    cv2.destroyAllWindows()
    return ""

