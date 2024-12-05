<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Tambah Mahasiswa') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <form action="{{ route('mahasiswa.store') }}" method="POST">
                        @csrf

                        <div class="mb-6">
                            <label for="nim"
                                class="block text-sm font-medium text-gray-700 dark:text-gray-200">NIM</label>
                            <input type="text" name="nim" id="nim"
                                class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                                required>
                        </div>

                        <div class="mb-6">
                            <label for="nama"
                                class="block text-sm font-medium text-gray-700 dark:text-gray-200">Nama</label>
                            <input type="text" name="nama" id="nama"
                                class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                                required>
                        </div>

                        <div class="mb-6">
                            <label for="kelas_id"
                                class="block text-sm font-medium text-gray-700 dark:text-gray-200">Kelas</label>
                            <select name="kelas_id" id="kelas_id"
                                class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                                required>
                                @foreach ($kelas as $kelasItem)
                                    <option value="{{ $kelasItem->id }}">{{ $kelasItem->nama }}</option>
                                @endforeach
                            </select>
                        </div>

                        <div class="mb-6">
                            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Ambil Foto</label>
                            <div class="flex justify-center">
                                <video id="video" autoplay playsinline
                                    class="w-full h-60 bg-gray-800 rounded-md mb-4"></video>
                            </div>
                            <div class="flex justify-center">
                                <button type="button" id="capture"
                                    class="inline-flex items-center px-6 py-2 bg-green-600 text-white text-sm font-semibold rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
                                    Capture Foto
                                </button>
                            </div>
                            <div id="photo-container" class="grid grid-cols-5 gap-2 mt-4"></div>
                            <div class="flex justify-center mt-4">
                                <button type="button" id="verify"
                                    class="hidden inline-flex items-center px-6 py-2 bg-yellow-600 text-white text-sm font-semibold rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50">
                                    Verifikasi
                                </button>
                            </div>
                        </div>

                        <button type="submit" id="submit" disabled
                            class="inline-flex items-center px-6 py-2 bg-blue-600 text-white text-sm font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50">
                            Simpan
                        </button>

                        <input type="hidden" name="photos[]" id="photo1">
                        <input type="hidden" name="photos[]" id="photo2">
                        <input type="hidden" name="photos[]" id="photo3">
                        <input type="hidden" name="photos[]" id="photo4">
                        <input type="hidden" name="photos[]" id="photo5">
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('video');
        const captureButton = document.getElementById('capture');
        const verifyButton = document.getElementById('verify');
        const photoContainer = document.getElementById('photo-container');
        const photoInputs = [
            document.getElementById('photo1'),
            document.getElementById('photo2'),
            document.getElementById('photo3'),
            document.getElementById('photo4'),
            document.getElementById('photo5'),
        ];

        navigator.mediaDevices.getUserMedia({
                video: true
            })
            .then((stream) => {
                video.srcObject = stream;
            })
            .catch((err) => {
                console.error("Error akses kamera:", err);
            });

        let photoCount = 0;

        captureButton.addEventListener('click', () => {
            if (photoCount >= 5) {
                alert('Anda hanya dapat mengambil 5 foto.');
                return;
            }

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const photoData = canvas.toDataURL('image/png');

            const img = document.createElement('img');
            img.src = photoData;
            img.className = 'w-full h-full object-cover rounded-md';
            photoContainer.appendChild(img);

            photoInputs[photoCount].value = photoData;

            photoCount++;

            if (photoCount === 5) {
                verifyButton.classList.remove('hidden');
            }
        });

        verifyButton.addEventListener('click', async () => {
            const photos = photoInputs.map(input => input.value);

            if (photos.length !== 5) {
                alert("Harap ambil 5 foto sebelum memverifikasi.");
                return;
            }

            verifyButton.setAttribute('disabled', 'true');
            verifyButton.textContent = "Memverifikasi...";

            try {
                const response = await fetch('{{ route('mahasiswa.verify') }}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': '{{ csrf_token() }}'
                    },
                    body: JSON.stringify({
                        photos
                    })
                });

                const result = await response.json();

                if (result.success) {
                    alert("Semua foto berhasil diverifikasi!");

                    document.getElementById('submit').disabled = false;
                } else {
                    alert("Beberapa foto tidak memiliki wajah. Periksa foto berikut:\n" +
                        result.details.map((valid, index) =>
                            `Foto ${index + 1}: ${valid ? 'Valid' : 'Tidak Valid'}`).join("\n"));
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Terjadi kesalahan saat memverifikasi foto.");
            } finally {
                verifyButton.setAttribute('disabled', 'false');
                verifyButton.textContent = "Verifikasi";
            }
        });
    </script>
</x-app-layout>
