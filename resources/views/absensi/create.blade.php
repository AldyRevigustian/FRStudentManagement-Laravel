<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Menghidupkan Mesin') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <form action="{{ route('absensi.store') }}" method="POST" style="display:inline;">
                        @csrf

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
                            <label for="matakuliah_id"
                                class="block text-sm font-medium text-gray-700 dark:text-gray-200">Kelas</label>
                            <select name="matakuliah_id" id="matakuliah_id"
                                class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300"
                                required>
                                @foreach ($matakuliah as $matakuliahItem)
                                    <option value="{{ $matakuliahItem->id }}">{{ $matakuliahItem->nama }}</option>
                                @endforeach
                            </select>
                        </div>

                        <button type="submit"
                            class="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black text-sm font-semibold rounded-md focus:outline-none mb-4">
                            Hidupkan Mesin
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>
