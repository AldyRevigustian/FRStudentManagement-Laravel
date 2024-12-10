<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Tambah Matakuliah') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <form action="{{ route('matakuliah.store') }}" method="POST">
                        @csrf

                        <div class="mb-6">
                            <label for="nama" class="block text-sm font-medium text-gray-700 dark:text-gray-200">Nama
                                Matakuliah</label>
                            <input type="text" name="nama" id="nama"
                                class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                                required>
                        </div>

                        <button type="submit"
                            class="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black text-sm font-semibold rounded-md focus:outline-none mb-4">
                            Simpan
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>
