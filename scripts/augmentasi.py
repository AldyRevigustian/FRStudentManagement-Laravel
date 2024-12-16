import os
from PIL import Image
from facenet_pytorch import MTCNN
import numpy as np
from imgaug import augmenters as iaa
import shutil
import torch


class FaceProcessor:
    def __init__(self, dataset_dir, output_dir):
        self.dataset_dir = dataset_dir
        self.output_dir = output_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.detector = MTCNN(device=self.device)

        self.seq = iaa.Sequential(
            [
                iaa.Fliplr(0.5),
                iaa.Affine(rotate=(-30, 30)),
                iaa.LinearContrast((0.9, 1.1)),
                iaa.Multiply((0.8, 1.2)),
                iaa.Grayscale(alpha=(0.0, 1.0)),
                iaa.AdditiveGaussianNoise(scale=(0, 0.05 * 255)),
                iaa.AddToHueAndSaturation((-10, 10)),
                iaa.MultiplyHueAndSaturation((0.8, 1.2)),
            ]
        )

        self._initialize_output_dir()

    def _initialize_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir)
            print(f"Directory {self.output_dir} and its contents have been cleared.")

    def detect_and_crop_face(self, image_path):
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        img_rgb = np.array(img)
        boxes, _ = self.detector.detect(img_rgb)

        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            x_min, y_min, x_max, y_max = map(int, box)
            img_cropped = img.crop((x_min, y_min, x_max, y_max))
            return img_cropped.resize((160, 160))
        return None

    def crop_profile(self, image_path, padding=0.5):
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        img_rgb = np.array(img)
        boxes, _ = self.detector.detect(img_rgb)

        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            x_min, y_min, x_max, y_max = map(int, box)

            width = x_max - x_min
            height = y_max - y_min
            pad_x = int(padding * width)
            pad_y = int(padding * height)

            x_min = max(0, x_min - pad_x)
            y_min = max(0, y_min - pad_y)
            x_max = min(img.width, x_max + pad_x)
            y_max = min(img.height, y_max + pad_y)

            img_cropped = img.crop((x_min, y_min, x_max, y_max))
            img_cropped = img_cropped.resize((370, 370))

            img_cropped_rgb = np.array(img_cropped)
            boxes_cropped, _ = self.detector.detect(img_cropped_rgb)

            if boxes_cropped is not None and len(boxes_cropped) > 0:
                print("Face detected")
                return img_cropped
        return None

    def save_profile(self, person_name):
        person_folder = os.path.join(self.dataset_dir, person_name)
        images = [f for f in os.listdir(person_folder) if f.endswith(".jpg")]

        for image_filename in images:
            image_path = os.path.join(person_folder, image_filename)
            cropped = self.crop_profile(image_path)
            if cropped is not None:
                cropped.save(os.path.join(person_folder, "profile.jpg"))
                break

    def augment_and_save(self, face, person_name, base_filename, num_augments=10):
        person_folder = os.path.join(self.output_dir, person_name)
        if not os.path.exists(person_folder):
            os.makedirs(person_folder)

        original_filename = os.path.join(person_folder, f"{base_filename}_original.jpg")
        face.save(original_filename)

        for i in range(num_augments):
            augmented_face = self.seq(image=np.array(face))

            if augmented_face is None or augmented_face.size == 0:
                print(
                    f"Warning: Empty image after augmentation for {base_filename}_aug_{i+1}"
                )
                continue

            augmented_image = Image.fromarray(augmented_face).convert("RGB")
            new_filename = os.path.join(person_folder, f"{base_filename}_aug_{i+1}.jpg")

            try:
                augmented_image.save(new_filename)
                if not self.detect_face(new_filename):
                    print(
                        f"Warning: No face detected in {new_filename}, removing image."
                    )
                    os.remove(new_filename)
            except ValueError as e:
                print(f"Error: Cannot save image {new_filename} - {e}")

    def detect_face(self, image_path):
        img = Image.open(image_path)
        img_rgb = np.array(img)
        boxes, _ = self.detector.detect(img_rgb)
        return boxes is not None and len(boxes) > 0

    def process_person_images(self, person_name):
        person_folder = os.path.join(self.dataset_dir, person_name)
        images = [f for f in os.listdir(person_folder) if f.endswith(".jpg")]

        for image_filename in images:
            image_path = os.path.join(person_folder, image_filename)
            face = self.detect_and_crop_face(image_path)

            if face is not None:
                base_filename = image_filename.split(".")[0]
                self.augment_and_save(face, person_name, base_filename)

    def delete_images_without_faces(self):
        for person_name in os.listdir(self.output_dir):
            person_folder = os.path.join(self.output_dir, person_name)
            if os.path.isdir(person_folder):
                for img_name in os.listdir(person_folder):
                    img_path = os.path.join(person_folder, img_name)
                    try:
                        img = Image.open(img_path).convert("RGB")
                        faces, _ = self.detector(img, return_prob=True)
                        if faces is None or len(faces) == 0:
                            print(f"Deleting {img_path} - No face detected.")
                            os.remove(img_path)
                    except Exception as e:
                        print(f"Error processing {img_path}: {e}")
        print("Deletion complete.")

    def process_all(self):
        print(f"Using device: {self.device}")

        for person_name in os.listdir(self.dataset_dir):
            person_folder = os.path.join(self.dataset_dir, person_name)
            if os.path.isdir(person_folder):
                print(f"Processing {person_name}")
                self.process_person_images(person_name)
                self.save_profile(person_name)

        self.delete_images_without_faces()
        print("Augmentation complete.")


if __name__ == "__main__":
    dataset_dir = "D:/Project/StudentManagement/scripts/Images"
    output_dir = "D:/Project/StudentManagement/scripts/Images/Augmented_Images/"

    processor = FaceProcessor(dataset_dir, output_dir)
    processor.process_all()
