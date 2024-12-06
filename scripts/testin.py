import os
import cv2
import time
import torch
import joblib
import numpy as np
import mysql.connector
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.metrics.pairwise import cosine_similarity
import argparse
from mysql.connector import pooling
import gc

parser = argparse.ArgumentParser(description="Mengambil argumen kelas dan mata kuliah")
parser.add_argument("--selected_class_id", type=int, help="ID kelas yang dipilih")
parser.add_argument("--selected_class_name", type=str, help="Nama kelas yang dipilih")
parser.add_argument(
    "--selected_course_id", type=int, help="ID mata kuliah yang dipilih"
)
parser.add_argument(
    "--selected_course_name", type=str, help="Nama mata kuliah yang dipilih"
)
args = parser.parse_args()

selected_class_id = args.selected_class_id
selected_class_name = args.selected_class_name
selected_course_id = args.selected_course_id
selected_course_name = args.selected_course_name

dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "student_management",
}

pool = pooling.MySQLConnectionPool(
    pool_name="student_management_pool",
    pool_size=5,
    **dbconfig,
)

conn = pool.get_connection()
cursor = conn.cursor()

device = "cuda" if torch.cuda.is_available() else "cpu"
inception_resnet = InceptionResnetV1(pretrained="vggface2").eval().to(device)
svm_model = joblib.load("D:/Project/StudentManagement/scripts/Model/svm_model.pkl")
label_encoder_classes = np.load(
    "D:/Project/StudentManagement/scripts/Model/label_encoder_classes.npy"
)
known_embeddings = np.load(
    "D:/Project/StudentManagement/scripts/Model/known_face_embeddings.npy"
)

mtcnn = MTCNN(
    keep_all=True,
    device=device,
    selection_method="largest",
    post_process=False,
)

folderModePath = "D:/Project/StudentManagement/scripts/Resources/Modes"
modePathList = os.listdir(folderModePath)
imgBackground = cv2.imread(
    "D:/Project/StudentManagement/scripts/Resources/background.png"
)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

cap = cv2.VideoCapture(0)
cap.set(3, 960)
cap.set(4, 720)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
# cv2.namedWindow("Face Recognition", cv2.WINDOW_FULLSCREEN)
cv2.resizeWindow("Face Recognition", 1920, 1080)


THRESHOLD = 0.7
PRINT_DELAY = 1.5
MODE_DISPLAY_DURATION = 3

detected_name = None
detected_time = None
modeType = 0
predicted_name = "Unknown"
mode_start_time = None
current_student_info = None
current_student_img = None


def get_student_info(predicted_name):
    try:
        query = """
            SELECT m.*, k.nama AS kelas_nama
            FROM `mahasiswas` m
            JOIN `kelas` k ON m.kelas_id = k.id
            WHERE m.id LIKE %s;
        """
        cursor.execute(query, (f"%{predicted_name}%",))

        student_info = cursor.fetchone()
        if student_info:
            return student_info
        else:
            print("Mahasiswa tidak ditemukan.")
            return None

    except mysql.connector.Error as err:
        print(f"Terjadi error: {err}")


def insert_absensi(kelas_id, mata_kuliah_id, mahasiswa_id):
    try:
        today_date = datetime.today().strftime("%Y-%m-%d")

        query_check = """
            SELECT * FROM `absensis`
            WHERE `kelas_id` = %s
            AND `mata_kuliah_id` = %s
            AND `mahasiswa_id` = %s
            AND DATE(`tanggal`) LIKE %s;
        """

        cursor.execute(
            query_check, (kelas_id, mata_kuliah_id, mahasiswa_id, f"%{today_date}%")
        )
        existing_record = cursor.fetchone()

        if existing_record:
            print("Data absensi sudah ada untuk tanggal tersebut.")
            return False

        query_insert = """
            INSERT INTO `absensis` (`kelas_id`, `mata_kuliah_id`, `mahasiswa_id`)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query_insert, (kelas_id, mata_kuliah_id, mahasiswa_id))

        conn.commit()
        print("Data berhasil ditambahkan.")
        return True

    except mysql.connector.Error as err:
        print(f"Terjadi error: {err}")
        return False


def add_text_with_custom_font(
    image,
    text,
    position,
    font_size,
    text_color=(255, 255, 255),
    font_path="D:/Project/StudentManagement/scripts/Font/SFMedium.OTF",
):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font tidak ditemukan, menggunakan font default.")
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=text_color)
    image_with_text = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return image_with_text


def get_box_area(box):
    width = box[2] - box[0]
    height = box[3] - box[1]
    return width * height


frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    frame_counter += 1
    if frame_counter % 5 != 0:
        continue

    current_time = time.time()
    frame_with_background = imgBackground.copy()

    if modeType in [2, 3] and mode_start_time is not None:
        if current_time - mode_start_time >= MODE_DISPLAY_DURATION:
            modeType = 0
            mode_start_time = None
            current_student_info = None
            current_student_img = None

    frame_with_background[65 : 65 + 950, 1210 : 1210 + 621] = imgModeList[modeType]

    resized_frame = cv2.resize(frame, (960, 720))
    frame_with_background[242 : 242 + 720, 80 : 80 + 960] = resized_frame

    frame_with_background = add_text_with_custom_font(
        frame_with_background,
        f"{selected_class_name} - {selected_course_name}",
        (20, 35),
        35,
        (65, 65, 65),
        "D:/Project/StudentManagement/scripts/Font/SFBold.OTF",
    )

    if (
        modeType in [2, 3]
        and current_student_info is not None
        and current_student_img is not None
    ):
        frame_with_background = add_text_with_custom_font(
            frame_with_background,
            current_student_info["id"],
            (1430, 643),
            35,
            (65, 65, 65),
        )
        frame_with_background = add_text_with_custom_font(
            frame_with_background,
            current_student_info["name"],
            (1430, 767),
            35,
            (65, 65, 65),
        )
        frame_with_background = add_text_with_custom_font(
            frame_with_background,
            current_student_info["class"],
            (1430, 893),
            35,
            (65, 65, 65),
        )
        frame_with_background[197 : 197 + 370, 1335 : 1335 + 370] = current_student_img

    if modeType == 0:
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs = mtcnn.detect(img_rgb)

        if boxes is not None and len(boxes) > 0:
            areas = [get_box_area(box) for box in boxes]
            closest_face_idx = np.argmax(areas)
            box = boxes[closest_face_idx]

            x_min, y_min, x_max, y_max = map(int, box)
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(frame.shape[1], x_max)
            y_max = min(frame.shape[0], y_max)

            face = img_rgb[y_min:y_max, x_min:x_max]
            if face.size != 0:
                face_resized = cv2.resize(face, (160, 160))
                face_tensor = (
                    torch.from_numpy(face_resized).permute(2, 0, 1).float() / 255.0
                ).to(device)

                with torch.no_grad():
                    face_embedding = (
                        inception_resnet(face_tensor.unsqueeze(0))
                        .detach()
                        .cpu()
                        .numpy()
                    )
                    predicted_label = svm_model.predict(face_embedding)[0]
                    predicted_name = label_encoder_classes[predicted_label]

                    similarity_scores = cosine_similarity(
                        face_embedding, known_embeddings
                    )

                if np.max(similarity_scores) < THRESHOLD:
                    predicted_name = "Unknown"

                bbox = (160 + x_min, 320 + y_min, 180 + x_max, 330 + y_max)
                cv2.rectangle(
                    frame_with_background,
                    (bbox[0], bbox[1]),
                    (bbox[2], bbox[3]),
                    (0, 255, 0),
                    2,
                )

                if detected_name == predicted_name and predicted_name != "Unknown":
                    frame_with_background[65 : 65 + 950, 1210 : 1210 + 621] = (
                        imgModeList[1]
                    )
                    if current_time - detected_time >= PRINT_DELAY:
                        print(f"Name detected: {predicted_name}")
                        detected_time = current_time

                        studentInfo = get_student_info(predicted_name)
                        print(studentInfo)

                        if studentInfo[6] == selected_class_name:
                            imgPath = f"D:/Project/StudentManagement/scripts/Images/{predicted_name}/0.jpg"
                            if not os.path.exists(imgPath):
                                print(
                                    f"Error: No such file '{imgPath}' in local storage."
                                )
                                continue

                            imgStudent = cv2.imread(imgPath)
                            imgStudent_resized = cv2.resize(imgStudent, (370, 370))

                            current_student_info = {
                                "id": str(studentInfo[0]),
                                "name": studentInfo[1],
                                "class": studentInfo[6],
                            }
                            current_student_img = imgStudent_resized

                            if insert_absensi(
                                selected_class_id, selected_course_id, studentInfo[0]
                            ):
                                modeType = 2
                            else:
                                modeType = 3

                            mode_start_time = current_time
                else:
                    detected_name = predicted_name
                    detected_time = current_time
                del face_embedding, face_tensor, face, face_resized

    cv2.imshow("Face Recognition", frame_with_background)

    gc.collect()
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

conn.close()
cursor.close()
cap.release()
cv2.destroyAllWindows()
