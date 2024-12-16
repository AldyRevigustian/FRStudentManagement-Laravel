import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from PIL import Image
import joblib


class FaceDataset(Dataset):
    def __init__(self, root_dir, mtcnn, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.mtcnn = mtcnn
        self.image_paths = []
        self.labels = []
        self.label_encoder = LabelEncoder()

        self._load_dataset()

    def _load_dataset(self):
        """Load dataset and encode labels"""
        for person_name in os.listdir(self.root_dir):
            person_folder = os.path.join(self.root_dir, person_name)
            if os.path.isdir(person_folder):
                for img_name in os.listdir(person_folder):
                    img_path = os.path.join(person_folder, img_name)
                    self.image_paths.append(img_path)
                    self.labels.append(person_name)

        self.labels = self.label_encoder.fit_transform(self.labels)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Error opening image {img_path}: {e}")
            return None, None

        if self.transform:
            img = self.transform(img)

        faces, probs = self.mtcnn(img, return_prob=True)

        if faces is not None and len(faces) > 0:
            face = faces[0]
            return face, label
        else:
            print(f"No face detected in image {img_path}")
            return None, None


class FaceRecognitionTrainer:
    def __init__(self, dataset_path, model_save_path):
        self.dataset_path = dataset_path
        self.model_save_path = model_save_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.inception_resnet = (
            InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        )

        self.face_embeddings = []
        self.labels = []
        self.failed_images = []
        self.known_face_embeddings = []

        print(f"Using device: {self.device}")

    def _create_data_loader(self, batch_size=32):
        dataset = FaceDataset(self.dataset_path, self.mtcnn)
        return DataLoader(dataset, batch_size=batch_size, shuffle=True), dataset

    def _process_batch(self, faces, label):
        if faces is not None:
            try:
                faces = faces.to(self.device)
                embeddings = self.inception_resnet(faces)
                self.face_embeddings.append(embeddings.detach().cpu().numpy())
                self.known_face_embeddings.append(
                    self.inception_resnet(faces[0].unsqueeze(0).to(self.device))
                    .detach()
                    .cpu()
                    .numpy()
                )
                self.labels.append(label.cpu().numpy())
            except Exception as e:
                print(f"Error processing batch: {e}")
                return False
            return True
        else:
            self.failed_images.append(label)
            return False

    def _prepare_data(self):
        if not self.face_embeddings or not self.labels:
            print("No data available for training. Please check your dataset.")
            return None, None

        known_face_embeddings = np.vstack(self.known_face_embeddings)
        face_embeddings = (
            np.vstack(self.face_embeddings) if self.face_embeddings else np.array([])
        )
        labels = np.concatenate(self.labels) if self.labels else np.array([])

        return face_embeddings, labels

    def _save_models(self, svm_model, label_encoder):
        os.makedirs(self.model_save_path, exist_ok=True)

        np.save(
            os.path.join(self.model_save_path, "label_encoder_classes.npy"),
            label_encoder.classes_,
        )

        np.save(
            os.path.join(self.model_save_path, "known_face_embeddings.npy"),
            np.vstack(self.known_face_embeddings),
        )

        joblib.dump(svm_model, os.path.join(self.model_save_path, "svm_model.pkl"))

        print("Models and encodings saved successfully.")

    def train(self, batch_size=32):
        dataloader, dataset = self._create_data_loader(batch_size)

        for faces, label in dataloader:
            self._process_batch(faces, label)

        face_embeddings, labels = self._prepare_data()
        if face_embeddings is None:
            return False

        svm_model = SVC(kernel="linear", probability=True)
        svm_model.fit(face_embeddings, labels)

        self._save_models(svm_model, dataset.label_encoder)

        return True


if __name__ == "__main__":
    dataset_path = "D:/Project/StudentManagement/scripts/Images/Augmented_Images/"
    model_save_path = "D:/Project/StudentManagement/scripts/Model/"

    trainer = FaceRecognitionTrainer(dataset_path, model_save_path)
    if trainer.train():
        print("Training completed successfully.")
    else:
        print("Training failed. Please check the error messages above.")
