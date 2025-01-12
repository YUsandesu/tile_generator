import cv2

def capture_photo():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Error] Could not open camera...")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("[Error] Could not read frame...")
        return

    cv2.imwrite('captured.jpg', frame)
    print("[Progress] Captured An Image")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_photo()