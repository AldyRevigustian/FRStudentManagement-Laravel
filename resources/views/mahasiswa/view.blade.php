<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Show Mahasiswa') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <div class="mb-6">
                        <label for="nim"
                            class="block text-sm font-medium text-gray-700 dark:text-gray-200">NIM</label>
                        <input type="text" name="nim" id="nim" readonly
                            class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                            value="{{ old('nim', $mahasiswa->id) }}" required>
                    </div>
                    <div class="mb-6">
                        <label for="nama"
                            class="block text-sm font-medium text-gray-700 dark:text-gray-200">Nama</label>
                        <input type="text" name="nama" id="nama" readonly
                            class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                            value="{{ old('nama', $mahasiswa->nama) }}" required>
                    </div>

                    <div class="mb-6">
                        <label for="kelas_id"
                            class="block text-sm font-medium text-gray-700 dark:text-gray-200">Kelas</label>
                        <input type="text" name="kelas" id="kelas" readonly
                            class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                            value="{{ $mahasiswa->kelas->nama }}" required>
                    </div>

                    <div id="photo-container" class="grid grid-cols-5 gap-2 mt-4"></div>

                    <form action="{{ route('mahasiswa.destroy', $mahasiswa->id) }}" method="POST"
                        style="display:inline;">
                        @csrf
                        @method('DELETE')
                        <div class="flex justify-center mt-4">
                            <button type="submit"
                                class="inline-flex items-center px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold rounded-md focus:outline-none">
                                Delete Mahasiswa
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        const photoContainer = document.getElementById('photo-container');
        const deleteAllBtn = document.getElementById('delete-all-btn');
        const idMahasiswa = "{{ $mahasiswa->id }}";
        const basePath = `/images/${idMahasiswa}/`;
        const files = ['0.jpg', '1.jpg', '2.jpg', '3.jpg', '4.jpg'];

        let hasImages = false;

        files.forEach(file => {
            const imgPath = `${basePath}${file}`;

            const img = document.createElement('img');
            img.src = imgPath;
            img.alt = file;
            img.className = 'w-full h-auto rounded-md shadow';

            img.onload = () => {
                hasImages = true;
                deleteAllBtn.classList.remove('hidden');
            };

            img.onerror = () => {
                img.style.display = 'none';
            };

            photoContainer.appendChild(img);
        });
    </script>
</x-app-layout>
