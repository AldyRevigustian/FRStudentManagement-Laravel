import gc
import os
import cv2
import time
import torch
import joblib
import argparse
import numpy as np
import mysql.connector
from datetime import datetime
from mysql.connector import pooling
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.metrics.pairwise import cosine_similarity


class FaceRecognitionSystem:
    def __init__(self):
        self.parse_arguments()
        self.setup_database()
        self.initialize_models()
        self.setup_camera()
        self.load_resources()
        self.initialize_variables()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Mengambil argumen kelas dan mata kuliah"
        )
        parser.add_argument(
            "--selected_class_id", type=int, help="ID kelas yang dipilih"
        )
        parser.add_argument(
            "--selected_class_name", type=str, help="Nama kelas yang dipilih"
        )
        parser.add_argument(
            "--selected_course_id", type=int, help="ID mata kuliah yang dipilih"
        )
        parser.add_argument(
            "--selected_course_name", type=str, help="Nama mata kuliah yang dipilih"
        )
        args = parser.parse_args()

        self.selected_class_id = args.selected_class_id
        self.selected_class_name = args.selected_class_name
        self.selected_course_id = args.selected_course_id
        self.selected_course_name = args.selected_course_name

    def setup_database(self):
        dbconfig = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "student_management",
        }
        self.pool = pooling.MySQLConnectionPool(
            pool_name="student_management_pool",
            pool_size=5,
            **dbconfig,
        )
        self.conn = self.pool.get_connection()
        self.cursor = self.conn.cursor()

    def initialize_models(self):
        self.device = "cpu"
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.device = torch.device("cuda:0")
            torch.cuda.set_device(self.device)

        self.inception_resnet = (
            InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        )
        self.svm_model = joblib.load(
            "D:/Project/StudentManagement/scripts/Model/svm_model.pkl"
        )
        self.label_encoder_classes = np.load(
            "D:/Project/StudentManagement/scripts/Model/label_encoder_classes.npy"
        )
        self.known_embeddings = np.load(
            "D:/Project/StudentManagement/scripts/Model/known_face_embeddings.npy"
        )
        self.mtcnn = MTCNN(
            keep_all=True,
            device=self.device,
            selection_method="largest",
            post_process=False,
        )

        self.embedding_cache = {}

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 960)
        self.cap.set(4, 720)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
        # cv2.namedWindow("Face Recognition", cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow("Face Recognition", 1920, 1080)

    def load_resources(self):
        self.folderModePath = "D:/Project/StudentManagement/scripts/Resources/Modes"
        self.modePathList = os.listdir(self.folderModePath)
        self.imgBackground = cv2.imread(
            "D:/Project/StudentManagement/scripts/Resources/background.png"
        )
        self.imgModeList = [
            cv2.imread(os.path.join(self.folderModePath, path))
            for path in self.modePathList
        ]

    def initialize_variables(self):
        self.THRESHOLD = 0.7
        self.PRINT_DELAY = 1.2
        self.MODE_DISPLAY_DURATION = 3
        self.detected_name = None
        self.detected_time = None
        self.modeType = 0
        self.predicted_name = "Unknown"
        self.mode_start_time = None
        self.current_student_info = None
        self.current_student_img = None
        self.frame_counter = 0
        self.max_cache_size = 1000
        # self.cache_cleanup_threshold = 0.8


    def get_student_info(self, predicted_name):
        try:
            query = """
                SELECT m.*, k.nama AS kelas_nama
                FROM `mahasiswas` m
                JOIN `kelas` k ON m.kelas_id = k.id
                WHERE m.id LIKE %s;
            """
            self.cursor.execute(query, (f"%{predicted_name}%",))
            student_info = self.cursor.fetchone()
            if student_info:
                return student_info
            else:
                print("Mahasiswa tidak ditemukan.")
                return None
        except mysql.connector.Error as err:
            print(f"Terjadi error: {err}")

    def insert_absensi(self, kelas_id, mata_kuliah_id, mahasiswa_id):
        try:
            today_date = datetime.today().strftime("%Y-%m-%d")
            query_check = """
                SELECT * FROM `absensis`
                WHERE `kelas_id` = %s
                AND `mata_kuliah_id` = %s
                AND `mahasiswa_id` = %s
                AND DATE(`tanggal`) LIKE %s;
            """
            self.cursor.execute(
                query_check, (kelas_id, mata_kuliah_id, mahasiswa_id, f"%{today_date}%")
            )
            existing_record = self.cursor.fetchone()

            if existing_record:
                print("Data absensi sudah ada untuk tanggal tersebut.")
                return False

            query_insert = """
                INSERT INTO `absensis` (`kelas_id`, `mata_kuliah_id`, `mahasiswa_id`)
                VALUES (%s, %s, %s);
            """
            self.cursor.execute(query_insert, (kelas_id, mata_kuliah_id, mahasiswa_id))
            self.conn.commit()
            print("Data berhasil ditambahkan.")
            return True

        except mysql.connector.Error as err:
            print(f"Terjadi error: {err}")
            return False

    def add_text_with_custom_font(
        self,
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
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    @staticmethod
    def get_box_area(box):
        width = box[2] - box[0]
        height = box[3] - box[1]
        return width * height

    def process_face(self, frame, img_rgb, boxes):
        areas = [self.get_box_area(box) for box in boxes]
        closest_face_idx = np.argmax(areas)
        box = boxes[closest_face_idx]

        x_min, y_min, x_max, y_max = map(int, box)
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(frame.shape[1], x_max)
        y_max = min(frame.shape[0], y_max)

        face = img_rgb[y_min:y_max, x_min:x_max]
        if face.size == 0:
            return None

        face_resized = cv2.resize(face, (160, 160), interpolation=cv2.INTER_LINEAR)

        face_tensor = (
            torch.from_numpy(face_resized).permute(2, 0, 1).float() / 255.0
        ).to(self.device)

        with torch.no_grad():
            face_embedding = (
                self.inception_resnet(face_tensor.unsqueeze(0).to(self.device))
                .detach()
                .cpu()
                .numpy()
            )
            predicted_label = self.svm_model.predict(face_embedding)[0]
            predicted_name = self.label_encoder_classes[predicted_label]

            similarity_scores = cosine_similarity(face_embedding, self.known_embeddings)

        embedding_key = str(face_embedding.tobytes())
        if embedding_key in self.embedding_cache:
            predicted_name = self.embedding_cache[embedding_key]
        else:
            predicted_label = self.svm_model.predict(face_embedding)[0]
            predicted_name = self.label_encoder_classes[predicted_label]
            if len(self.embedding_cache) > self.max_cache_size:
                self.embedding_cache.clear()
            self.embedding_cache[embedding_key] = predicted_name

        if np.max(similarity_scores) < self.THRESHOLD:
            predicted_name = "Unknown"

        bbox = (160 + x_min, 320 + y_min, 180 + x_max, 330 + y_max)

        if self.device != "cpu" and self.frame_counter % 30 == 0:
            torch.cuda.empty_cache()

        return predicted_name, bbox, face_embedding, face_tensor, face, face_resized

    def update_display(self, frame_with_background):
        if (
            self.modeType in [2, 3]
            and self.current_student_info is not None
            and self.current_student_img is not None
        ):
            frame_with_background = self.add_text_with_custom_font(
                frame_with_background,
                self.current_student_info["id"],
                (1430, 643),
                35,
                (65, 65, 65),
            )
            frame_with_background = self.add_text_with_custom_font(
                frame_with_background,
                self.current_student_info["name"],
                (1430, 767),
                35,
                (65, 65, 65),
            )
            frame_with_background = self.add_text_with_custom_font(
                frame_with_background,
                self.current_student_info["class"],
                (1430, 893),
                35,
                (65, 65, 65),
            )
            frame_with_background[197 : 197 + 370, 1335 : 1335 + 370] = (
                self.current_student_img
            )

        return frame_with_background

    def process_frame(self, frame, current_time):
        frame_with_background = self.imgBackground.copy()

        if self.modeType in [2, 3] and self.mode_start_time is not None:
            if current_time - self.mode_start_time >= self.MODE_DISPLAY_DURATION:
                self.modeType = 0
                self.mode_start_time = None
                self.current_student_info = None
                self.current_student_img = None

        frame_with_background[65 : 65 + 950, 1210 : 1210 + 621] = self.imgModeList[
            self.modeType
        ]
        resized_frame = cv2.resize(frame, (960, 720))
        frame_with_background[242 : 242 + 720, 80 : 80 + 960] = resized_frame

        frame_with_background = self.add_text_with_custom_font(
            frame_with_background,
            f"{self.selected_class_name} - {self.selected_course_name}",
            (20, 35),
            35,
            (65, 65, 65),
            "D:/Project/StudentManagement/scripts/Font/SFBold.OTF",
        )

        frame_with_background = self.update_display(frame_with_background)

        if self.modeType == 0:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, probs = self.mtcnn.detect(img_rgb)

            if boxes is not None and len(boxes) > 0:
                result = self.process_face(frame, img_rgb, boxes)
                if result is not None:
                    (
                        predicted_name,
                        bbox,
                        face_embedding,
                        face_tensor,
                        face,
                        face_resized,
                    ) = result
                    cv2.rectangle(
                        frame_with_background,
                        (bbox[0], bbox[1]),
                        (bbox[2], bbox[3]),
                        (0, 255, 0),
                        2,
                    )

                    if (
                        self.detected_name == predicted_name
                        and predicted_name != "Unknown"
                    ):
                        frame_with_background[65 : 65 + 950, 1210 : 1210 + 621] = (
                            self.imgModeList[1]
                        )
                        if current_time - self.detected_time >= self.PRINT_DELAY:
                            print(f"Name detected: {predicted_name}")
                            self.detected_time = current_time

                            studentInfo = self.get_student_info(predicted_name)
                            print(studentInfo)

                            if studentInfo[6] == self.selected_class_name:
                                imgPath = f"D:/Project/StudentManagement/scripts/Images/{predicted_name}/profile.jpg"
                                if not os.path.exists(imgPath):
                                    print(
                                        f"Error: No such file '{imgPath}' in local storage."
                                    )
                                    return frame_with_background

                                imgStudent = cv2.imread(imgPath)
                                imgStudent_resized = cv2.resize(imgStudent, (370, 370))

                                self.current_student_info = {
                                    "id": str(studentInfo[0]),
                                    "name": studentInfo[1],
                                    "class": studentInfo[6],
                                }
                                self.current_student_img = imgStudent_resized

                                if self.insert_absensi(
                                    self.selected_class_id,
                                    self.selected_course_id,
                                    studentInfo[0],
                                ):
                                    self.modeType = 2
                                else:
                                    self.modeType = 3

                                self.mode_start_time = current_time
                    else:
                        self.detected_name = predicted_name
                        self.detected_time = current_time

                    del face_embedding, face_tensor, face, face_resized

        return frame_with_background

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break

                self.frame_counter += 1
                if self.frame_counter % 3 != 0:
                    continue

                current_time = time.time()
                frame_with_background = self.process_frame(frame, current_time)
                cv2.imshow("Face Recognition", frame_with_background)

                # gc.collect()
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if self.frame_counter % 100 == 0:
                    gc.collect()

        finally:
            self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
