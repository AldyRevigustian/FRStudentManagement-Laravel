<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
            {{ __('Daftar Absensi') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900 dark:text-gray-100">
                    <a href="{{ route('absensi.create') }}"
                        class="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-black text-sm font-semibold rounded-md focus:outline-none mb-4">
                        Hidupkan Mesin
                    </a>

                    @if (session('success'))
                        <div class="mb-4 p-4 bg-green-100 text-green-700 border border-green-300 rounded-lg">
                            <strong class="font-medium">Success!</strong> {{ session('success') }}
                        </div>
                    @endif

                    <!-- Absensi Table -->
                    <table id="absensiTable" class="stripe w-full">
                        <thead>
                            <tr>
                                <th class="w-2">ID Mahasiswa</th>
                                <th>Nama Mahasiswa</th>
                                <th class="w-1/12">Kelas</th>
                                <th class="w-1/5">Mata Kuliah</th>
                                <th class="w-1/6">Tanggal</th>
                                <th class="w-1/12">Aksi</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($absensis as $absensi)
                                <tr>
                                    <td>{{ $absensi->mahasiswa->id }}</td>
                                    <td>{{ $absensi->mahasiswa->nama }}</td>
                                    <td>{{ $absensi->kelas->nama }}</td>
                                    <td>{{ $absensi->mataKuliah->nama }}</td>
                                    <td>{{ $absensi->tanggal }}</td>
                                    <td class="flex space-x-2">
                                        <form action="{{ route('absensi.destroy', $absensi->id) }}" method="POST"
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
                $('#absensiTable').DataTable({
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
