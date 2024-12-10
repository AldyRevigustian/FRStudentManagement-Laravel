<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Daftar Mahasiswa') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <a href="{{ route('mahasiswa.create') }}"
                        class="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black text-sm font-semibold rounded-md focus:outline-none mb-4">
                        Tambah Mahasiswa
                    </a>

                    @if (session('success'))
                        <div class="mb-4 p-4 bg-green-100 text-green-700 border border-green-300 rounded-lg">
                            <strong class="font-medium">Success!</strong> {{ session('success') }}
                        </div>
                    @endif

                    <table id="mahasiswaTable" class="stripe w-full">
                        <thead>
                            <tr>
                                <th class="w-2">NIM</th>
                                <th>Nama</th>
                                <th>Kelas</th>
                                <th class="w-1/6">Aksi</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($mahasiswas as $mahasiswa)
                                <tr>
                                    <td>{{ $mahasiswa->id }}</td>
                                    <td>{{ $mahasiswa->nama }}</td>
                                    <td>{{ $mahasiswa->kelas->nama }}</td>
                                    <td class="flex space-x-2">
                                        <!-- Edit Button -->
                                        <a href="{{ route('mahasiswa.edit', $mahasiswa->id) }}"
                                            class="inline-flex items-center px-3 py-1.5 bg-yellow-600 text-white text-xs font-semibold rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2">
                                            Edit
                                        </a>

                                        <!-- Delete Button -->
                                        <form action="{{ route('mahasiswa.destroy', $mahasiswa->id) }}" method="POST"
                                            style="display:inline;">
                                            @csrf
                                            @method('DELETE')
                                            <button type="submit"
                                                class="inline-flex items-center px-3 py-1.5 bg-red-600 text-white text-xs font-semibold rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2">
                                                Hapus
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    @push('scripts')
        <script>
            $(document).ready(function() {
                $('#mahasiswaTable').DataTable({
                    "processing": true,
                    "serverSide": false,
                    "paging": true,
                    "searching": true,
                    "ordering": true
                });
            });
        </script>
    @endpush
</x-app-layout>
